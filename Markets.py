from __future__ import annotations
from logging.config import valid_ident
from typing import TYPE_CHECKING
import numpy

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

        def trade_essential(factory: Factory, buyer: Person, max_trade_ammount : float):
            traded_product = max_trade_ammount
            if factory.avaliable_stock <= traded_product:
                traded_product = factory.avaliable_stock
            if(buyer.capital <= factory.product_price * traded_product):
                traded_product = buyer.capital/factory.product_price
            
            buyer.essential_satisfaction = traded_product
            
            transfer_capital(buyer,traded_product*factory.product_price, factory,'bought essential')
            factory.avaliable_stock -= traded_product

            return traded_product

        def trade_luxury(factory: Factory, buyer: Person, max_cost: float):
            from math import floor

            # This division creates errors that propagate!!
            # Truncate on decimal e^-10
            max_cost = (10**-10)*floor((10**10)*max_cost)
            traded_product = max_cost/factory.product_price
            if factory.avaliable_stock < traded_product:
                traded_product = factory.avaliable_stock

            #TODO fix this mess
            buyer.luxury_satisfaction += traded_product

            transfer_capital(buyer, traded_product*factory.product_price, factory, 'bought luxury')
            factory.avaliable_stock -= traded_product

            return traded_product * factory.product_price

        def runEssentialMarket():

            price_sorted_factory_id_list: List[int] = medianOneGenerate(len(GoodsMarket.essencial_factories)-1,len(Person.all_persons),decay_speed=0.9) #give a distribution of factories to trade (lower prices more likely)
            price_sorted_factories = sorted(GoodsMarket.essencial_factories, key=lambda x: x.product_price)

            def attemptEssentialTrade(person: Person, needed_essentials: float, i: int, j: int = 0):
                ''' Act as a circular list until find tradeable factory '''

                from globals import FLOATING_POINT_ERROR_MARGIN
                
                if j > len(price_sorted_factory_id_list):
                    return 1 - needed_essentials  #Error, could not find any factory with enough stock to trade (or person has not enough capital to trade)

                idx = i + j  #Circular list index
                while idx >= len(price_sorted_factory_id_list):
                    idx -= len(price_sorted_factory_id_list)

                trade_factory = price_sorted_factories[price_sorted_factory_id_list[idx]]

                if trade_factory.avaliable_stock <= 0:
                    return attemptEssentialTrade(person, needed_essentials, i, j+1)
                else:
                    traded_ammount = trade_essential(trade_factory, person, needed_essentials)
                    needed_essentials -= traded_ammount
                    return 1 - needed_essentials

            for i in range(len(Person.all_persons)):
                person = Person.all_persons[i]
                #Find a factory to trade
                traded = attemptEssentialTrade(person, 1, i)
                person.essential_satisfaction = traded
            
            pass
            #TODO set essential capital projection for next timestep?

        def runLuxuryMarket():
            
            price_sorted_factory_id_list: List[int] = medianOneGenerate(len(GoodsMarket.luxury_factories)-1, len(Person.all_persons))  #give a distribution of factories to trade (lower prices more likely)
            price_sorted_factories = sorted(GoodsMarket.luxury_factories, key=lambda x: x.product_price)

            def attemptLuxuryTrade(person: Person, max_cost: float, i: int, j: int=0):
                ''' Act as a circular list until find tradeable factory '''

                from globals import FLOATING_POINT_ERROR_MARGIN
                
                if j > len(price_sorted_factory_id_list) or max_cost <= FLOATING_POINT_ERROR_MARGIN: # No factory has stock or person has consumed all luxury capital
                    return max_cost

                idx = i + j  #Circular list index
                while idx >= len(price_sorted_factory_id_list):
                    idx -= len(price_sorted_factory_id_list)

                trade_factory = price_sorted_factories[price_sorted_factory_id_list[idx]]

                if trade_factory.avaliable_stock <= 0:
                    return attemptLuxuryTrade(person, max_cost, i, j+1)
                else:
                    trade_cost = trade_luxury(trade_factory, person, max_cost)
                    max_cost -= trade_cost
                    return attemptLuxuryTrade(person, max_cost, i, j+1)

            from globals import FLOATING_POINT_ERROR_MARGIN
            
            for i in range(len(Person.all_persons)):
                person = Person.all_persons[i]
                max_luxury_capital_projection = person.luxury_capital_projection()
                #Find a factory to trade
                leftover_capital = attemptLuxuryTrade(person, max_luxury_capital_projection, i)
                if leftover_capital > FLOATING_POINT_ERROR_MARGIN:
                    #TODO what to do in this case?
                    pass

            pass
            #TODO set persons luxury_capital percentage and sharemarket_capital_percentage

        if len(GoodsMarket.essencial_factories) > 0:
            runEssentialMarket()
        #Update person expense agenda
        for person in Person.all_persons:
            person.update_timestep_capital()
            person.luxury_satisfaction = 0
        if len(GoodsMarket.luxury_factories) > 0:
            runLuxuryMarket()


