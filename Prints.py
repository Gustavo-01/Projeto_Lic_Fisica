def printPersonsAndFactories(all_persons,all_factories):
    print("PERSONS")
    print("{0:<20} - {1:<4} - {2:<10}".format("Name","Capital","Employed"))
    print("-"*45)
    for person in all_persons:
        employed = "not employed"
        if(person.employer != None):
            employed = "employed by "+str(person.employer.id)
        if(person.ownedFactory != None):
            employed = "Owns factory: " + str(person.ownedFactory.id)
        print("{0:<20} - {1:<4} - {2:<10}".format(person.name,str(person.capital),employed))
    print("")
    print("-FACTORIES-")
    print("{3:<2} {0:<20} - {1:<9} - {2:<10}".format("Owner_Name","N_Workers","Essencial","ID"))
    print("-"*50)
    for factory in all_factories:
        print("{3:<2} {0:<20} - {1:<9} - {2:<10}".format(factory.owner.name,str(len(factory.workers)),str(factory.product),factory.id))

