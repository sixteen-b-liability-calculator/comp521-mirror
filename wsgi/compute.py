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

def introduces_liability(buy, sell, anniversary_days_back):
    profitable = sell.price > buy.price

    earlier_date = min(sell.date, buy.date)
    later_date = max(sell.date, buy.date)

    # the date algorithm is as follows:
    # 1. find a "hypothetical anniversary" tuple of the earlier_date, e.g.:
    #    date(2001,08,31) -> (2001,14,31)
    #    date(2001,07,01) -> (2001,13,01)
    # 2. adjust the day of that tuple according to anniversary_days_back, e.g.:
    #    (2001,14,31), 1 days back -> (2001,14,30)
    #    (2001,13,01), 0 days back -> (2001,13,01)
    #    (2001,13,01), 1 days back -> (2001,13,-0)
    #    (2001,13,01), 2 days back -> (2001,13,-1)
    # 3. if days is non-positive, decrement month; now non-positive days -N (N
    #    may be zero) represent days really in the given month
    #    NB we can't end up with month 0 like this since we only have months 7
    #    and greater after step 1
    #    (2001,13,-0) -> (2001,12,-0)
    #    (2001,13,-1) -> (2001,12,-1)
    # 4. fixup the month/year without respect to the day
    #    (2001,14,30) -> (2002,02,30)
    #    (2001,13,01) -> (2002,01,01)
    #    (2001,12,-0) -> (2001,12,-0)
    #    (2001,12,-1) -> (2001,12,-1)
    # 5. determine "first invalid day" based on tuple by pushing past-last-day
    #    tuples to the first day of the next month; mapping non-positive day
    #    values -N (N may be 0), to the day N days before the last day of the
    #    month; and mapping valid dates to themselves
    #    (2002,02,30) -> date(2002,03,01)
    #    (2002,01,01) -> date(2002,01,01)
    #    (2001,12,-0) -> date(2001,12,31)
    #    (2001,12,-1) -> date(2001,12,30)
    # 6. the later_date makes a valid trade iff it falls /before/ the "first
    #    invalid day"

    def month_fixup(und):
        if und[1] > 12:
            und[1] -= 12
            und[0] += 1

    # steps 1 and 2
    undate = [earlier_date.year, earlier_date.month + 6, earlier_date.day - anniversary_days_back]
    # step 3
    if undate[2] < 1:
        undate[1] -= 1
    # step 4
    month_fixup(undate)
    # determine the number of days in the real month; this is where step 2 came
    # in handy to simplify matters since undate[1] is always the one
    # we need to know
    if undate[1] == 2:
        # find the day of the day before march 1
        days_in_month = (datetime.date(undate[0], 3, 1) - datetime.timedelta(days=1)).day
    elif undate[1] in [1, 3, 5, 7, 8, 10, 12]:
        days_in_month = 31
    else:
        days_in_month = 30
    # step 5
    if undate[2] < 1: # non-positive values:
        undate[2] += days_in_month
    elif undate[2] > days_in_month:
        undate[2] -= days_in_month
        undate[1] += 1
        month_fixup(undate)
    first_invalid_date = datetime.date(*undate)

    sixmonth = later_date < first_invalid_date

    return profitable and sixmonth

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

def make_model(purchases, sales):
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
                if introduces_liability(purchases[p], sales[s], 0))

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

def run_problem(purchases, sales):
    opt = SolverFactory('glpk')

    model = make_model(purchases,sales)

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

def run_greedy(purchases, sales):
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
            if amt > 0 and s_amt > 0 and introduces_liability(p, s, 0):
                if amt >= s_amt:
                    s_sales_amts[i] = 0
                    amt -= s_amt
                    collect(p,s,s_amt)
                else:
                    s_sales_amts[i] -= amt
                    collect(p,s,amt)
                    amt = 0

    return ret