#--------------------
#-- WorkersMarket ---
#--------------------

class WorkersMarket():
    ''' Hires workers for factories '''
    workers_to_update: Dict[Factory, List[Person]] = {}

    #Find factory with bigger salary - update salary

    @staticmethod
    def runMarket():
        ''' Find work for every worker, set new employer for every person '''

        from globals import Factory, Person, MINIMUM_WAGE

        #----------------------------------------------------------
        projected_salary_sorted: List[Factory] = sorted(
            Factory.all_factories, key=lambda factory: factory.labor_avaliable_capital(), reverse=True
            )
        new_factory_worker_number: Dict[Factory, int] = {}
        for factory in Factory.all_factories:
            new_factory_worker_number[factory] = 0
        #----------------------------------------------------------

        persons_shuffled = [person for person in Person.all_persons]
        numpy.random.shuffle(persons_shuffled)
        for person in persons_shuffled:
            #Factories with more than triple their original workers cannot hire more
            projected_salary_sorted = [factory for factory in projected_salary_sorted if new_factory_worker_number[factory] <= 3*len(factory.workers)+1]

            #Get hiring factory (factory with higher salary)
            if(len(projected_salary_sorted) == 0):  #No more hiring factories
                person.employer = None
                break
            else:
                hiring_factory = projected_salary_sorted[0]

            #- Employ if salary bigger than minimum wage -#
            projected_salary = hiring_factory.labor_avaliable_capital() / (1+new_factory_worker_number[hiring_factory]) #Salary for worker if it joins now, can be lower but never higher
            if projected_salary <= MINIMUM_WAGE:
                person.employer = None  #There exists no more factories capable of hiring higher than minimum wage
                continue
            else:
                person.employer = hiring_factory

            if hiring_factory not in WorkersMarket.workers_to_update:
                WorkersMarket.workers_to_update[hiring_factory] = [person]
            else:
                WorkersMarket.workers_to_update[hiring_factory].append(person)
            new_factory_worker_number[hiring_factory] += 1

            #Re-sort factories
            projected_salary_sorted: List[Factory] = sorted(
                projected_salary_sorted, key=lambda factory: factory.labor_avaliable_capital()/(1+new_factory_worker_number[factory]), reverse=True
                )
            #-----------#            
        #- Update workers -#
        Factory.updateFactoryWorkers(WorkersMarket.workers_to_update)
        pass

#--------------------
#--- SharesMarket ---
#--------------------


