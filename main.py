from __future__ import annotations
from typing import List

from numpy import true_divide
from globals import *
import Prints
import enum

class InitialConditions(enum.Enum):
    BOURGEOISIE = 1
    EGALITARIANISM = 2
    SOLE_OWNERSHIP = 3

def startSim(people_number :int = 20,factory_number :int = 50,max_capital :int = 1000,min_capital :int = 10, initial_condition: InitialConditions = InitialConditions.SOLE_OWNERSHIP, burgeoisie_percentage :int = 15):
    #--Resolve initial conditions--#
    if initial_condition == InitialConditions.EGALITARIANISM:
        initial_condition = InitialConditions.BOURGEOISIE
        burgeoisie_percentage = 100

    #--GENERATE PERSONS--#
    import random
    import GetRandomNames
    from MedianOneGenerator import medianOneGenerate , uniformGenerate
    from math import ceil
    #Generate random name for every person
    names = GetRandomNames.getRandomName(people_number)
    #Create person
    unemployed_people : List[Person] = []
    burgeoisie : List[Person] = []
    for i in range(0,people_number):
        person = Person(names[i], random.randint(min_capital, max_capital))
        unemployed_people.append(person)
        if i <= ceil(people_number * burgeoisie_percentage):
            burgeoisie.append(person)

    #--FACTORY CREATION--#
    def pickRandomPeople(ammount:int = 1, pool = Person.all_persons, repetition = True) -> List[Person]:
        if(len(pool) <= ammount):
            ammount = len(pool) - 1
        indexes = uniformGenerate(len(pool)-1,ammount,repetition = repetition)
        return [pool[i] for i in indexes]

    def findWorkers(ammount: int = 1):
        #Grab random unemployed
        workers = pickRandomPeople(ammount, unemployed_people, repetition = False)
        for worker in workers:
            unemployed_people.remove(worker)
        return workers

    #Workers
    number_workers_list = medianOneGenerate(people_number,factory_number,min_number = 1)
    number_shareholders_list = medianOneGenerate(people_number * burgeoisie_percentage/100,factory_number,min_number = 1)

    for i in range(factory_number):
        workers :List[Person] = findWorkers(number_workers_list[i])
        if len(workers) == 0:
            continue
        #Grab random people from first (person_count * burgeoisie_percentage) indices and distribute 100 over them
        share_holders :List[Person] = pickRandomPeople(number_shareholders_list[i], burgeoisie, repetition=False) #TODO ERROR! Returning same person twice!
        #Distribute ShareValues
        share_values = uniformGenerate(0,len(share_holders), int_return=False) #max_number = 0+1
        SUM = sum(share_values)
        share_values = [value/SUM for value in share_values]
        shares = {}
        for i in range(len(share_values)):
            shares[share_holders[i]] = share_values[i]
        #- TEST -
        if sum(share_values) > 1+FLOATING_POINT_ERROR_MARGIN or sum(share_values) < 1-FLOATING_POINT_ERROR_MARGIN:
            print(sum(share_values))
        #--------
        
        # - TEST -
        SUM = 0
        for p in shares:
            SUM += shares[p]
        if SUM > 1+FLOATING_POINT_ERROR_MARGIN or SUM < 1-FLOATING_POINT_ERROR_MARGIN:
            print(SUM)
        #---------

        #Create Factory
        Factory(bool(round(random.random())),workers,shares,random.random()*max_capital + min_capital)

startSim()

print("done starting sim")

def nextTimeStep():
    #CONSUMERS MARKET
    #-------------------------
    for factory in Factory.all_factories:
        factory.produce() #Pay salaries and produce new stock ammount
    GoodsMarket.runMarket()
    print("GoodsMarket done")
    #-------------------------

    #Salary Projection and fundraising
    #---------------------
    for factory in Factory.all_factories:
        projected_capital = factory.project_needed_capital() #Project needed capital
        factory.TEST_PROJECT_CAPITAL = projected_capital
        factory.getFunding(projected_capital) #Fundraise (set shares for sale or distribute capital)
    #---------------------

    #SHARES MARKET
    #---------------------
    SharesMarket.runMarket()
    print("sharesMarket done")
    #---------------------

    #WORKERS MARKET
    #----------------------
    WorkersMarket.runMarket()
    print("workersMarket done")
    #---------------------

Prints.printPersonsAndFactories(Person.all_persons,Factory.all_factories,0)
nextTimeStep()
Prints.printPersonsAndFactories(Person.all_persons,Factory.all_factories,1)
nextTimeStep()
Prints.printPersonsAndFactories(Person.all_persons,Factory.all_factories,2)
"""
for i in range(0,10):
    print("----- i = " + str(i) + "-------")
    testWorkersMarket()
    print("WorkersMarket End")
    testShareMarket()
    print("ShareMarket End")
    Prints.printPersonsAndFactories(Person.all_persons, Factory.all_factories)
"""     
 
#Prints
print("\n\n--------------- End State: ----------------\n\n") 

#Prints.printPersonsAndFactories(Person.all_persons,Factory.all_factories,3)

print(len(Factory.all_factories))
print(len(Person.all_persons))
pass
