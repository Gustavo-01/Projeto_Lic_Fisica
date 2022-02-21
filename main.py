from __future__ import annotations
from typing import List
from globals import *
import Prints
import enum

class Initial_conditions(enum.Enum):
    bourgeoisie = 1
    egalitarianism = 2
    sole_ownership = 3

def startSim(people_number :int = 20,factory_number :int = 10,max_capital :int = 1000,min_capital :int = 10, initial_condition: Initial_conditions = Initial_conditions.sole_ownership, burgeoisie_percentage :int = 15):
    #--Resolve initial conditions--#
    if initial_condition == Initial_conditions.egalitarianism:
        initial_condition = Initial_conditions.bourgeoisie
        burgeoisie_percentage = 100

    #--GENERATE PERSONS--#
    import random
    import GetRandomNames
    #Generate random name for every person
    names = GetRandomNames.getRandomName(people_number)
    #Create person
    for i in range(0,people_number):
        Person(names[i], random.randint(min_capital, max_capital))

    def pickRandomPerson():
        person_id = int(len(Person.all_persons) * random.random())
        return Person.all_persons[person_id]

    def CreateFactories(people_number :int,factory_number :int):
        #Randomize number of workers assigned to every factory
        from MedianOneGenerator import generate
        number_workers_list = generate(people_number,factory_number)
        for i in range(factory_number):

            #Find ShareHolders
            """
            owner_id = random.randint(0,people_number-1)
            counter = 0
            owner = Person.all_persons[owner_id]
            while(len(owner.owned_factories) > 0):
                counter+=1
                owner_id+=1
                if owner_id >= people_number:
                    owner_id = 0
                owner = Person.all_persons[owner_id]
                if counter >= people_number:
                    break
            #if everyone owns a factory
            if counter >= people_number:
                print("Only created "+str(i)+" factories, everyone owns a factory!")
                return
            """
            def findShareHolders():
                pass

            
            def findWorker():
                #Grab random person
                worker_id = random.randint(0,people_number-1)
                counter = 0
                worker = Person.all_persons[worker_id]
                #If worker already is employed, search another worker
                while(worker.employer is not None):
                    worker_id += 1
                    counter += 1
                    if worker_id >= people_number:
                        worker_id = 0
                    if counter == people_number-1:
                        return None
                    worker = Person.all_persons[worker_id]
                worker.employer = -1 #flags person as employed (until factory is created)
                return worker

            #Find workers
            number_workers = number_workers_list[i]
            if number_workers == 0:
                number_workers = 1
            workers: List[Factory] = []
            for k in range(0,number_workers):
                worker = findWorker()
                if worker is not None:
                    workers.append(worker)

            #Create Factory
            factory = Factory(bool(random.randint(0,1)),i,workers, owner)
            owner.owned_factories.append(factory)
            owner.share_catalog[factory] = 1
            
            #Check if factory has no workers
            if len(factory.workers) == 0:
                Factory.destroy(factory)

    def CreateFactory(shareHolders : Dict[Person,int], workers :List[Person]):
        pass

    CreateFactories(people_number,factory_number)

startSim()

print("done starting sim")
Prints.printPersonsAndFactories(Person.all_persons,Factory.all_factories)


def nextTimeStep():
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

    #CONSUMERS MARKET
    #-------------------------
    for factory in Factory.all_factories:
        factory.produce() #Pay salaries and produce new stock ammount
    GoodsMarket.runMarket()
    print("done with GoodsMarket")
    #-------------------------

GoodsMarket.runMarket()
nextTimeStep()

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

