from __future__ import annotations
from typing import Dict, List, Tuple
from numpy import log

LUXURY_PRODUCION_COST_MULTIPLIER: float = 1.5 # essencial will always be one, this will define the price relative to essencial

PRODUCTION_PER_PERSON_SCALE: float = 1.0
PRODUCTION_PER_PRODUCT: float = 1.0

FACTORY_STOCK_AGRESSIVENESS: float = 0.3 #could be dynamic for every factory

#- GLOBAL FUNCTIONS -

def transfer_capital(sender: Person|Factory,capital: float,recipient: Person|Factory):
    if sender.capital < capital:
        raise Exception("ATTEMPTED TRANSFER WITH INVALID CAPITAL")
    if type(recipient) != Factory and type(recipient) != Person:
        raise Exception("ATTEMPTED TRANSFER WITH INVALID RECIPIENT")
    if type(sender) != Factory and type(sender) != Person:
        raise Exception("ATTEMPTED TRANSFER WITH INVALID SENDER")        
    recipient.capital += capital
    sender.capital -= capital

def productProductivityCost(is_essential: bool):
    cost = PRODUCTION_PER_PRODUCT
    if is_essential:
        cost *= LUXURY_PRODUCION_COST_MULTIPLIER
    return cost

#--------------------
#---- FACTORY -------
#--------------------

