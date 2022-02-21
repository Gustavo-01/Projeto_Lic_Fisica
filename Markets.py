from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Dict, List, Tuple
    from globals import Factory, Person


#--------------------
#--- GoodsMarket ----
#--------------------

class GoodsMarket():
    '''Controls consumption of essential an luxury, also sets each persons luxury_capital_percentage and sharemarket_capital_percentage'''
    essencial_factories: List[Factory] = []
    luxury_factories: List[Factory] = []
    avg_essential_price: float = 1
    
    @staticmethod
    def runMarket():
        from MedianOneGenerator import medianOneGenerate
        from globals import Person, transfer_capital

        def runEssentialMarket():

            price_sorted_factory_id_list: List[int] = medianOneGenerate(len(GoodsMarket.essencial_factories)-1,len(Person.all_persons)) #give a distribution of factories to trade (lower prices more likely)
            price_sorted_factories = sorted(GoodsMarket.essencial_factories,key= lambda x: x.product_price)

            def attemptEssentialTrade(person:Person, i: int,j: int = 0):
                ''' Act as a circular list until find tradeable factory '''
                
                if j > len(price_sorted_factories):
                    return False #Error, could not find any factory with enough stock to trade (or person has not enough capital to trade)
                
                idx = i + j #Circular list index
                if idx >= len(price_sorted_factories):
                    idx -= len(price_sorted_factories)
                
                trade_factory = price_sorted_factories[price_sorted_factory_id_list[idx]]
                
                if trade_factory.avaliable_stock == 0 or trade_factory.product_price > person.capital:
                    return attemptEssentialTrade(person,i,j+1)
                elif trade_factory.avaliable_stock > 0 and trade_factory.product_price < person.capital:
                    trade_factory.avaliable_stock -= 1
                    transfer_capital(person,trade_factory.product_price,trade_factory)
                    return True
            
            i :int = 0 #cycle persons with price_sorted_factories
            for person in Person.all_persons:
                #Find a factory to trade
                traded = attemptEssentialTrade(person,i)
                if not traded:
                    print("person did not consume essential")
                    #TODO what to do in this case?
            
            #TODO set essential capital projection for next timestep
        
        def runLuxuryMarket():
            
            price_sorted_factory_id_list: List[int] = medianOneGenerate(len(GoodsMarket.luxury_factories)-1,len(Person.all_persons)) #give a distribution of factories to trade (lower prices more likely)
            price_sorted_factories = sorted(GoodsMarket.luxury_factories,key= lambda x: x.product_price)

            def attemptLuxuryTrade(person:Person, max_cost: float, i: int,j: int = 0):
                ''' Act as a circular list until find tradeable factory '''
                
                if j > len(price_sorted_factories):
                    return False #Error, could not find any factory with enough stock to trade (or person has not enough capital to trade)
                
                idx = i + j #Circular list index
                if idx >= len(price_sorted_factories):
                    idx -= len(price_sorted_factories)
                
                trade_factory = price_sorted_factories[price_sorted_factory_id_list[idx]]
                
                if trade_factory.avaliable_stock == 0 or trade_factory.product_price > max_cost:
                    return attemptLuxuryTrade(person,max_cost,i,j+1)
                elif trade_factory.avaliable_stock > 0 and trade_factory.product_price < max_cost:
                    trade_factory.avaliable_stock -= 1
                    transfer_capital(person,trade_factory.product_price,trade_factory)
                    return True

            i :int = 0 #cycle persons with price_sorted_factories
            for person in Person.all_persons:
                max_luxury_capital_projection = person.luxury_capital_projection()
                luxury_expense = 0
                while(luxury_expense < max_luxury_capital_projection):
                    #Find a factory to trade
                    capital_before_trade = person.capital
                    traded = attemptLuxuryTrade(person,max_luxury_capital_projection,i)
                    if not traded:
                        print("person did not consume luxury")
                        break
                    else:
                        trade_cost = capital_before_trade - person.capital
                        luxury_expense += trade_cost

            #TODO set persons luxury_capital percentage and sharemarket_capital_percentage

        runEssentialMarket()

        runLuxuryMarket()


