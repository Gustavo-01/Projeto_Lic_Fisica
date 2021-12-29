from __future__ import annotations
from typing import Dict, List, Tuple
from numpy import log, number

# necessary for pyton3 version < 10.0

# essencial will always be one, this will define the price relative to essencial
LUXURY_PRODUCE_PRICE_MULTIPLIER: float = 1.5
PRODUCTION_PER_PERSON_SCALE: float = 1.0
PRODUCTION_PER_PRODUCT: float = 1.0
FACTORY_STOCK_AGRESSIVENESS: float = 0.3

#- GLOBAL FUNCTIONS -

def productCost(is_essential: bool):
    cost = PRODUCTION_PER_PRODUCT
    if is_essential:
        cost *= LUXURY_PRODUCE_PRICE_MULTIPLIER
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
        self.owner: Person = owner #TODO change this
        self.workers: List[Person] = workers
        self.salary: int = len(self.workers) * productCost(product_is_essential)
        #Stock_variables
        self.stock: int = int(owner.capital/2)
        self.last_stock: int = self.stock
        self.avaliable_stock: int = self.stock
        self.new_stock_value:int = None
        #--------------
        self.shares_percentages: Dict[Person,float] = {owner: 1} #at creation, owner owns 100% of factory

        self.capital: int = 0
        
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

    def calculateNeededProductivity(self):
        ''' With new stock value, create or destroy productivity '''
        
        needed_productivity: float = self.new_stock_value * productCost(self.product_is_essential)
        return needed_productivity
    
    def project_salary(self, needed_productivity, test_mode):
        ''' Define new projected salary (attract more workers if bigger salary) '''
        last_productivity = self.stock * productCost(self.product_is_essential)

        #new_salary is the salary offered assuming no new workers
        #will be recalculated again once the workers market ends
        projected_salary = (needed_productivity / last_productivity) * self.salary

        if(test_mode):
            print("\n- FACTORY: " + str(self.fact_id) + "\n"+
                "last_productivity: " + str(last_productivity) + " -- needed_productivity: " + str(needed_productivity) +"\n"+
                "last_stock: " + str(self.stock) + " -- new_stock: " + str(self.new_stock_value))

        return projected_salary
    
    def getFunding(self):
        ''' Get funding from owner or put factory shares on the SharesMarket '''
        total_cost = self.salary * len(self.workers)
        max_owner_capital_invest = self.owner.max_capital_investment_per_factory()
        if(max_owner_capital_invest < total_cost):
            #ENTER SHARESMARKET
            share_value = SharesMarket.calculateShareValue(self)
            def get_needed_shares_number(shares_number):
                ''' Recursive function that finds maximum shares number sold such that (total_cost-shares_revenue) < max_owner_capital_invest '''
                owner_cost = total_cost - (shares_number * share_value)
                if owner_cost < max_owner_capital_invest:
                    return get_needed_shares_number(shares_number+1)
                else:
                    return shares_number-1

            needed_shares_number = get_needed_shares_number(0)
            if(needed_shares_number > 100):
                #TODO what if factory needs to sell more than all of itself??
                pass

            SharesMarket.set_shares_for_sale(self,needed_shares_number)
            owner_capital_investment = total_cost - (needed_shares_number*share_value)

        else:
            #Owner has the needed capital, factory will not enter SharesMarket
            owner_capital_investment = total_cost
        self.owner.transfer_capital(owner_capital_investment,self)

    def produce(self):
        ''' Pay salaries, create products '''
        
        pass

    #---------------------------------------
    #------- Static Functions --------------
    #---------------------------------------

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
            return round(base * (1 - ((leftover)**(3/2)-aggressiveness)))

        return stockFunction(last_two_mean, leftover_stock_ratio, FACTORY_STOCK_AGRESSIVENESS)
    
    @staticmethod
    def updateFactoryWorkers(factory_worker_number: dict[Factory,int]):
        '''Doublecheck if workers number match, set new workers variable for factories and set new salary'''
        
        def check_workers_number_match(factory_worker_number: dict[Factory,int]):
            for factory in factory_worker_number:
                if(len(factory.workers) != factory_worker_number[factory]):
                    
                    print("\n -- Factory_id: "+ str(factory.fact_id) + "\n- factory.workers: " + str(len(factory.workers))
                    +" -- factory_worker_number: " + str(factory_worker_number[factory]))
                    
                    raise Exception("Error in WorkersMarket (factory_worker_number != factory.workers)")
    
        #Update workers in factories
        for factory in Factory.all_factories:
            factory.workers = []
        for person in Person.all_persons:
            if(person.employer is not None):
                person.employer.workers.append(person)

        #Check for WorkersMarket errors
        check_workers_number_match(factory_worker_number)
        
        #Update factories salary
        for factory in Factory.all_factories:
            needed_productivity: float = factory.new_stock_value * productCost(factory.product_is_essential)
            factory.salary = Factory.salary_with_productivity(len(factory.workers),needed_productivity)

    def paySalary(self, worker: Person):
        #TODO
        if self.owner.capital >= self.salary:
            self.owner.capital -= self.salary
            worker.capital += self.salary
        else:
            self.__fire(worker)
            # worker.capital += self.salary #?

    def avaliableProductivity(self):
        productivity: float = Factory.productivity_with_salary(self.salary) * len(self.workers)
        return productivity
    
    #--Production

    def invest(self, base_funding: int):
        if base_funding > self.new_stock_value:
            investment = self.new_stock_value
        else:
            investment = base_funding
        # will add to production price if is not essencial
        self.stock = investment * (LUXURY_PRODUCE_PRICE_MULTIPLIER * self.product_is_essential)
        return investment

    def fire(self, person: Person):
        #TODO
        person.employer = None

