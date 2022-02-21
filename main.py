from __future__ import annotations
from typing import List

from numpy import true_divide
from globals import *
import Prints
import enum

from tests import generate

class InitialConditions(enum.Enum):
    BOURGEOISIE = 1
    EGALITARIANISM = 2
    SOLE_OWNERSHIP = 3

def startSim(people_number :int = 30,factory_number :int = 10,max_capital :int = 1000,min_capital :int = 10, initial_condition: InitialConditions = InitialConditions.SOLE_OWNERSHIP, burgeoisie_percentage :int = 15):
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

        #Grab random people from first (person_count * burgeoisie_percentage) indices and distribute 100 over them
        share_holders :List[Person] = pickRandomPeople(number_shareholders_list[i], burgeoisie)
        #Distribute ShareValues
        share_values = uniformGenerate(0,len(share_holders), int_return=False)
        SUM = sum(share_values)
        share_values = [value/SUM * 100 for value in share_values]
        shares = {}
        for i in range(len(share_values)):
            shares[share_holders[i]] = share_values[i]

        #Create Factory
        factory = Factory(bool(round(random.random())),workers,shares,random.random()*max_capital + min_capital)

        #Check if factory has no workers
        if len(factory.workers) == 0:
            Factory.destroy(factory)

startSim()

print("done starting sim")
Prints.printPersonsAndFactories(Person.all_persons,Factory.all_factories)

def nextTimeStep():
    #CONSUMERS MARKET
    #-------------------------
    for factory in Factory.all_factories:
        factory.produce() #Pay salaries and produce new stock ammount
    GoodsMarket.runMarket()
    print("done with GoodsMarket")
    #-------------------------

    #Salary Projection
    #---------------------
    for factory in Factory.all_factories:
        factory.analyzeMarket() #find new stock ammount
        projected_salary = factory.calculateNeededProductivity() #Set new salary
        WorkersMarket.factory_salary_projection[factory] = projected_salary
    #---------------------

    #PRIMARY SHARES MARKET
    #---------------------
    for factory in Factory.all_factories:
        factory.getFunding()
    SharesMarket.runMarket()
    print("done with sharesMarket")
    #---------------------

    #WORKERS MARKET
    #----------------------
    WorkersMarket.runMarket()
    print("done with workersMarket")
    #---------------------

#GoodsMarket.runMarket()
#nextTimeStep()

Prints.printPersonsAndFactories(Person.all_persons,Factory.all_factories,1)

def testWorkersMarket():
    for factory in Factory.all_factories:
        factory.analyzeMarket() #find new stock ammount
        projected_salary = factory.calculateNeededProductivity() #Set new salary and search for new workers
        WorkersMarket.factory_salary_projection[factory] = projected_salary
    print("running workersMarket")
    WorkersMarket.runMarket(False)

#testWorkersMarket()
#print("WorkersMarket End")

def testShareMarket():
    for factory in Factory.all_factories:
        factory.getFunding()
    print("running sharesMarket")
    SharesMarket.runMarket()
#testShareMarket()

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
print("--------------- End State: ----------") 

#Prints.printPersonsAndFactories(Person.all_persons,Factory.all_factories,1)

