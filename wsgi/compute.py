import sys
import os
# from __future__ import division
from pyomo import *
from pyomo.opt import SolverFactory, SolverStatus, TerminationCondition
from pyomo.environ import *

from numbers import Number
import datetime

import itertools

#for python vizualizations 
#{
#import datetime <-- Already Have
#from flask import Flask, render_template
#import tempfile

import matplotlib
import matplotlib.pyplot as plt
from pylab import *
#matplotlib.use('Agg') # this allows 'png' plotting 
from matplotlib.dates import MonthLocator, WeekdayLocator, DateFormatter, YearLocator
#} 
#end for python vizualizations

from aux_code.httpExceptions import *

class Trade:
    def __init__(self, number=None, price=None, year=None, month=None, day=None, **extra):
        if not (isinstance(number, Number) and isinstance(price, Number)):
            raise TypeError()
        if number <= 0 or price < 0:
            raise ValueError()
        self.number = number
        self.price = price
        self.date = datetime.date(year, month, day)
	self.extra = extra
    def recreate_dict(self):
        return dict(number=self.number, price=self.price, year=self.date.year,
                month=self.date.month, day=self.date.day, **self.extra)

def dates_within_range(buy, sell, stella_correction, jammies_correction):
    earlier_date = min(sell.date, buy.date)
    later_date = max(sell.date, buy.date)

    # the date algorithm is as follows:
    # 1. find a "hypothetical anniversary" tuple of the earlier_date, e.g.:
    #    date(2001,08,31) -> (2001,14,31)
    #    date(2001,07,01) -> (2001,13,01)
    # 2. end-of-month adjustment.
    #    Increment the month and set day to 1 to make a real date object
    #    Decrement this by a day; now we have the end of the month.
    #    Iff date is larger than this, then:
    #    if Jammies is ON: use the last-day date
    #    if Jammies is OFF: use the first-day date
    # 3. stella adjustment, iff stella is ON: take the previous real day
    # this yields the first day on which the trade could not be paired

    def first_day_of_next_month(und):
        if und[1] > 11:
            return datetime.date(und[0] + 1, und[1] - 11, 1)
        else:
            return datetime.date(und[0], und[1] + 1, 1)
    def date_less_one(dat):
        return dat - datetime.timedelta(days=1)

    # step 1
    undate = [earlier_date.year, earlier_date.month + 6, earlier_date.day]
    # step 2
    first_day = first_day_of_next_month(undate)
    last_day = date_less_one(first_day)
    if undate[2] > last_day.day:
        if jammies_correction:
            real_anniversary = last_day
        else:
            real_anniversary = first_day
    else:
        real_anniversary = datetime.date(last_day.year, last_day.month, undate[2])
    # step 3
    if stella_correction:
        first_invalid_date = date_less_one(real_anniversary)
    else:
        first_invalid_date = real_anniversary

    return later_date < first_invalid_date

def introduces_liability(buy, sell, stella_correction, jammies_correction):
    return (sell.price > buy.price) and dates_within_range(buy, sell, stella_correction, jammies_correction)

def validate_buysell(buysellstr, input_list):
    ret = []
    try:
        for entry in input_list:
            if not isinstance(entry, dict):
                raise TypeError()
            ret.append(Trade(**entry))
        return ret
    except (ValueError, TypeError):
        raise FourhundredException("invalid '%s' entry" % buysellstr)

def make_model(purchases, sales, stella_correction, jammies_correction):
    model = ConcreteModel()

    number_corr = 1
    price_corr = 1
    for t in itertools.chain(purchases, sales):
        while int(number_corr * t.number) != number_corr * t.number:
            number_corr *= 10
        while int(price_corr * t.price) != price_corr * t.price:
            price_corr *= 10

    # purchases
    model.purchases = RangeSet(len(purchases))
    purchase_counts = ((p+1,int(number_corr * purchases[p].number)) for p in range(len(purchases)))
    model.purchase_count = Param(model.purchases,
            initialize=dict(purchase_counts), domain=PositiveIntegers)

    # sales
    model.sales = RangeSet(len(sales))
    sale_counts = ((p+1,int(number_corr * sales[p].number)) for p in range(len(sales)))
    model.sale_count = Param(model.sales,
            initialize=dict(sale_counts), domain=PositiveIntegers)

    # profitable pairings
    profits = list((p,s)
                for p in range(len(purchases)) for s in range(len(sales))
                if introduces_liability(purchases[p], sales[s], stella_correction, jammies_correction))

    model.pairings = Set(within=model.purchases * model.sales,
            initialize=list((p+1,s+1) for (p,s) in profits))

    profit_values = dict(((p+1,s+1),int(price_corr * sales[s].price) - int(price_corr * purchases[p].price))
                            for (p,s) in profits)
    # profit associated with each pairing
    model.profits = Param(model.pairings, domain=PositiveIntegers,
            initialize=profit_values)

    # output counts of each pairing
    model.selected = Var(model.pairings, domain=NonNegativeIntegers)

    def obj_rule(model):
        return summation(model.profits, model.selected)

    model.obj = Objective(rule=obj_rule, sense=maximize)

    def purchase_limit(model, t):
        pairings = list(model.selected[t, s] for s in model.sales
                                        if (t,s) in model.pairings)
        if pairings:
            used = sum(pairings)
            return used <= model.purchase_count[t]
        else:
            return Constraint.Feasible

    def sale_limit(model, t):
        pairings = list(model.selected[p, t] for p in model.purchases
                                        if (p,t) in model.pairings)
        if pairings:
            used = sum(pairings)
            return used <= model.sale_count[t]
        else:
            return Constraint.Feasible

    model.purchase_constraint = Constraint(model.purchases, rule=purchase_limit)
    model.sale_constraint = Constraint(model.sales, rule=sale_limit)

    # print "printing model: ", model.pprint()  # debug

    # model.pyomo_preprocess()   (pyomo 3.7)

    # # # # # # # # # # # # # dual model # # # # # # # # # # # # # #

    dual_model = ConcreteModel()

    # purchases
    dual_model.purchases = RangeSet(len(purchases))
    purchase_counts = ((p+1,int(number_corr * purchases[p].number)) for p in range(len(purchases)))
    dual_model.purchase_count = Param(dual_model.purchases,
            initialize=dict(purchase_counts), domain=PositiveIntegers)
    dual_model.purchase_dual = Var(dual_model.purchases, domain=NonNegativeIntegers)

    # sales
    dual_model.sales = RangeSet(len(sales))
    sale_counts = ((p+1,int(number_corr * sales[p].number)) for p in range(len(sales)))
    dual_model.sale_count = Param(dual_model.sales,
            initialize=dict(sale_counts), domain=PositiveIntegers)
    dual_model.sale_dual = Var(dual_model.sales, domain=NonNegativeIntegers)

    dual_model.pairings = Set(within=dual_model.purchases * dual_model.sales,
            initialize=list((p+1,s+1) for (p,s) in profits))

    dual_model.profits = Param(dual_model.pairings, domain=PositiveIntegers,
            initialize=profit_values)

    def profit_match(dual_model, p, s):
        return dual_model.sale_dual[s] + dual_model.purchase_dual[p] >= dual_model.profits[(p,s)]

    def dual_obj_rule(dual_model):
        return summation(dual_model.sale_count, dual_model.sale_dual) + summation(dual_model.purchase_count, dual_model.purchase_dual)

    dual_model.obj = Objective(rule=dual_obj_rule, sense=minimize)
    dual_model.profit_constraint = Constraint(dual_model.pairings, rule=profit_match)

    # dual_model.pyomo_preprocess()  (pyomo 3.7)

    return (number_corr, price_corr, model, dual_model)

