from __future__ import annotations
from typing import TYPE_CHECKING
import numpy
from sympy import per

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

        def trade_essential(factory: Factory, buyer: Person,max_trade_ammount : float):
            traded_product = max_trade_ammount
            if factory.avaliable_stock <= traded_product:
                traded_product = factory.avaliable_stock
            if(buyer.capital <= factory.product_price * traded_product):
                traded_product = buyer.capital/factory.product_price
            
            buyer.essential_satisfaction = traded_product
            
            transfer_capital(buyer,traded_product*factory.product_price,factory)
            factory.avaliable_stock -= traded_product

            return traded_product

        def trade_luxury(factory: Factory, buyer: Person, max_cost: float):
            traded_product = max_cost/factory.product_price
            if factory.avaliable_stock < traded_product:
                traded_product = factory.avaliable_stock

            buyer.luxury_satisfaction = 1 - ((buyer.luxury_satisfaction)-traded_product)/buyer.luxury_satisfaction
            
            transfer_capital(buyer,traded_product*factory.product_price,factory)
            factory.avaliable_stock -= traded_product

            return traded_product * factory.product_price

        def runEssentialMarket():

            price_sorted_factory_id_list: List[int] = medianOneGenerate(len(GoodsMarket.essencial_factories)-1,len(Person.all_persons),decay_speed=0.9) #give a distribution of factories to trade (lower prices more likely)
            price_sorted_factories = sorted(GoodsMarket.essencial_factories,key= lambda x: x.product_price)

            def attemptEssentialTrade(person:Person, needed_essentials :float, i: int, j: int = 0):
                ''' Act as a circular list until find tradeable factory '''

                if j > len(price_sorted_factories):
                    return False #Error, could not find any factory with enough stock to trade (or person has not enough capital to trade)

                idx = i + j #Circular list index
                if idx >= len(price_sorted_factories):
                    idx -= len(price_sorted_factories)

                trade_factory = price_sorted_factories[price_sorted_factory_id_list[idx]]

                if trade_factory.avaliable_stock <= 0:
                    return attemptEssentialTrade(person,needed_essentials,i,j+1)
                else:
                    traded_ammount = trade_essential(trade_factory,person,needed_essentials)
                    needed_essentials -= traded_ammount
                    if needed_essentials <= 0:
                        return True
                    else:
                        return attemptEssentialTrade(person,needed_essentials,i,j+1)

            for i in range(len(Person.all_persons)):
                person = Person.all_persons[i]
                #Find a factory to trade
                traded = attemptEssentialTrade(person,1,i)
                if not traded:
                    print("person did not consume essential")
                    #TODO what to do in this case?
            
            pass
            #TODO set essential capital projection for next timestep?
        
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


                if trade_factory.avaliable_stock <= 0:
                    return attemptLuxuryTrade(person,max_cost,i,j+1)
                else:
                    trade_cost = trade_luxury(trade_factory,person,max_cost)
                    max_cost -= trade_cost
                    if max_cost <= 0:
                        return True
                    else:
                        return attemptLuxuryTrade(person,max_cost,i,j+1)


            for i in range(len(Person.all_persons)):
                person = Person.all_persons[i]
                max_luxury_capital_projection = person.luxury_capital_projection()
                #Find a factory to trade
                traded = attemptLuxuryTrade(person,max_luxury_capital_projection,i)
                if not traded:
                    print("person did not fully consume luxury")
                    #TODO what to do in this case?

            pass
            #TODO set persons luxury_capital percentage and sharemarket_capital_percentage

        if len(GoodsMarket.essencial_factories)>0:
            runEssentialMarket()
        if len(GoodsMarket.luxury_factories) > 0:
            runLuxuryMarket()


#--------------------
#-- WorkersMarket ---
#--------------------

