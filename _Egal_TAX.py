from __future__ import annotations
from typing import Dict, List, Tuple

import enum
from matplotlib import pyplot as plt
from math import ceil

from globals import Person, Factory, GoodsMarket, WorkersMarket, SharesMarket, cleanup, saveState, act_government, Government, Gov
import Prints


class InitialConditions(enum.Enum):
    BOURGEOISIE = 1
    EGALITARIANISM = 2
    SOLE_OWNERSHIP = 3
    MONOPOLY = 4


def startSim(people_number: int = 20, factory_number: int = 6, max_capital: int = 1000,
             min_capital: int = 10, initial_condition: InitialConditions = InitialConditions.EGALITARIANISM,
             burgeoisie_percentage: int = 0.5):
    #--Delete any previous simulation residue--#
    Person.all_persons = []
    Factory.all_factories = []
    SharesMarket.factory_shares = {}
    SharesMarket.shares_for_trade = {}
    GoodsMarket.essential_factories = []
    GoodsMarket.luxury_factories = []
    WorkersMarket.workers_to_update = {}

    #--Resolve initial conditions--#
    print(initial_condition)
    if initial_condition == InitialConditions.EGALITARIANISM:
        burgeoisie_percentage = 1
    elif initial_condition == InitialConditions.MONOPOLY:
        burgeoisie_percentage = 1/people_number
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
        if i < people_number * burgeoisie_percentage:
            burgeoisie.append(person)

    #--FACTORY CREATION--#
    def pickRandomPeople(ammount: int = 1, pool=Person.all_persons, repetition=True) -> List[Person]:
        if(len(pool) < ammount):
            ammount = len(pool)
        indexes = uniformGenerate(len(pool)-1, int(ammount), repetition=repetition)
        return [pool[i] for i in indexes]

    def findWorkers(ammount: int = 1):
        if ammount == 0 or len(unemployed_people) == 0:
            return [] 
        #Grab random unemployed
        workers = pickRandomPeople(ammount, unemployed_people, repetition=False)
        for worker in workers:
            unemployed_people.remove(worker)
        return workers

    #Workers
    number_workers_list = medianOneGenerate(people_number, factory_number, min_number=1)
    number_shareholders_list = medianOneGenerate(people_number * burgeoisie_percentage, factory_number, min_number=1)

    for i in range(factory_number):
        workers: List[Person] = findWorkers(number_workers_list[i])
        if len(workers) == 0:
            continue
        #Grab random people from first (person_count * burgeoisie_percentage) indices and distribute 100 over them
        if initial_condition == InitialConditions.SOLE_OWNERSHIP:
            owner = Person.all_persons[i]
            shares = {}
            shares[owner] = 1
        else:
            share_holders: List[Person] = pickRandomPeople(number_shareholders_list[i], burgeoisie, repetition=False) #TODO ERROR! Returning same person twice!
            #Distribute ShareValues
            share_values = uniformGenerate(0, len(share_holders), int_return=False) #max_number = 0+1
            SUM = sum(share_values)
            share_values = [value/SUM for value in share_values]
            shares = {}
            for i in range(len(share_values)):
                shares[share_holders[i]] = share_values[i]

        #Create Factory
        if(len([factory for factory in Factory.all_factories if factory.product_is_essential]) == 0):
            essential = True
        elif(len([factory for factory in Factory.all_factories if not factory.product_is_essential]) == 0):
            essential = False
        else:
            essential = bool(round(random.random()))
        Factory(essential, workers, shares, random.random()*max_capital + min_capital)

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

    act_government(Person.all_persons)


f = open("printOutput/print.txt", "w")
f.close()
def run_f(cycles,initial_condition):
    graph_interval: int = ceil(cycles/200)
    bufferstates: List[float] = []
    states: List[List[float]] = []
    startSim(initial_condition = initial_condition)
    nextTimeStep()
    for i in range(0, cycles):
        #Prints.printPersonsAndFactories(Person.all_persons, Factory.all_factories, i, f)
        nextTimeStep()
        bufferstates.append(saveState(Person.all_persons, Factory.all_factories))
        if i % graph_interval == 0:
            bufferstate_n = len(bufferstates[0])
            state = [0] * bufferstate_n
            for bufferstate in bufferstates:
                for i in range(0,len(bufferstate)):
                    state[i] += bufferstate[i]
            states.append([s/len(bufferstates) for s in state])
            bufferstates = []
    return Prints.process_state(states,cycles)

def get_plot(runs_n,cycles,initial_condition):    
    runs: Tuple[List[int], List[List[float]]] = list()
    for i in range(0, runs_n):
        runs.append(run_f(cycles,initial_condition))
        print(i)
    (days,vals) = Prints.process_multistate(runs,cycles)
    return Prints.plotStates(days,vals).gca()

initial_condition = InitialConditions.EGALITARIANISM
Government.type = Gov.NONE
get_plot(30,5000,initial_condition)
Government.type = Gov.TRANSATION
get_plot(30,5000,initial_condition)
Government.type = Gov.WEALTH_CAP
get_plot(30,5000,initial_condition)
Government.type = Gov.BOTH
get_plot(30,5000,initial_condition)
l = plt.legend(["No tax", "Transaction", "Wealth cap", "Both"])
l.set_draggable(True)

f.close()
plt.show()
