from __future__ import annotations
from typing import List, TextIO
from globals import *

def printPersonsAndFactories(all_persons: List[Person],all_factories: List[Factory],day :int = 0, f: TextIO = None):
    f.write("\t"*3 + "day:{:<20d}".format(day) + "\n")
    f.write("PERSONS\n")
    f.write("{0:<25s} - {1:<10s} - {2:<4s} - {3:<6s} - {4:<6s} \n".format("Name","Capital","Employed","Ess_sat","Lux_sat"))
    f.write("-"*50 + "\n")
    for person in sorted(all_persons, key=lambda p: p.name):
        employed = "None"
        if(person.employer != None):
            employed = str(person.employer.__fact_id__)
        f.write("{0:<25s} - {1:>10.2f}$ - {2:<4s} - {3:>5.0f}% - {4:>5.0f}% \n".format(
            person.name,person.capital,employed,person.essential_satisfaction*100,person.luxury_satisfaction*100))
    f.write("\n")
    f.write("-FACTORIES-\n")
    f.write("{0:<3s} - {1:<6s} - {2:<4s} - {3:>10s}  - {4:<7s} - {5:>7s} - {6:>7s} - {7:>5s} - {8:>2s} \n".format(
        "ID","Essen","Works.","Salary","ava_stk","stock","new_stk","price","profit"))
    f.write("-"*80 + "\n")
    for factory in sorted(all_factories, key=lambda f: f.__fact_id__):
        f.write("{0:<3d} - {1:<6s} - {2:<4d} - {3:>10.2f}$ - {4:<7.2f} - {5:>7.2f} - {6:>7.2f} - {7:>5.2f} - {8:>2.0f}% \n".format(
            factory.__fact_id__,str(factory.product_is_essential),len(factory.workers),factory.salary,factory.avaliable_stock,
            factory.stock,factory.new_stock,factory.product_price,factory.profit_margin_per_product * 100))
    f.write("\n\n")