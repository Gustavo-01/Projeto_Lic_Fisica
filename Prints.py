from typing import List
from Classes import Factory, Person


def printPersonsAndFactories(all_persons: List[Person],all_factories: List[Factory]):
    print("PERSONS")
    print("{0:<20} - {1:<4} - {2:<10}".format("Name","Capital","Employed"))
    print("-"*45)
    for person in sorted(all_persons, key=lambda p: p.name):
        employed = "not employed"
        if(person.employer != None):
            employed = "employed by "+str(person.employer.id)
        if(person.owned_factories != None):
            employed = "Owns factory: " + str(person.owned_factories.fact_id)
        print("{0:<20} - {1:<4} - {2:<10}".format(person.name,str(person.capital),employed))
    print("")
    print("-FACTORIES-")
    print("{3:<2} {0:<20} - {1:<9} - {2:<10}".format("Owner_Name","N_Workers","Essencial","ID"))
    print("-"*50)
    for factory in sorted(all_factories, key=lambda f: len(f.workers)):
        print("{3:<2} {0:<20} - {1:<9} - {2:<10}".format(factory.owner.name,str(len(factory.workers)),str(factory.product_is_essential),factory.fact_id))

