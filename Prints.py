from __future__ import annotations
from typing import List
from globals import *


def printPersonsAndFactories(all_persons: List[Person],all_factories: List[Factory],day :int = 0):
    print(" "*30 + "day:{:<20d}".format(day))
    print("PERSONS")
    print("{0:<20} - {1:<4} - {2:<10}".format("Name","Capital","Employed"))
    print("-"*45)
    for person in sorted(all_persons, key=lambda p: p.name):
        employed = "not employed"
        if(person.employer != None):
            employed = "employed by "+str(person.employer.fact_id)
        if(len(person.owned_factories) > 0):
            employed += " -- Owns factory: " + str(person.owned_factories[0].fact_id)
        print("{0:<20} - {1:<4} - {2:<10}".format(person.name,str(person.capital),employed))
    print("")
    print("-FACTORIES-")
    print("{3:<2} {0:<20} - {1:<9} - {2:<10} - {4:<10}".format("Owner_Name","N_Workers","Essencial","ID","Salary"))
    print("-"*50)
    for factory in sorted(all_factories, key=lambda f: f.fact_id):
        print("{3:<2} {0:<20} - {1:<9} - {2:<10} - {4:<10}".format(list(factory.share_holders.keys())[0].name,str(len(factory.workers)),str(factory.product_is_essential),factory.fact_id,str(factory.salary) + "$"))

