from __future__ import annotations
from cmath import inf
from typing import List

import enum

from numpy import NaN
from globals import Person, Factory, GoodsMarket, WorkersMarket, SharesMarket, cleanup
import Prints


class InitialConditions(enum.Enum):
    BOURGEOISIE = 1
    EGALITARIANISM = 2
    SOLE_OWNERSHIP = 3
    MONOPOLY = 4


def startSim(people_number: int = 20, factory_number: int = 20, max_capital: int = 1000, min_capital: int = 10, initial_condition: InitialConditions = InitialConditions.EGALITARIANISM, burgeoisie_percentage: int = 15):
    #--Resolve initial conditions--#
    if initial_condition == InitialConditions.EGALITARIANISM:
        initial_condition = InitialConditions.BOURGEOISIE
        burgeoisie_percentage = 100
    if InitialConditions == InitialConditions.MONOPOLY:
        burgeoisie_percentage = 1/people_number * 100

    #--GENERATE PERSONS--#
    import random
    import GetRandomNames
    from MedianOneGenerator import medianOneGenerate, uniformGenerate
    from math import ceil
    #Generate random name for every person
    names = GetRandomNames.getRandomName(people_number)
    #Create person
    unemployed_people: List[Person] = []
    burgeoisie: List[Person] = []
    for i in range(0, people_number):
        person = Person(names[i], random.randint(min_capital, max_capital))
        unemployed_people.append(person)
        if i <= ceil(people_number * burgeoisie_percentage):
            burgeoisie.append(person)

    #--FACTORY CREATION--#
    def pickRandomPeople(ammount: int = 1, pool=Person.all_persons, repetition=True) -> List[Person]:
        if(len(pool) <= ammount):
            ammount = len(pool) - 1
        indexes = uniformGenerate(len(pool)-1, ammount, repetition=repetition)
        return [pool[i] for i in indexes]

    def findWorkers(ammount: int = 1):
        #Grab random unemployed
        workers = pickRandomPeople(ammount, unemployed_people, repetition=False)
        for worker in workers:
            unemployed_people.remove(worker)
        return workers

    #Workers
    number_workers_list = medianOneGenerate(people_number, factory_number, min_number=1)
    number_shareholders_list = medianOneGenerate(people_number * burgeoisie_percentage/100, factory_number, min_number=1)

    for i in range(factory_number):
        workers: List[Person] = findWorkers(number_workers_list[i])
        if len(workers) == 0:
            continue
        #Grab random people from first (person_count * burgeoisie_percentage) indices and distribute 100 over them
        share_holders: List[Person] = pickRandomPeople(number_shareholders_list[i], burgeoisie, repetition=False) #TODO ERROR! Returning same person twice!
        #Distribute ShareValues
        share_values = uniformGenerate(0, len(share_holders), int_return=False) #max_number = 0+1
        SUM = sum(share_values)
        share_values = [value/SUM for value in share_values]
        shares = {}
        for i in range(len(share_values)):
            shares[share_holders[i]] = share_values[i]

        #Create Factory
        Factory(bool(round(random.random())), workers, shares, random.random()*max_capital + min_capital)


startSim(initial_condition=InitialConditions.MONOPOLY)

print("done starting sim")


def nextTimeStep():

    #CONSUMERS MARKET
    #-------------------------
    for factory in Factory.all_factories:
        factory.produce() #Pay salaries and produce new stock ammount
    GoodsMarket.runMarket()
    #-------------------------

    #Salary Projection and fundraising
    #---------------------
    for factory in Factory.all_factories:
        projected_capital = factory.project_needed_capital() #Project needed capital
        factory.getFunding(projected_capital) #Fundraise (set shares for sale or distribute capital)
    #---------------------

    #SHARES MARKET
    #---------------------
    SharesMarket.runMarket()
    #---------------------

    #WORKERS MARKET
    #----------------------
    WorkersMarket.runMarket()
    #---------------------
    
    cleanup(Person.all_persons, Factory.all_factories)
    

f = open("printOutput/print.txt", "w")
f.close()
for i in range(0, 1000):
    f = open("printOutput/print.txt", "a")
    Prints.printPersonsAndFactories(Person.all_persons, Factory.all_factories, i, f)
    nextTimeStep()
    f.close()



#Prints
print("\n\n--------------- End State: ----------------\n\n")

#Prints.printPersonsAndFactories(Person.all_persons,Factory.all_factories,3)

print(len(Factory.all_factories))
print(len(Person.all_persons))
pass
