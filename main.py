from __future__ import annotations
from  Classes import Person,Factory

#----todo----
def trade(factory : Factory,person : Person ,ammount : int):
    print(factory.owner.name+"'s factory traded " + str(factory.ammount) + " " + str(factory.product_is_essential) + "with " + person.name)
#------------

def startSim(people_number :int = 10,factory_number :int = 10,max_capital :int = 1000,min_capital :int = 0):
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
        import MedianOneGenerator
        number_workers_list = MedianOneGenerator.generate(people_number,factory_number)
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

            #Find workers
            number_workers = number_workers_list[i]
            workers = []
            for k in range(0,number_workers):
                #Grab random person
                worker_id = random.randint(0,people_number-1)
                #If worker already is employed or is factory owner, search another worker
                counter = 0
                worker = Person.all_persons[worker_id]
                while((worker.employer is not None or worker.owned_factories is not None or worker.name == owner.name) and counter < people_number):
                    worker_id += 1
                    counter += 1
                    if worker_id >= people_number:
                        worker_id = 0
                    worker = Person.all_persons[worker_id]
                if counter < people_number:
                    workers.append(worker)

            #Create Factory
            factory = Factory(Person.all_persons[owner_id],workers,bool(random.randint(0,1)),i)
            Factory.all_factories.append(factory)

            #Employ every worker and set owner
            owner.owned_factories = factory
            if owner.employer is not None:
                owner.employer.workers.remove(owner)
                owner.employer = None
                print("removed "+owner.name+" from factory "+str(i))
            for worker in workers:
                worker.employer = factory

    CreateFactories(people_number,factory_number)



startSim()

def nextTimeStep():
    for factory in Factory.all_factories:
        factory.analyzeMarket() #find new stock ammount
        factory.getNeededProductivity() #Set new salary and search for new workers
        #WOKERS MARKET TIMESTEP
        #---------------------
        #
        #---------------------
        factory.getFunding() #If needed, sell factory ownership
        #SHARES MARKET TIMESTEP
        #---------------------
        #
        #---------------------
        factory.produce() #Pay salaries and produce new stock ammount
    for person in Person.all_persons:
        person.consume() #person.consume handles consumption of essencial, luxury and if owner, invest
        #CONSUMERS MARKET TIMESTEP
        #-------------------------
        #
        #-------------------------

nextTimeStep()

#Prints
import Prints
Prints.printPersonsAndFactories(Person.all_persons,Factory.all_factories)
