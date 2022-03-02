from __future__ import annotations
from typing import List
from globals import *


def printPersonsAndFactories(all_persons: List[Person],all_factories: List[Factory],day :int = 0):
    print(" "*30 + "day:{:<20d}".format(day))
    print("PERSONS")
    print("{0:<25s} - {1:<10s} - {2:<4s} - {3:<6s} - {4:<6s}".format("Name","Capital","Employed","Ess_sat","Lux_sat"))
    print("-"*50)
    for person in sorted(all_persons, key=lambda p: p.name):
        employed = "None"
        if(person.employer != None):
            employed = str(person.employer.__fact_id__)
        print("{0:<25s} - {1:>10.2f}$ - {2:<4s} - {3:>5.0f}% - {4:>5.0f}%".format(person.name,person.capital,employed,person.essential_satisfaction*100,person.luxury_satisfaction*100))
    print("")
    print("-FACTORIES-")
    print("{0:<3s} - {1:<6s} - {2:<4s} - {3:>10s}  - {4:<7s} - {5:>7s} - {6:>7s} - {7:>5s} - {8:>2s}".format("ID","Essen","Works.","Salary","ava_stk","stock","new_stk","price","profit"))
    print("-"*80)
    for factory in sorted(all_factories, key=lambda f: f.__fact_id__):
        owner = sorted(list(factory.share_holders.keys()),key=factory.share_holders.get)[0]
        print("{0:<3d} - {1:<6s} - {2:<4d} - {3:>10.2f}$ - {4:<7.2f} - {5:>7.2f} - {6:>7.2f} - {7:>5.2f} - {8:>2.0f}%".format(factory.__fact_id__,str(factory.product_is_essential),len(factory.workers),factory.salary,factory.avaliable_stock,factory.stock,factory.new_stock,factory.product_price,factory.profit_margin_per_product * 100))