class Factory:
    '''Controls production, salary payment, stockValues, and investment'''
    
    all_factories: List[Factory] = []

    def __init__(self, product_is_essential: bool, fact_id: int, workers: List[Person], owner: Person):
        self.fact_id: int = fact_id
        self.product_is_essential: bool = product_is_essential
        #owner
        self.owner: Person = owner
        #--------------
        self.workers: List[Person] = workers
        for worker in workers:
            worker.employer = self
        self.salary: int = len(self.workers) * productProductivityCost(product_is_essential)
        self.product_price: float = (self.salary * len(self.workers)) + 0 
        #Stock_variables
        self.stock: int = int(owner.capital/2)
        self.last_stock: int = self.stock
        self.avaliable_stock: int = self.stock
        self.new_stock_value:int = None
        #--------------
        self.share_holders: Dict[Person,float] = {owner: 1} #at creation, owner owns 100% of factory

        self.capital: int = 0

        self.profit_margin_per_product = 0.1 #determined by leftover stock and factory aggressiveness


        if product_is_essential:  # Is esential
            GoodsMarket.essencial_factories.append(self)
        else:
            GoodsMarket.luxury_factories.append(self)

    #--------------------------------
    #-- Functions called from main --
    #--------------------------------

    def analyzeMarket(self):
        ''' Find new stock value '''
        self.new_stock_value = Factory.findNewStockValue(self.stock,self.last_stock,self.avaliable_stock)
        self.profit_margin_per_product = (self.stock - self.last_stock) * (FACTORY_STOCK_AGRESSIVENESS/self.stock)

    def getFunding(self):
        ''' Get funding from owner or put factory shares on the SharesMarket '''
        total_cost = self.salary * len(self.workers)
        max_owner_capital_invest = self.owner.max_capital_investment_per_factory()
        if max_owner_capital_invest < total_cost:
            #ENTER SHARESMARKET
            share_value = SharesMarket.calculateShareValue(self)
            def get_needed_shares_number(shares_number):
                ''' Recursive function that finds maximum shares number sold such that (total_cost-shares_revenue) < max_owner_capital_invest '''
                owner_cost = total_cost - (shares_number * share_value)
                if owner_cost > max_owner_capital_invest:
                    return get_needed_shares_number(shares_number+1)
                else:
                    return shares_number

            needed_shares_number = get_needed_shares_number(0)
            if needed_shares_number > 100:
                #TODO what if factory needs to sell more than all of itself??
                pass

            SharesMarket.factory_shares_for_sale[(self,self.owner)] = needed_shares_number
            owner_capital_investment = total_cost - (needed_shares_number*share_value)

        else:
            #Owner has the needed capital, factory will not enter SharesMarket
            owner_capital_investment = total_cost
        transfer_capital(self.owner,owner_capital_investment,self)

    def produce(self):
        ''' Pay salaries, create products and set price '''
        #last stock is this timestep stock
        self.last_stock = self.stock
        
        #define product price
        cost_per_product = self.capital / self.stock
        self.product_price = cost_per_product + self.profit_margin_per_product
        
        #Pay salaries
        def pay_salary(person: Person):
            if person.employer != self:
                raise Exception("Factory is paying salary of a non-worker person!")
            transfer_capital(self,self.salary,person)

        for person in self.workers:
            pay_salary(person)

        #produce
        new_stock = int(self.productivity_with_salary(self.salary) * len(self.workers) * productProductivityCost(self.product_is_essential))
        self.stock = new_stock + self.avaliable_stock
        self.avaliable_stock = self.stock

    #-------------------------------
    #------ General Methods --------
    #-------------------------------
    
    def calculateNeededProductivity(self):
        ''' With new stock value, create or destroy productivity '''
        
        stock_to_produce = self.new_stock_value-self.avaliable_stock
        if stock_to_produce < 0:
            stock_to_produce = 0
        needed_productivity: float = stock_to_produce * productProductivityCost(self.product_is_essential)
        return needed_productivity

    def project_salary(self, needed_productivity, test_mode):
        ''' Define new projected salary (attract more workers if bigger salary) '''
        last_productivity = self.stock * productProductivityCost(self.product_is_essential)

        #new_salary is the salary offered assuming no new workers
        #will be recalculated again once the workers market ends
        projected_salary = (needed_productivity / last_productivity) * self.salary

        if test_mode:
            print("\n- FACTORY: " + str(self.fact_id) + "\n"+
                "last_productivity: " + str(last_productivity) + " -- needed_productivity: " + str(needed_productivity) +"\n"+
                "last_stock: " + str(self.stock) + " -- new_stock: " + str(self.new_stock_value))

        return projected_salary

    def refreshOwner(self):
        '''Find maximum share holder, set that as owner'''
        #Find max share holder
        max_share_holder = self.owner
        for person in self.share_holders:
            if self.share_holders[person] > self.share_holders[max_share_holder]:
                max_share_holder = person

        if max_share_holder != self.owner:
            #change owner
            self.owner.owned_factories.pop(self)
            max_share_holder.owned_factories.append(self)
            self.owner = max_share_holder

    def avaliableProductivity(self):
        productivity: float = Factory.productivity_with_salary(self.salary) * len(self.workers)
        return productivity

    #---------------------------------------
    #------- Static Functions --------------
    #---------------------------------------

    @staticmethod
    def destroy(factory: Factory):
        factory.owner.owned_factories.remove(factory)
        for person in factory.share_holders:
            person.share_catalog.pop(factory)
        Factory.all_factories.remove(factory)

    #--Important-- Will determine how productive every person is
    @staticmethod
    def productivity_with_salary(salary :int):
        if salary is None :
            salary=0
        return  log((salary+1)) * 50 * PRODUCTION_PER_PERSON_SCALE

    @staticmethod
    def salary_with_productivity(N: int, productivity: float):
        #N must be > 0
        exp = productivity/(N * PRODUCTION_PER_PERSON_SCALE * 50)
        return 10**(exp) -1

    @staticmethod
    def findNewStockValue(stock: int, last_stock: int, leftover_stock: int):
        # Use last two stock values and leftOverStock to decide production
        last_two_mean = stock + (last_stock - stock)/2

        if stock != 0:  # division by 0 problem
            leftover_stock_ratio = leftover_stock/stock
        else:
            leftover_stock_ratio = 0

        def stockFunction(base, leftover, aggressiveness):
            '''Return best stock for next step'''
            return round(base * (1 - ((leftover)**(3/2)-aggressiveness)))

        return stockFunction(last_two_mean, leftover_stock_ratio, FACTORY_STOCK_AGRESSIVENESS)

    @staticmethod
    def updateFactoryWorkers(factory_worker_number: dict[Factory,int]):
        '''Doublecheck if workers number match, set new workers variable for factories set new salary '''
        
        def check_workers_number_match(factory_worker_number: dict[Factory,int]):
            for factory in factory_worker_number:
                if len(factory.workers) != factory_worker_number[factory]:
                    
                    print("\n -- Factory_id: "+ str(factory.fact_id) + "\n- factory.workers: " + str(len(factory.workers))
                    +" -- factory_worker_number: " + str(factory_worker_number[factory]))
                    
                    raise Exception("Error in WorkersMarket (factory_worker_number != factory.workers)")
    
        #Update workers in factories
        for factory in Factory.all_factories:
            factory.workers = []
        for person in Person.all_persons:
            if person.employer is not None:
                person.employer.workers.append(person)
        
        #Check for WorkersMarket errors
        check_workers_number_match(factory_worker_number)
        
        #Update factories salary
        for factory in Factory.all_factories:
            needed_productivity: float = factory.new_stock_value * productProductivityCost(factory.product_is_essential)
            if len(factory.workers) > 0:
                factory.salary = Factory.salary_with_productivity(len(factory.workers),needed_productivity)
            else:
                Factory.destroy(factory)
    