class WorkersMarket():
    ''' Hires workers for factories '''
    factory_labor_capital: Dict[Factory,float]= {}

    workers_to_update: Dict[Factory,List[Person]] = {}

    @staticmethod
    def runMarket(test_mode = False):
        ''' Find work for every worker, set new employer for every person '''

        from globals import Factory, Person

        def get_hiring_factory(i: int):
            '''return hiring factory (factory the person will now be working for)'''

            hiring_factory = sorted_factories[sorted_factory_id_list[i]]
            if hiring_factory not in new_factory_worker_number:
                new_factory_worker_number[hiring_factory] = 0
            return hiring_factory

        #---------------------------------------------------------
        from MedianOneGenerator import medianOneGenerate
        sorted_factory_id_list: List[int] = medianOneGenerate(len(Factory.all_factories)-1,len(Person.all_persons),) #give a number of workers per factory
        sorted_factories = sorted(WorkersMarket.factory_labor_capital, key=WorkersMarket.factory_labor_capital.get)
        #----------------------------------------------------------

        new_factory_worker_number: Dict[Factory,int] = {}
        for i in range(len(Person.all_persons)):
            person = Person.all_persons[i]
            hiring_factory = get_hiring_factory(i)
            
            #check if new worker number exceeds triple the original ammount
            j: int = 1 #cycle salary_sorted_factory_id_list until finds a factory not full (if needed)
            while new_factory_worker_number[hiring_factory] > 3*len(hiring_factory.workers):
                idx = i + j #Circular list index
                if idx >= len(Factory.all_factories):
                    idx -= len(Factory.all_factories)
                
                hiring_factory = get_hiring_factory(idx)

                if j > len(Factory.all_factories):
                    #Person becomes unemployed
                    print("Could not find factory!" + person.name + " went unemployed!")
                    #All factories are full
                    break

            #- Employ -#
            person.employer = hiring_factory
            
            if hiring_factory not in WorkersMarket.workers_to_update:
                WorkersMarket.workers_to_update[hiring_factory] = [person]
            else:
                WorkersMarket.workers_to_update[hiring_factory].append(person)
            #-----------#
        #- Update workers -#
        Factory.updateFactoryWorkers(WorkersMarket.workers_to_update)

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
    shares_for_trade: Dict[Tuple[Factory,Person],float] = {} #{(facotry,seller): share}
    factory_shares: Dict[Factory,float] = {} # {factory: (share}

    @staticmethod
    def share_value(share: float, factory: Factory):
        return share * factory.capital

    @staticmethod
    def runMarket():
        
        from globals import Person, transfer_capital

        def sell_shares(factory: Factory, price: float, shares: float, buyer: Person, seller :Person|Factory = None):
            '''Create new shares and sell to buyer'''
            
            #transfer share from seller to buyer
            if buyer not in factory.share_holders:
                factory.share_holders[buyer] = shares
                buyer.share_catalog[factory] = shares
            else:
                factory.share_holders[buyer] += shares
                buyer.share_catalog[factory] += shares

            if seller == None:
                seller = factory #Sold directly from factory
            else:
                seller.share_catalog[factory] -= shares
                factory.share_holders[seller] -= shares
                if seller.share_catalog[factory] == 0:
                    seller.share_catalog.pop(factory)
                    factory.share_holders.pop(seller)

            transfer_capital(buyer,price,seller)
            
            #remove share from market
            SharesMarket.factory_shares[factory] -= shares

        def PrimaryMarket():
            '''create shares - capital goes to factory'''

            def primary_share_sell_attempt(factory:Factory, shares_for_sale:float, person: Person):
                '''Attempt to sell factory share'''
                
                #TODO Selling too many shares

                max_investment = person.shareMarket_capital_investment_projection() / 2
                total_share_value = SharesMarket.share_value(shares_for_sale,factory)
                if max_investment >= total_share_value:
                    sold_shares = shares_for_sale
                    price = total_share_value
                else:
                    price = max_investment
                    sold_shares = shares_for_sale * price / total_share_value

                sell_shares(factory,price,sold_shares,person)

            #PRIMARY MARKET: Factory sells shares - Every share must be sold
            for factory in SharesMarket.factory_shares:

                #- First attempt shareholders -#
                unordered_list = list(range(len(factory.share_holders)-1))
                share_holders_list = list(factory.share_holders.keys())
                numpy.random.shuffle(unordered_list)
                for i in unordered_list:
                    shares_for_sale = SharesMarket.factory_shares[factory]
                    person = share_holders_list[i]
                    if SharesMarket.factory_shares[factory] <= 0:
                        break
                    primary_share_sell_attempt(factory,shares_for_sale,person)

                if factory not in SharesMarket.factory_shares:
                    #All shares were sold to shareHolders
                    break

                #- Then indiscriminated search -#
                unordered_list = list(range(len(Person.all_persons)-1))
                numpy.random.shuffle(unordered_list)
                for i in unordered_list:
                    shares_for_sale = SharesMarket.factory_shares[factory]
                    if SharesMarket.factory_shares[factory] <= 0:
                        break
                    person = Person.all_persons[i]
                    primary_share_sell_attempt(factory,shares_for_sale,person)
            
            for value in SharesMarket.factory_shares.values():
                if value > 0:
                    raise Exception("Something went wrong, factory_shares_for_sale is not empty after primary shareMarket round!")
            SharesMarket.factory_shares = {}

        def SecondaryMarket():
            '''Shareholders sell and buy shares'''
            
            def secondary_share_sell_attempt(seller:Person, shares_for_sale:float, buyer: Person):
                '''Attempt to sell factory share'''
                
                max_investment = buyer.shareMarket_capital_investment_projection() / 2
                total_share_value = SharesMarket.share_value(shares_for_sale,factory)
                if max_investment >= total_share_value:
                    sold_shares = shares_for_sale
                    price = total_share_value
                else:
                    price = max_investment
                    sold_shares = shares_for_sale * price / total_share_value

                sell_shares(factory,price,sold_shares,seller)

            #Sell step
            for share_holder in Person.all_persons:
                #if person cannot fulfil essential AND luxury needs:
                if share_holder.capital < (Person.essential_capital_projection() + share_holder.luxury_capital_projection()):

                    needed_capital = (Person.essential_capital_projection() + share_holder.luxury_capital_projection()) - share_holder.capital
                    #- TODO lower luxury consumption! -
                    
                    #----------------------------------
                    import random
                    #Sell some shares
                    for factory in share_holder.share_catalog:
                        total_share_value = share_holder.share_catalog[factory] * factory.capital
                        if(total_share_value >= needed_capital):
                            shares_for_sale = needed_capital/total_share_value
                        else:
                            shares_for_sale = share_holder.share_catalog[factory]
                        SharesMarket.shares_for_trade[(factory,share_holder)] = shares_for_sale

                        needed_capital -= SharesMarket.share_value(shares_for_sale,factory)
                        if needed_capital <= 0:
                            break
            
            #Buy step
            #Sort by share value (biggest goes first)            
            sorted_shares = sorted(SharesMarket.shares_for_trade,key=lambda x: SharesMarket.share_value(x[0], SharesMarket.shares_for_trade[x[0]]))
            for share in sorted_shares:
                factory = share[0]
                seller = share[1]
                total_share_value = SharesMarket.share_value(SharesMarket.shares_for_trade[share],factory)
                
                #- Indiscriminated search -#
                unordered_list = range(len(Person.all_persons)-1)
                numpy.random.shuffle(unordered_list)
                for i in unordered_list:
                    if SharesMarket.shares_for_trade[factory] <= 0:
                        SharesMarket.shares_for_trade.pop(factory)
                        break
                    person = Person.all_persons[i]
                    secondary_share_sell_attempt(seller,shares_for_sale,person)

            if(len(SharesMarket.shares_for_trade) != 0):
                    print("could not sell a factory share on secondary market")
        
        PrimaryMarket()
        SecondaryMarket()


