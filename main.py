from  Classes import Person,Factory

#----todo----
def trade(factory,person,ammount):
    print(factory.owner.name+"'s factory traded " + str(factory.ammount) + " " + str(factory.product) + "with " + person.name)
#------------

def startSim(people_number = 10,factory_number = 10,max_capital = 1000,min_capital = 0):
    #--GENERATE PERSONS--
    import random
    import GetRandomNames
    #Generate random name for every person
    names = GetRandomNames.getRandomName(people_number)
    #Create person
    for i in range(0,people_number):
        person = Person(names[i], random.randint(min_capital, max_capital))
        Person.all_persons.append(person)

    def CreateFactories(people_number,factory_number):
        #Randomize number of workers assigned to every factory
        import MedianOneGenerator
        number_workers_list = MedianOneGenerator.generate(people_number,factory_number)
        for i in range(0,factory_number):
            #Find an Owner
            ownerID = random.randint(0,people_number-1)
            counter = 0
            owner = Person.all_persons[ownerID]
            while(owner.ownedFactory != None and counter < people_number):
                counter+=1
                ownerID+=1
                if(ownerID >= people_number):
                    ownerID = 0
                owner = Person.all_persons[ownerID]
            #if everyone owns a factory
            if(counter >= people_number):
                print("Only created "+str(i)+" factories, everyone owns a factory!")
                return

            #Find workers
            number_workers = number_workers_list[i]
            workers = []
            for k in range(0,number_workers):
                #Grab random person
                workerID = random.randint(0,people_number-1)
                #If worker already is employed or is factory owner, search another worker
                counter = 0
                worker = Person.all_persons[workerID]
                while((worker.employer != None or worker.ownedFactory != None or worker.name == owner.name) and counter < people_number):
                    workerID += 1
                    counter += 1
                    if(workerID >= people_number):
                        workerID = 0
                    worker = Person.all_persons[workerID]
                if(counter < people_number):
                    workers.append(worker)

            #Create Factory
            factory = Factory(Person.all_persons[ownerID],workers,bool(random.randint(0,1)),i)
            Factory.all_factories.append(factory)

            #Employ every worker and set owner
            owner.ownedFactory = factory
            if(owner.employer != None):
                owner.employer.workers.remove(owner)
                owner.employer = None
                print("removed "+owner.name+" from factory "+str(i))
            for worker in workers:
                worker.employer = factory

    CreateFactories(people_number,factory_number)

startSim(50)

#Prints
import Prints
Prints.printPersonsAndFactories(Person.all_persons,Factory.all_factories)