#--------------------
#-- WorkersMarket ---
#--------------------

class WorkersMarket():
    ''' Hires workers for factories '''
    avaliable_workers: List[Person] = []
    factory_salary_projection: Dict[Factory,float]= {}

    @staticmethod
    def runMarket(test_mode = False):
        ''' Find work for every worker, set new employer for every person '''

        from globals import Factory, Person

        def get_hiring_factory(i: int):
            '''return hiring factory (factory the person will now be working for)'''
            hiring_factory = salary_sorted_factories[salary_sorted_factory_id_list[i]][0]
            if hiring_factory not in new_factory_worker_number:
                new_factory_worker_number[hiring_factory] = 0
            return hiring_factory

        from MedianOneGenerator import medianOneGenerate
        salary_sorted_factory_id_list: List[int] = medianOneGenerate(len(Factory.all_factories)-1,len(Person.all_persons),) #give a number of workers per factory
        salary_sorted_factories = WorkersMarket.sort_dict(WorkersMarket.factory_salary_projection)

        if test_mode:
            import MedianOneGenerator
            MedianOneGenerator.plot_occurrences(salary_sorted_factory_id_list)


        i: int = 0 #cycle salary_sorted_factory_id_list
        new_factory_worker_number: Dict[Factory,int] = {}
        for person in Person.all_persons:
            hiring_factory = get_hiring_factory(i)
            
            #check if new worker number exceeds triple the original ammount
            j: int = 1 #cycle salary_sorted_factory_id_list until finds a factory not full (if needed)
            while new_factory_worker_number[hiring_factory] > 3*len(hiring_factory.workers):
                if(i+j < len(Factory.all_factories) and i+j >= 0):
                    hiring_factory = get_hiring_factory(i+j)
                j = (-j if j>0 else -(j-1))

                #--test_mode--#
                if j > len(Factory.all_factories):
                    #Person becomes unemployed
                    if test_mode:
                        print("Could not find factory! A person went unemployed!")
                    break
                #-------------#

            person.employer = hiring_factory
            i+=1
            new_factory_worker_number[hiring_factory] += 1

        if test_mode:
            print("\n\n"+"-"*30+"\n--- WORKER-MARKET-TEST ---\n\n")
            for factory in new_factory_worker_number:
                print("FACTORY: " + str(factory.fact_id) +"\n"+
                      "last-worker_N: " + str(len(factory.workers)) + "  --  new-worker_N: " + str(new_factory_worker_number[factory]) + "\n"+
                      "last-salary: " + str(factory.salary) + " -- projected-salary: " + str(WorkersMarket.factory_salary_projection[factory]))
        Factory.updateFactoryWorkers(new_factory_worker_number)

    @staticmethod
    def sort_dict(d : Dict[Factory,float]):
        return sorted(d.items(), key=lambda x: x[1])

    """
    @staticmethod
    def getAvgSalary():
        salary_sum: int = 0
        i: int = 0
        for person in Person.all_persons:
            salary_sum += person.employer.salary
            i+=1
        return salary_sum/i
    """

#--------------------
#--- SharesMarket ---
#--------------------

