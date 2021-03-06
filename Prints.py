from __future__ import annotations
from typing import Dict, List

from matplotlib import pyplot as plt

from globals import Person, Factory, GoodsMarket, SharesMarket, WorkersMarket

def printPersonsAndFactories(all_persons: List[Person], all_factories: List[Factory], day: int = 0, f: TextIO = None):
    f.write("\n\n")
    f.write("\n\n")
    f.write("\t"*3 + "day:{:<20d}".format(day) + "\n")
    f.write("\n\n")
    f.write("\n\n")
    f.write("PERSONS\n")
    f.write("{0:<25s} - {1:<10s} - {2:<4s} - {3:<6s} - {4:<6s} \n".format("Name", "Capital", "Employed", "Ess_sat", "Lux_sat"))
    f.write("-"*50 + "\n")
    for person in sorted(all_persons, key=lambda p: p.name):
        employed = "None"
        if(person.employer is not None):
            employed = str(person.employer.fact_id)
        f.write("{0:<25s} - {1:>10.2f}$ - {2:<4s} - {3:>5.0f}% - {4:>5.0f}% \n".format(
            person.name, person.capital, employed, person.essential_satisfaction*100, person.luxury_satisfaction*100))
    f.write("\n")
    f.write("-FACTORIES-\n")
    f.write("{0:<3s} - {1:<6s} - {2:<4s} - {3:>10s}  - {4:>7s} - {5:>7s} - {6:>5s} - {7:>2s} - {8:>4s} \n".format(
        "ID", "Essen", "Wok.", "Salary", "left_stk", "new_stk", "price", "profit", "share_val"))
    f.write("-"*80 + "\n")
    for factory in sorted(all_factories, key=lambda f: f.fact_id):
        f.write("{0:<3d} - {1:<6s} - {2:<4d} - {3:>10.2f}$ - {4:>7.2f} - {5:>7.2f} - {6:>5.2f} - {7:>2.0f}% - {8:<4.2f}$ \n".format(
            factory.fact_id, str(factory.product_is_essential), len(factory.workers), factory.salary, factory.avaliable_stock,
            factory.new_stock, factory.product_price, factory.profit_margin_per_product * 100, SharesMarket.share_value(1, factory)))
    f.write("\n\n")


def plotStates(state: List[List[float]], axes: plt = None):
    days: List[int] = []
    vals_n: int = len(state[0])
    vals: List[List[float]] = []
    for i in range(vals_n):
        vals.append([])
    for i in range(len(state)):
        days.append(i)
        for j in range(len(state[i])):
            vals[j].append(state[i][j])

    for i in range(0,vals_n):
        plt.subplot(vals_n, 1,i+1)
        plt.plot(days, vals[i])
        if(i != vals_n):
            ax = plt.gca()
            ax.get_xaxis().set_visible(False) #hide x axis
    plt.subplot(vals_n,1,1)
    plt.title('(top50 - bottom50)/total')
    plt.ylabel('Inequality')
    plt.subplot(vals_n, 1,2)
    plt.title('Production')
    plt.ylabel('total stock')
    plt.subplot(vals_n, 1,3)
    plt.title('Essential satisfaction')
    plt.ylabel('essential/person')
#    plt.subplot(vals_n, 1,4)
#    plt.title('Luxury satisfaction')
#    plt.ylabel('luxury/person')
#    plt.xlabel('cycle')
    return plt
