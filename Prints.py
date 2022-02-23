from __future__ import annotations
from typing import List
from globals import *


def printPersonsAndFactories(all_persons: List[Person],all_factories: List[Factory],day :int = 0):
    print(" "*30 + "day:{:<20d}".format(day))
    print("PERSONS")
    print("{0:<25s} - {1:<10s} - {2:<10s}".format("Name","Capital","Employed"))
    print("-"*50)
    for person in sorted(all_persons, key=lambda p: p.name):
        employed = "not employed"
        if(person.employer != None):
            employed = "employed by "+str(person.employer.__fact_id__)
        if(len(person.owned_factories) > 0):
            employed += " -- Owns factory: " + str(person.owned_factories[0].__fact_id__)
        print("{0:<25s} - {1:>10.3f}$ - {2:<10s}".format(person.name,person.capital,employed))
    print("")
    print("-FACTORIES-")
    print("{0:<3s} - {1:<6s} - {2:<8s} - {3:<10s}  - {4:<25s} - {5:>7s} ".format("ID","Essencial","N_Works.","Salary","Owner_Name","owned%"))
    print("-"*80)
    for factory in sorted(all_factories, key=lambda f: f.__fact_id__):
        owner = sorted(list(factory.share_holders.keys()),key=factory.share_holders.get)[0]
        print("{0:<3d} - {1:<6s} - {2:<8d} - {3:>10.3f}$ - {4:<25s} - {5:>7.3f}%".format(factory.__fact_id__,str(factory.product_is_essential),len(factory.workers),factory.salary,owner.name,factory.share_holders[owner]*100))

