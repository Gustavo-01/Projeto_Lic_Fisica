from __future__ import annotations
from typing import Dict, List
from numpy import log

# necessary for pyton3 version < 10.0

# essencial will always be one, this will define the price relative to essencial
LUXURY_PRODUCE_PRICE: float = 1.5
PRODUCTION_PER_PERSON_SCALE: float = 1
PRODUCTION_PER_PRODUCT: float = 1
FACTORY_STOCK_AGRESSIVENESS: float = 0.3

def productCost(is_essential: bool):
    cost = PRODUCTION_PER_PRODUCT
    if is_essential:
        cost *= LUXURY_PRODUCE_PRICE
    return cost

class Factory:
    '''Controls production, salary payment, stockValues, and investment'''
    
    all_factories: List[Factory] = []

    def __init__(self, product_is_essential: bool, fact_id: int, workers: List[Person], owner: Person):
        self.fact_id: int = fact_id
        self.owner: Person = owner #TODO change this
        self.workers: List[Person] = workers
        self.salary: int = len(self.workers) * productCost(product_is_essential)
        self.product_is_essential: bool = product_is_essential
        self.product_ammount: int = None
        self.stock: int = int(owner.capital/2)
        self.last_stock: int = self.stock
        self.avaliable_stock: int = self.stock
        self.new_stock_value:int = None

        if product_is_essential:  # Is esential
            GoodsMarket.essencial_factories.append(self)
        else:
            GoodsMarket.luxury_factories.append(self)

    #--------------------------------
    #-- Functions called from main --
    #--------------------------------

    def analyzeMarket(self):
        ''' Find new stock ammount '''
        self.new_stock_value = Factory.findNewStockValue(self.stock,self.last_stock,self.avaliable_stock)
        
    
    def calculateNeededProductivity(self,test_mode = False):
        ''' With new stock value, create or destroy productivity (raise,lower) worker wages, (hire,fire) workers '''
        
        def project_salary(test_mode : bool):
            #TODO test this
            last_productivity = self.stock * productCost(self.product_is_essential)

            if(test_mode):
                print("\n- FACTORY: " + str(self.fact_id) + "\n"+
                      "last_productivity: " + str(last_productivity) + " -- needed_productivity: " + str(needed_productivity) +"\n"+
                      "last_stock: " + str(self.stock) + " -- new_stock: " + str(self.new_stock_value))
            
            return (needed_productivity / last_productivity) * self.salary
        
        needed_productivity: float = self.new_stock_value * productCost(self.product_is_essential)
        #new_salary is the salary offered assuming no new workers
        #will be recalculated again once the workers market ends
        projected_salary = project_salary(test_mode)
        return projected_salary
    
    def getFunding(self):
        ''' Get funding from owners or sell ownership '''
        
        cost = Factory.calculateCosts(len(self.workers),self.salary,self.new_stock_value)
        pass
    
    def produce(self):
        ''' Pay salaries, create products '''
        
        pass

    #---------------------------------------
    #------- General Functions -------------
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
        '''Doublecheck if workers number match, set new workers variable for factories'''
        
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
        #Check for errors
        check_workers_number_match(factory_worker_number)


    def paySalary(self, worker: Person):
        #TODO
        if self.owner.capital >= self.salary:
            self.owner.capital -= self.salary
            worker.capital += self.salary
        else:
            self.__fire(worker)
            # worker.capital += self.salary #?

    def avaliableProductivity(self):
        productivity: float = 10 + Factory.productivity_with_salary(self.salary) * len(self.workers) #Base productivity from owner is 10
        return productivity


    #--Production

    def invest(self, base_funding: int):
        if base_funding > self.new_stock_value:
            investment = self.new_stock_value
        else:
            investment = base_funding
        # will add to production price if is not essencial
        self.stock = investment * (LUXURY_PRODUCE_PRICE * self.product_is_essential)
        return investment

    def __fire(self, person: Person):
        #TODO
        person.employer = None



class Person:
    '''Controls consumption and maximum investment'''

    all_persons: List[Person] = []

    def __init__(self, name: str, capital: int, employer: Factory = None, owned_factories: List[Factory] = None):
        self.name: str = name
        self.capital: int = capital
        self.employer: Factory = employer
        self.owned_factories: List[Factory] = owned_factories

    def __consume_ess(self):
        # trade with factories
        print("traded essential")

    def __consume_lux(self):
        # trade with factories
        print("invested")

    def consume(self):
        self.__consume_ess()
        if self.owned_factories is not None:  # is a factory owner
            # Will invest up to 80% of remaining wealth
            self.capital -= self.owned_factories.invest(self.capital*0.8)
        self.__consume_lux()


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

    @staticmethod
    def getAvgSalary():
        salary_sum: int = 0
        i: int = 0
        for person in Person.all_persons:
            salary_sum += person.employer.salary
            i+=1
        return salary_sum/i
