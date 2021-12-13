from __future__ import annotations
from typing import List
from numpy import NaN, log

# necessary for pyton3 version < 10.0

# essencial will always be one, this will define the price relative to essencial
LUXURY_PRODUCE_PRICE: float = 1.5
PRODUCTION_PER_PERSON_SCALE: float = 1

class Factory:
    '''Controls production, salary payment, stockValues, and investment'''
    
    all_factories: List[Factory] = []

    def __init__(self, owner: Person, workers: List[Person], product_is_essential: bool, fact_id: int, productivity: int = 1):
        self.fact_id: int = fact_id
        self.owner: Person = owner
        self.workers: List[Person] = workers
        self.product_is_essential: bool = product_is_essential
        self.productivity: int = productivity
        self.product_ammount: int = None
        self.salary: int = None #TODO (find salaries or hire)
        self.stock: int = int(owner.capital/2)
        self.last_stock: int = self.stock
        self.avaliable_stock: int = self.stock
        self.avaliable_productivity: int = self.__updateAvaliableProductivity()
        self.new_stock_value:int = NaN

        if product_is_essential:  # Is esential
            GoodsMarket.essencial_factories.append(self)
        else:
            GoodsMarket.luxury_factories.append(self)

    #--------------------------------
    #-- Functions called from main --
    #--------------------------------

    def analyzeMarket(self):
        ''' Find new stock ammount '''
        Factory.findNewStockValue(self,self.stock,self.last_stock,self.avaliable_stock)
        
        pass
    
    def getNeededProductivity(self,worker_ammount: int,new_stock_value: int):
        ''' With new stock value, create or destroy productivity (raise,lower) worker wages, (hire,fire) workers '''
        
        pass
    
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
    def findNewStockValue(stock: int, last_stock: int, leftover_stock: int):
        # Use last two stock values and leftOverStock to decide production
        last_two_mean = stock + (last_stock - stock)/2

        if stock != 0:  # division by 0 problem
            leftover_stock_ratio = leftover_stock/stock
        else:
            leftover_stock_ratio = 0

        def stockFunction(base, leftover, aggressiveness):
            return round(base * (1 - ((leftover)**(3/2)-aggressiveness)))

        return stockFunction(last_two_mean, leftover_stock_ratio, 0.3)
    
    def paySalary(self, worker: Person):
        #TODO
        if self.owner.capital >= self.salary:
            self.owner.capital -= self.salary
            worker.capital += self.salary
        else:
            self.__fire(worker)
            # worker.capital += self.salary #?

    def __updateAvaliableProductivity(self):
        return 10 + Factory.productivity_with_salary(self.salary) * len(self.workers) #Base productivity from owner is 10


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

    def __init__(self, name: str, capital: int, employer: Person = None, owned_factories: List[Factory] = None):
        self.name: str = name
        self.capital: int = capital
        self.employer: Person = employer
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