#--------------------
#---- PERSON --------
#--------------------

class Person:
    '''Controls consumption and maximum investment'''

    all_persons: List[Person] = []

    def __init__(self, name: str, capital: int, employer: Factory = None):
        self.name: str = name
        self.capital: int = capital
        self.employer: Factory = employer
        self.owned_factories: List[Factory] = []
        self.share_catalog: Dict[Factory,float] = {}
        self.LUXURY_CAPITAL_PERCENTAGE :float = 0.01 #TODO placeholder - if person filled its luxury_capital_percentage, percentage should increase
        self.SHAREMARKET_CAPITAL_PERCENTAGE :float = 0.01 #TODO placeholder - if person could not buy any shares and, percentage should increase, if person is owner, percentage should grow slower

    @staticmethod
    def essential_capital_projection():
        #TODO - return capital needed to (survive?) -> minimum capital needed to enter GoodsMarket
        #Used 1 as placeholder
        return 1

    def luxury_capital_projection(self):
        ''' Calculated after essential market Timestep (essential capital already withdrawn) '''
        return self.capital * self.LUXURY_CAPITAL_PERCENTAGE

    def shareMarket_capital_investment_projection(self):
        ''' Calculated after essential market Timestep (essential capital already withdrawn) '''
        return self.capital * self.SHAREMARKET_CAPITAL_PERCENTAGE

    def factory_capital_investment_projection(self):
        ''' capital avaliable  '''
        return self.capital - (self.luxury_capital_projection() + self.shareMarket_capital_investment_projection())

    def max_capital_investment_per_factory(self):
        #TODO test this
        if len(self.owned_factories) > 0:
            return self.factory_capital_investment_projection()/len(self.owned_factories)
        else:
            return 0


#-----------------------
#---- M A R K E T S ----
#-----------------------

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
        from MedianOneGenerator import generate

        def runEssentialMarket():

            price_sorted_factory_id_list: List[int] = generate(len(GoodsMarket.essencial_factories)-1,len(Person.all_persons)) #give a distribution of factories to trade (lower prices more likely)
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
            
            price_sorted_factory_id_list: List[int] = generate(len(GoodsMarket.luxury_factories)-1,len(Person.all_persons)) #give a distribution of factories to trade (lower prices more likely)
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

        def get_hiring_factory(i: int):
            '''return hiring factory (factory the person will now be working for)'''
            hiring_factory = salary_sorted_factories[salary_sorted_factory_id_list[i]][0]
            if hiring_factory not in new_factory_worker_number:
                new_factory_worker_number[hiring_factory] = 0
            return hiring_factory

        from MedianOneGenerator import generate
        salary_sorted_factory_id_list: List[int] = generate(len(Factory.all_factories)-1,len(Person.all_persons),) #give a number of workers per factory
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
        
        def sell_share(seller: Person, factory: Factory, value: float, buyer: Person):
            '''Sell seller share in factory to buyer'''
            
            #check if shares match
            if seller.share_catalog[factory] != factory.share_holders[seller]:
                raise Exception("factory share record and seller share record do not match")
            
            #transfer capital from buyer to seller (or factory if seller is owner)
            if seller == factory.owner:
                transfer_capital(buyer,value,factory) #Primary ShareMarket
            else:
                transfer_capital(buyer,value,seller) #Secondary ShareMarket

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


