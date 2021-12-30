from __future__ import annotations
from typing import List
from  Classes import Person,Factory, SharesMarket, WorkersMarket

#----todo----
def trade(factory : Factory,person : Person ,ammount : int):
    print(factory.owner.name+"'s factory traded " + str(factory.ammount) + " " + str(factory.product_is_essential) + "with " + person.name)
#------------

def startSim(people_number :int = 2,factory_number :int = 10,max_capital :int = 1000,min_capital :int = 10):
    #--GENERATE PERSONS--#
    import random
    import GetRandomNames
    #Generate random name for every person
    names = GetRandomNames.getRandomName(people_number)
    #Create person
    for i in range(0,people_number):
        person = Person(names[i], random.randint(min_capital, max_capital))
        Person.all_persons.append(person)

    def CreateFactories(people_number :int,factory_number :int):
        #Randomize number of workers assigned to every factory
        from MedianOneGenerator import generate
        number_workers_list = generate(people_number,factory_number)
        for i in range(0,factory_number):

            #Find an Owner
            owner_id = random.randint(0,people_number-1)
            counter = 0
            owner = Person.all_persons[owner_id]
            while(owner.owned_factories is not None and counter < people_number):
                counter+=1
                owner_id+=1
                if owner_id >= people_number:
                    owner_id = 0
                owner = Person.all_persons[owner_id]
            #if everyone owns a factory
            if counter >= people_number:
                print("Only created "+str(i)+" factories, everyone owns a factory!")
                return

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
            Factory.all_factories.append(factory)

            #Employ every worker and set owner
            factory.owner = owner
            for worker in workers:
                factory.workers = workers
                worker.employer = factory
            
            #Check if factory has no workers
            if len(factory.workers) == 0:
                Factory.all_factories.remove(factory)


    CreateFactories(people_number,factory_number)

startSim()

print("done starting sim")

def nextTimeStep():
    #WORKERS MARKET TIMESTEP
    #---------------------
    for factory in Factory.all_factories:
        factory.analyzeMarket() #find new stock ammount
        projected_salary = factory.calculateNeededProductivity() #Set new salary and search for new workers
        WorkersMarket.factory_salary_projection[factory] = projected_salary
    WorkersMarket.RunWorkersMarket()        
    #---------------------

    #SHARES MARKET TIMESTEP
    #---------------------
    for factory in Factory.all_factories:
        factory.getFunding()
    SharesMarket.runSharesMarket()
    #---------------------
    
    for factory in Factory.all_factories:
        factory.produce() #Pay salaries and produce new stock ammount
    for person in Person.all_persons:
        person.consume() #person.consume handles consumption of essencial, luxury and if owner, invest
        #CONSUMERS MARKET TIMESTEP
        #-------------------------
        #
        #-------------------------

#nextTimeStep()

def testWorkersMarket():
    from Classes import WorkersMarket, SharesMarket
    for factory in Factory.all_factories:
        factory.analyzeMarket() #find new stock ammount
        projected_salary = factory.calculateNeededProductivity() #Set new salary and search for new workers
        WorkersMarket.factory_salary_projection[factory] = projected_salary
    print("running workersMarket")
    WorkersMarket.RunWorkersMarket(True)


#Prints
import Prints
Prints.printPersonsAndFactories(Person.all_persons,Factory.all_factories)

