import sys
import os
from coopr.pyomo import *
from coopr.opt import SolverFactory
import coopr.environ

from numbers import Integral
import datetime

class FourhundredException(Exception):
    def __init__(self, msg):
        self.msg = msg

class Trade:
    def __init__(self, number, price, year, month, day):
        if not (isinstance(number, Integral) and isinstance(price, Integral)):
            raise TypeError()
        if number < 1 or price < 1:
            raise ValueError()
        self.number = number
        self.price = price
        self.date = datetime.date(year, month, day)

def validate_buysell(buysellstr, input_list):
    ret = []
    try:
        for entry in input_list:
            if not isinstance(entry, dict):
                raise TypeError()
            ret.append(Trade(entry.get('number'), entry.get('price'),
                entry.get('year'), entry.get('month'), entry.get('day')))
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
    profits = list((p,s,sales[s].price - purchases[p].price)
                for p in range(len(purchases)) for s in range(len(sales)))

    model.pairings = Set(within=model.purchases * model.sales,
            initialize=list((p+1,s+1) for (p,s,f) in profits if f > 0))

    # profit associated with each pairing
    model.profits = Param(model.pairings, domain=PositiveIntegers,
            initialize=dict(((p+1,s+1),f) for (p,s,f) in profits if f > 0))

    # output counts of each pairing
    model.selected = Var(model.pairings, domain=NonNegativeIntegers)

    def obj_rule(model):
        return summation(model.profits, model.selected)

    model.obj = Objective(rule=obj_rule, sense=maximize)

    def purchase_limit(model, t):
        used = sum(model.selected[t, s] for s in model.sales
                                        if (t,s) in model.pairings)
        return used <= model.purchase_count[t]

    def sale_limit(model, t):
        used = sum(model.selected[p, t] for p in model.purchases
                                        if (p,t) in model.pairings)
        return used <= model.sale_count[t]

    model.purchase_constraint = Constraint(model.purchases, rule=purchase_limit)
    model.sale_constraint = Constraint(model.sales, rule=sale_limit)

    model.preprocess()

    return model

def run_problem(purchases, sales):
    opt = SolverFactory('glpk')

    model = make_model(purchases,sales)

    results = opt.solve(model)

    #raise Exception(str(results))

    output = []
    solutions = results.get('Solution', [])
    if len(solutions) > 0:
        model.load(results)
        for (p,s) in model.pairings:
            ct = model.selected[p,s].value
            if ct > 0:
                output.append((purchases[p-1], sales[s-1], ct))
    return dict(pairs=output, result=results.json_repn())

if __name__ == "__main__":
    # the reloader would be nice but it doesn't work with subprocesses,
    # which opt.solve uses
    app.run(debug=True, host='192.168.56.101', use_reloader=False)