#--------------------
#---- PERSON --------
#--------------------

class Person:
    '''Controls consumption and maximum investment'''

    all_persons: List[Person] = []

    def __init__(self, name: str, capital: int, employer: Factory = None, owned_factories: List[Factory] = []):
        self.name: str = name
        self.capital: int = capital
        self.employer: Factory = employer
        self.owned_factories: List[Factory] = owned_factories
        self.LUXURY_PERCENTAGE :float = 0.1 #TODO placeholder

    @staticmethod
    def essential_capital_projection():
        #TODO - return capital needed to (survive?) -> minimum capital needed to enter GoodsMarket
        #Used 1 as placeholder
        return 1
    
    def max_capital_investment_per_factory(self):
        #TODO test this
        if(len(self.owned_factories) > 0):
            return (self.capital - Person.essential_capital_projection()) * (1-self.LUXURY_PERCENTAGE/len(self.owned_factories))
        else:
            return 0
    
    def transfer_capital(self,capital: float,recipient: Person|Factory):
        if self.capital < capital:
            raise Exception("ATTEMPTED TRANSFER WITH INVALID CAPITAL")
        if type(recipient) != Factory and type(recipient) != Person:
            raise Exception("ATTEMPTED TRANSFER WITH INVALID RECIPIENT")
        recipient.capital += capital
        self.capital -= capital


#--------------------
#---- MARKETS -------
#--------------------

class GoodsMarket():
    '''DocString'''
    essencial_factories: List[Factory] = []
    luxury_factories: List[Factory] = []

class WorkersMarket():
    '''DocString'''
    avaliable_workers: List[Person] = []
    factory_salary_projection: Dict[Factory,float]= {}
    
    @staticmethod
    def RunWorkersMarket(test_mode = False):
        ''' Find work for every worker, set new employer for every person '''

        def get_hiring_factory(i: int):
            '''return hiring factory (factory the person will now be working for)'''
            hiring_factory = salary_sorted_factories[salary_sorted_factory_id_list[i]][0]
            if hiring_factory not in new_factory_worker_number:
                new_factory_worker_number[hiring_factory] = 0
            return hiring_factory

        from MedianOneGenerator import generate
        salary_sorted_factory_id_list: List[int] = generate(len(Factory.all_factories),len(Person.all_persons),) #give a number of workers per factory
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

class SharesMarket():
    factory_shares_for_sale: Dict[Factory,int] = {} #{factory: (share_number,share_value)}
    
    @staticmethod
    def calculateShareValue(factory: Factory):
        #TODO Maybe this works??
        #one share is 1% of factory current value
        return factory.stock * 0.01

    @staticmethod
    def set_shares_for_sale(factory: Factory, shares_number: int):
        SharesMarket.factory_shares_for_sale[factory] = shares_number

    @staticmethod
    def runSharesMarket():
        #Every share MUST be sold
        def try_sell_share(factory: Factory, value: float):
            for person in Person.all_persons:
                #TODO
                #idk...
                pass
            
        
        for factory in SharesMarket.factory_shares_for_sale:
            share_N = SharesMarket.factory_shares_for_sale[factory]
            share_V = SharesMarket.calculateShareValue(factory)
            for n in range(0,share_N):
                try_sell_share(factory,share_V)
        
        
        
        SharesMarket.factory_shares_for_sale = {}
