import sys
import os
from coopr.pyomo import *
from coopr.opt import SolverFactory, SolverStatus, TerminationCondition
import coopr.environ

from numbers import Integral
import datetime

class FourhundredException(Exception):
    def __init__(self, msg):
        self.msg = msg

class Trade:
    def __init__(self, number=None, price=None, year=None, month=None, day=None, **extra):
        if not (isinstance(number, Integral) and isinstance(price, Integral)):
            raise TypeError()
        if number < 1 or price < 1:
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

    # purchases
    model.purchases = RangeSet(len(purchases))
    purchase_counts = ((p+1,purchases[p].number) for p in range(len(purchases)))
    model.purchase_count = Param(model.purchases,
            initialize=dict(purchase_counts), domain=PositiveIntegers)

    # sales
    model.sales = RangeSet(len(sales))
    sale_counts = ((p+1,sales[p].number) for p in range(len(sales)))
    model.sale_count = Param(model.sales,
            initialize=dict(sale_counts), domain=PositiveIntegers)

    # profitable pairings
    profits = list((p,s)
                for p in range(len(purchases)) for s in range(len(sales))
                if introduces_liability(purchases[p], sales[s], stella_correction, jammies_correction))

    model.pairings = Set(within=model.purchases * model.sales,
            initialize=list((p+1,s+1) for (p,s) in profits))

    # profit associated with each pairing
    model.profits = Param(model.pairings, domain=PositiveIntegers,
            initialize=dict(((p+1,s+1),sales[s].price - purchases[p].price)
                            for (p,s) in profits))

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

    model.preprocess()

    return model

def run_problem(purchases, sales, stella_correction, jammies_correction):
    opt = SolverFactory('glpk')

    model = make_model(purchases,sales,stella_correction,jammies_correction)

    results = opt.solve(model)

    output = []
    solutions = results.get('Solution', [])
    if len(solutions) > 0:
        model.load(results)
        for (p,s) in model.pairings:
            ct = model.selected[p,s].value
            if ct > 0:
                output.append((purchases[p-1], sales[s-1], ct))


    ret = dict(pairs=output, full_result=results.json_repn())


    if results.solver.status == SolverStatus.ok:
        if results.solver.termination_condition == TerminationCondition.optimal:
            ret['status'] = "optimal"
            # the following procedure for getting the value is right from
            # the coopr source itself...
            key = results.solution.objective.keys()[0]
            ret['value'] = results.solution.objective[key].value
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