def collect_dual(dual_model, number_corr, price_corr, ret, purchases, sales, opt, **ignore):

    #results = opt.solve(dual_model)   (pyomo 3.7)
    results = opt.solve(dual_model, load_solutions=False)
    dual_model.solutions.load_from(results)

    outputB = []
    outputS = []

    #solutions = results.get('Solution', [])  (pyomo 3.7)
    solutions = dual_model.solutions

    if len(solutions) > 0:
        # dual_model.load(results)   (pyomo 3.7)
        for p in dual_model.purchases:
            d = dual_model.purchase_dual[p].value
            outputB.append((purchases[p-1], float(d) / price_corr))
        for s in dual_model.sales:
            d = dual_model.sale_dual[s].value
            outputS.append((sales[s-1], float(d) / price_corr))

    ret['dual_solution'] = dict(buy=outputB, sell=outputS)
    ret['full_dual_result'] = results.json_repn()

    if results.solver.status == SolverStatus.ok:
        if results.solver.termination_condition == TerminationCondition.optimal:
            ret['dual_status'] = "optimal"
            # the following procedure is for getting the value
            key = results.solution.objective.keys()[0]
            ret['dual_value'] = float(results.solution.objective[key]['Value']) / price_corr / number_corr
        else:
            ret['dual_status'] = "not solved"
    else:
        ret['dual_status'] = "solver error"

def run_problem(purchases, sales, stella_correction, jammies_correction):
    opt = SolverFactory('glpk')
    
    (number_corr, price_corr, model, dual_model) = make_model(purchases,sales,stella_correction,jammies_correction)
    print number_corr, price_corr, model, dual_model
    # results = opt.solve(model)  (pyomo 3.7)
    results = opt.solve(model, load_solutions=False)
    model.solutions.load_from(results)

    output = []

    # solutions = results.get('Solution', [])  (pyomo 3.7)
    solutions = model.solutions
    print "solutions: ",solutions
    print "model.pairings: ", model.pairings
    if len(solutions) > 0:
        # model.load(results)   (pyomo 3.7)
        for (p,s) in model.pairings:
            ct = model.selected[p,s].value
            if ct > 0:
                output.append((purchases[p-1], sales[s-1], float(ct) / number_corr))


    ret = dict(pairs=output, full_result=results.json_repn())

    if results.solver.status == SolverStatus.ok:
        if results.solver.termination_condition == TerminationCondition.optimal:
            ret['status'] = "optimal"
            # the following procedure is for getting the value
            # let's do some error handling
            key = results.solution.objective.keys()[0]
            ret['value'] = float(results.solution.objective[key]['Value']) / price_corr / number_corr
            collect_dual(**locals())
        else:
            ret['status'] = "not solved"
    else:
        ret['status'] = "solver error"

    return ret

def run_greedy(purchases, sales, stella_correction, jammies_correction):
    s_purchases = sorted(purchases, key=lambda t: t.price)
    s_sales = sorted(sales, key=lambda t: -t.price)
    s_sales_amts = map(lambda s: s.number, s_sales)

    ret = dict(pairs = [], value = 0)

    def collect(p, s, amt):
        ret['pairs'].append((p,s,amt))
        ret['value'] += amt*(s.price-p.price)

    for p in s_purchases:
        amt = p.number
        for i in range(0, len(s_sales)):
            s = s_sales[i]
            s_amt = s_sales_amts[i]
            if amt > 0 and s_amt > 0 and introduces_liability(p, s, stella_correction, jammies_correction):
                if amt >= s_amt:
                    s_sales_amts[i] = 0
                    amt -= s_amt
                    collect(p,s,s_amt)
                else:
                    s_sales_amts[i] -= amt
                    collect(p,s,amt)
                    amt = 0

    return ret