class SharesMarket():
    ''' Sells owners shares to make enough capital for production and controls secondary shares trading '''
    factory_shares_for_sale: Dict[Tuple[Factory,Person],int] = {} #{factory: (share_number,share_value)}
    
    @staticmethod
    def calculateShareValue(factory: Factory):
        #TODO Maybe this works??
        #one share is 1% of factory current value
        return factory.stock * 0.01

    @staticmethod
    def runMarket():
        
        from globals import Person

        def sell_share(seller: Person, factory: Factory, value: float, buyer: Person):
            '''Sell seller share in factory to buyer'''
            
            #check if shares match
            if seller.share_catalog[factory] != factory.share_holders[seller]:
                raise Exception("factory share record and seller share record do not match")
            
            #transfer capital from buyer to seller (or factory if seller is owner)
            if seller == factory.owner:
                globals.transfer_capital(buyer,value,factory) #Primary ShareMarket
            else:
                globals.transfer_capital(buyer,value,seller) #Secondary ShareMarket

            #transfer share from seller to buyer
            if buyer not in factory.share_holders:
                factory.share_holders[buyer] = 0.01
                buyer.share_catalog[factory] = 0.01
            else:
                factory.share_holders[buyer] += 0.01
                buyer.share_catalog[factory] += 0.01
            
            #remove share from seller
            factory.share_holders[seller] -= 0.01
            seller.share_catalog[factory] -= 0.01
            if factory.share_holders[seller] == 0:
                factory.share_holders.pop(seller)
                seller.share_catalog.pop(factory)

        def PrimaryMarket():
            '''Owner sells shares - capital goes to factory'''

            def primary_share_sell_attempt(factory: Factory, value: float):
                '''Attempt to sell factory share, capital goes directly to factory'''
                #should first attempt shareholders, then indiscriminated search
                for person in factory.share_holders:
                    if person.shareMarket_capital_investment_projection() > value:
                        sell_share(factory.owner,factory,value,person)
                        return True
                for person in Person.all_persons:
                    if person.shareMarket_capital_investment_projection() > value:
                        sell_share(factory.owner,factory,value,person)
                        return True
                return False

            #PRIMARY MARKET: Owner sells shares - Every share MUST be sold - capital goes directly to factory production
            for share in SharesMarket.factory_shares_for_sale:
                factory = share[0]
                share_N = SharesMarket.factory_shares_for_sale[share]
                share_V = SharesMarket.calculateShareValue(factory)
                for n in range(share_N):
                    sold = primary_share_sell_attempt(factory,share_V)
                    if not sold:
                        print("COULD NOT SELL SHARE IN SHAREMARKET!") #WHAT TO DO??
                    else:
                        SharesMarket.factory_shares_for_sale[share] -= 1
                factory.refreshOwner()
                SharesMarket.factory_shares_for_sale.pop(share)


            if(len(SharesMarket.factory_shares_for_sale) != 0):
                raise Exception("Something went wrong, factory_shares_for_sale is not empty after primary shareMarket round!")

        def SecondaryMarket():
            '''Shareholders sell and buy shares'''
            
            #Sell step
            for person in Person.all_persons:
                #if person cannot fulfil essential AND luxury needs:
                projected_capital = person.capital #projected capital after SecondaryMarket
                while projected_capital < (Person.essential_capital_projection() + person.luxury_capital_projection()):
                    #Sell some shares (AND lower luxury consumption!)
                    #TODO lower luxury consumption
                    import random
                    factory = random.choice(list(person.share_catalog.keys())) #pick a random factory from share catalog
                    projected_capital += SharesMarket.calculateShareValue(factory)
                    share = (factory,person)
                    if share not in SharesMarket.factory_shares_for_sale:
                        SharesMarket.factory_shares_for_sale[share] = 1
                    else:
                        SharesMarket.factory_shares_for_sale[share] += 1
            
            #Buy step
            #first attempt owner and shareholders
            for share in sorted(SharesMarket.factory_shares_for_sale,key=lambda x: SharesMarket.calculateShareValue(x[0])):
                factory = share[0]
                share_value = SharesMarket.calculateShareValue(factory)
                seller = share[1]
                while SharesMarket.factory_shares_for_sale[share] > 0:
                    
                    #shareHolders
                    for person in sorted(factory.share_holders,key=lambda x: factory.share_holders[x]):
                        if person.shareMarket_capital_investment_projection() > share_value:
                            sell_share(seller,factory,share_value,person)
                            SharesMarket.factory_shares_for_sale[share] -= 1
                            continue
                    
                    #indiscriminate search
                    for person in Person.all_persons:
                        if person.shareMarket_capital_investment_projection() > share_value:
                            sell_share(seller,factory,share_value,person)
                            SharesMarket.factory_shares_for_sale[share] -= 1
                            continue
                    
                    print("could not sell a factory share on secondary market")
                factory.refreshOwner()            
        
        PrimaryMarket()
        SecondaryMarket()