class SharesMarket():
    ''' Sells owners shares to make enough capital for production and controls secondary shares trading '''
    shares_for_trade: Dict[Tuple[Factory, Person],float] = {}  #{(facotry,seller): share}
    factory_shares: Dict[Factory, float] = {} # {factory: (share}
    avaliable_capital: Dict[Person,float] = {} #{person: avaliable capital for primary shareMarket}

    @staticmethod
    def close_primary(factory:  Factory):
        '''Set sum share value as 1'''

        share_values = list(factory.share_holders.values())
        share_holders = list(factory.share_holders.keys())
        SUM = sum(share_values)
        share_values = [value/SUM for value in share_values]
        shares = {}
        for i in range(len(share_values)):
            shares[share_holders[i]] = share_values[i]
        
        factory.share_holders = shares
        for share_holder in shares:
            share_holder.share_catalog[factory] = shares[share_holder]


    @staticmethod
    def share_value(share: float, factory: Factory):
        '''Takes into account stock price, stock ammount, workers and salary'''
        from globals import FLOATING_POINT_ERROR_MARGIN
        value_per_share = factory.capital + (factory.product_price * factory.avaliable_stock) + (factory.salary * len(factory.workers))
        if value_per_share <= FLOATING_POINT_ERROR_MARGIN:
            return 0
        return share * value_per_share

    @staticmethod
    def share_ammount(capital: float, factory: Factory):
        '''Returns ammount of shares for sale to achieve needed capital (if factory is worth 0, then returns -1)'''
        from globals import FLOATING_POINT_ERROR_MARGIN
        value_per_share = factory.capital + (factory.product_price * factory.avaliable_stock) + (factory.salary * len(factory.workers))
        if(value_per_share <= FLOATING_POINT_ERROR_MARGIN):
            return -1  #Signals that factory is bankrupt
        return capital / value_per_share


    @staticmethod
    def runMarket():
        from globals import Person, transfer_capital, FLOATING_POINT_ERROR_MARGIN

        def sell_shares(factory: Factory, price: float, shares: float, buyer: Person, seller: Person | Factory = None):
            '''Create new shares and sell to buyer'''

            #transfer share from seller to buyer
            if buyer not in factory.share_holders:
                factory.share_holders[buyer] = shares
                buyer.share_catalog[factory] = shares
            else:
                factory.share_holders[buyer] += shares
                buyer.share_catalog[factory] += shares

            if seller is None:
                seller = factory  #Sold directly from factory
            else:
                seller.share_catalog[factory] -= shares
                factory.share_holders[seller] -= shares
                if seller.share_catalog[factory] == 0:
                    seller.share_catalog.pop(factory)
                    factory.share_holders.pop(seller)
           
            SharesMarket.avaliable_capital[buyer] -= price
            
            transfer_capital(buyer, price, seller,'bought share')

            #remove share from market
            if seller == factory:
                SharesMarket.factory_shares[factory] -= shares
            else:
                SharesMarket.shares_for_trade[(factory, seller)] -= shares

        def PrimaryMarket():
            '''create shares - capital goes to factory'''

            def primary_share_sell_attempt(factory: Factory, shares_for_sale: float, person: Person):
                '''Attempt to sell factory share'''

                from globals import FLOATING_POINT_ERROR_MARGIN

                max_investment = SharesMarket.avaliable_capital[person]

                total_share_value = SharesMarket.share_value(shares_for_sale, factory)
                if (total_share_value / shares_for_sale <= FLOATING_POINT_ERROR_MARGIN):
                    #FACTORY BANKRUPT - Buy 100% and delete all shareholders
                    for shareHolder in factory.share_holders.keys():
                        shareHolder.share_catalog.pop(factory)
                    factory.share_holders = {}
                    print("BANKRUPT: factory " + str(factory.fact_id) + " bought by " + person.name)
                    total_share_value = max_investment / 2
                    shares_for_sale = 1
                
                if max_investment >= total_share_value:
                    sold_shares = shares_for_sale
                    price = total_share_value
                else:
                    price = max_investment
                    sold_shares = shares_for_sale * price / total_share_value
                
                sell_shares(factory, price, sold_shares, person)

            #PRIMARY MARKET: Factory sells shares - Every share must be sold
            for factory in SharesMarket.factory_shares:

                #- First attempt shareholders -#
                ShareHolders_shuffled = [person for person in factory.share_holders.keys() if person.capital > FLOATING_POINT_ERROR_MARGIN]
                numpy.random.shuffle(ShareHolders_shuffled)
                for person in ShareHolders_shuffled:
                    shares_for_sale = SharesMarket.factory_shares[factory]
                    if SharesMarket.factory_shares[factory] <= 0:
                        break

                    if SharesMarket.avaliable_capital[person] / 2 > FLOATING_POINT_ERROR_MARGIN:
                        primary_share_sell_attempt(factory, shares_for_sale, person)

                #- Then indiscriminated search -#
                person_shuffled = [person for person in Person.all_persons if person.capital > FLOATING_POINT_ERROR_MARGIN and person not in ShareHolders_shuffled]
                numpy.random.shuffle(person_shuffled)
                for person in person_shuffled:
                    shares_for_sale = SharesMarket.factory_shares[factory]
                    if SharesMarket.factory_shares[factory] <= 0:
                        break
                    if SharesMarket.avaliable_capital[person] / 2 > FLOATING_POINT_ERROR_MARGIN:
                        primary_share_sell_attempt(factory,shares_for_sale,person)      
                             
            SharesMarket.factory_shares = {}

        def SecondaryMarket():
            '''Shareholders sell and buy shares'''
            
            from globals import FLOATING_POINT_ERROR_MARGIN, Factory
            
            def secondary_share_sell_attempt(seller:Person, total_share_value:float, factory: Factory, buyer: Person):
                '''Attempt to sell factory share'''

                max_investment = SharesMarket.avaliable_capital[person]
                if max_investment >= total_share_value:
                    price = total_share_value
                else:
                    price = max_investment

                sold_shares = SharesMarket.share_ammount(price, factory)
                if(sold_shares == -1):
                    return

                if sold_shares < FLOATING_POINT_ERROR_MARGIN:
                    return
                
                sell_shares(factory,price,sold_shares,buyer,seller)

            #Sell step
            for share_holder in [person for person in Person.all_persons if len(person.share_catalog) != 0]:
                #if person cannot fulfil essential AND luxury needs:
                if share_holder.capital < (Person.essential_capital_projection(Factory.all_factories) + share_holder.luxury_capital_projection()):

                    needed_capital = (Person.essential_capital_projection(Factory.all_factories) + share_holder.luxury_capital_projection()) - share_holder.capital
                    #- TODO lower luxury consumption! -
                    
                    #----------------------------------
                    #Sell shares
                    for factory in share_holder.share_catalog:
                        needed_shares = SharesMarket.share_ammount(needed_capital,factory)
                        if(needed_shares == -1):
                            continue
                        if(needed_shares >= share_holder.share_catalog[factory]):
                            shares_for_sale = share_holder.share_catalog[factory]
                        else:
                            shares_for_sale = needed_shares
                        
                        shares_value = SharesMarket.share_value(shares_for_sale,factory)
                        if(shares_value < FLOATING_POINT_ERROR_MARGIN):
                            continue
                        SharesMarket.shares_for_trade[(factory,share_holder)] = shares_for_sale

                        needed_capital -= shares_value
                        if needed_capital <= 0:
                            break
            
            #Buy step
            #Sort by share value (biggest goes first)
            sorted_shares = sorted(SharesMarket.shares_for_trade,key=lambda x: SharesMarket.share_value(SharesMarket.shares_for_trade[x],x[0]))
            for share in sorted_shares:
                factory = share[0]
                seller = share[1]
                total_share_value = SharesMarket.share_value(SharesMarket.shares_for_trade[share],factory)
                if (total_share_value / SharesMarket.shares_for_trade[share] <= FLOATING_POINT_ERROR_MARGIN):
                    #Factory is bankrupt - cannot sell share on secondary market
                    continue

                #- Indiscriminated search -#
                person_shuffled = [person for person in Person.all_persons if person.capital > FLOATING_POINT_ERROR_MARGIN]
                numpy.random.shuffle(person_shuffled)
                for person in person_shuffled:
                    if SharesMarket.shares_for_trade[share] <= 0:
                        SharesMarket.shares_for_trade.pop(share)
                        break
                    if SharesMarket.avaliable_capital[person] > FLOATING_POINT_ERROR_MARGIN:
                        secondary_share_sell_attempt(seller, total_share_value, factory, person)

            SharesMarket.shares_for_trade = {} #empty shares for trade
        
        for person in Person.all_persons:
            SharesMarket.avaliable_capital[person] = person.shareMarket_capital_investment_projection()
        PrimaryMarket()
        SecondaryMarket()



