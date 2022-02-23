from __future__ import annotations
from tkinter.messagebox import NO
from typing import TYPE_CHECKING
from numpy import log
if TYPE_CHECKING:
    from typing import Dict, List, Tuple
    from globals import Person, GoodsMarket, WorkersMarket, SharesMarket

class Factory:
    '''Controls production, salary payment, stockValues, and investment'''

    all_factories: List[Factory] = []
    __fact_id__ :int = 0

    def __init__(self, product_is_essential: bool, workers: List[Person], shares: Dict[Person,float], capital :float):
        from globals import GoodsMarket, LUXURY_PRODUCION_COST

        #- Register factory -#
        self.__fact_id__ = Factory.__fact_id__
        Factory.__fact_id__ += 1
        Factory.all_factories.append(self)
        if product_is_essential:  # Is esential
            GoodsMarket.essencial_factories.append(self)
            self.production_cost_per_product = 1
        else:
            GoodsMarket.luxury_factories.append(self)
            self.production_cost_per_product = LUXURY_PRODUCION_COST

        #- Capital -#
        self.capital: int = capital
        self.original_capital: int = capital #TEST
        self.labor_avaliable_capital_percentage = 1
        #-- Constants --
        self.product_is_essential: bool = product_is_essential
        #--ShareHolders----
        self.share_holders :Dict[Person,float] = shares
        for share_holder in shares:
            share_holder.share_catalog[self] = shares[share_holder]
        #--Workers----------
        self.workers: List[Person] = workers
        for worker in workers:
            worker.employer = self
        self.salary: int = capital / len(workers)
        #--Stock variables--
        self.stock: int = self.production_cost_per_product * Factory.production_per_worker(self.salary) * len(workers)
        self.last_stock: int = self.stock
        self.avaliable_stock: int = 0
        self.new_stock:int = None
        #--Product price---
        self.profit_margin_per_product = 0.4 #determined by leftover stock and factory aggressiveness
        self.product_price: float = (1+self.profit_margin_per_product) * (self.capital/self.stock)
        #-----------


    #--------------------------------
    #-- Functions called from main --
    #--------------------------------

    def findNewStock(self):
        ''' Find new stock value '''
        from globals import FACTORY_STOCK_AGRESSIVENESS

        self.new_stock = Factory.findNewStockValue(self.stock,self.last_stock,self.avaliable_stock)
        self.profit_margin_per_product = (self.stock - self.last_stock) * (FACTORY_STOCK_AGRESSIVENESS/self.stock)

    def getFunding(self,projected_capital):
        ''' Get funding by selling factory shares on the SharesMarket '''
        from globals import SharesMarket

        capital = self.labor_avaliable_capital()
        if projected_capital > capital:
            #ENTER SHARESMARKET
            needed_capital = projected_capital - capital

            #Factory cannot sell more than half of itself in a single timestep
            if(needed_capital > capital/2):
                needed_capital = capital/2
            shares_to_sell = needed_capital/capital
            SharesMarket.factory_shares[self] = shares_to_sell

            #TODO Remove percentage from all shareHolders
            
        else:
            #factory will not enter SharesMarket
            return

    def produce(self):
        ''' Pay salaries, create products and set price '''
        from globals import transfer_capital

        #last stock is this timestep stock
        self.last_stock = self.stock

        self.product_price = (1+self.profit_margin_per_product) * (self.capital/self.stock)

        for person in self.workers:
            if person.employer != self:
                raise Exception("Factory is paying salary of a non-worker person!")
            transfer_capital(self,self.salary,person)

        #produce
        print(self.new_stock)
        new_stock: int = self.production_cost_per_product * self.production_per_worker(self.salary) * len(self.workers)
        self.stock = new_stock + self.avaliable_stock
        self.avaliable_stock = self.stock

    def project_labor_capital(self):
        ''' project total labor cost (rough estimate) '''

        last_produced_stock = self.stock - self.last_stock

        if self.new_stock == 0:
            return 0
        if last_produced_stock == 0:
            return self.labor_avaliable_capital()
        return len(self.workers) * self.salary * self.new_stock / last_produced_stock

    #-------------------------------
    #------ General Methods --------
    #-------------------------------

    def labor_avaliable_capital(self):
        return self.capital * self.labor_avaliable_capital_percentage

    #---------------------------------------
    #------- Static Functions --------------
    #---------------------------------------

    @staticmethod
    def destroy(factory: Factory):
        from globals import transfer_capital, GoodsMarket

        final_capital = factory.capital
        for share_holder in factory.share_holders:
            #Return leftover capital to shareHolders
            transfer_capital(factory, factory.share_holders[share_holder]*final_capital/100, share_holder)
            #Delete shares from shareHolders
            share_holder.share_catalog.pop(factory)
        for worker in factory.workers:
            worker.employer = None

        Factory.all_factories.remove(factory)
        if(factory.product_is_essential):
            GoodsMarket.essencial_factories.remove(factory)
        else:
            GoodsMarket.luxury_factories.remove(factory)

    #TODO fixing
    @staticmethod
    def salary_with_productivity(N: int, productivity: float):
        from globals import PRODUCTION_PER_PERSON_SCALE
        from numpy import e

        # find salary from (log(salary)+1) * PRODUCTION_PER_PERSON_SCALE = production

        #N must be > 0
        exp = productivity/(N * PRODUCTION_PER_PERSON_SCALE * 50)
        return 10**(exp) -1

    @staticmethod
    def production_per_worker(salary :int):
        from globals import PRODUCTION_PER_PERSON_SCALE
        from numpy import e

        if salary is None or salary <= 1/e:
            return 0
        return (log(salary)+1) * PRODUCTION_PER_PERSON_SCALE

    @staticmethod
    def findNewStockValue(stock: int, last_stock: int, leftover_stock: int):
        '''Returns optimal ammount of new stock production'''
        from globals import FACTORY_STOCK_AGRESSIVENESS

        # Use last two stock values and leftOverStock to decide production
        last_two_mean = stock + (last_stock - stock)/2

        if stock != 0:  # division by 0 problem
            leftover_stock_ratio = leftover_stock/stock
        else:
            leftover_stock_ratio = 0

        def stockFunction(base, leftover_ratio, aggressiveness):
            '''Return best stock for next step'''
            new_stock = base * (1 - ((leftover_ratio)**(3/2)-aggressiveness))
            if new_stock < 0:
                new_stock = 0
            return new_stock

        optimal_stock = stockFunction(last_two_mean, leftover_stock_ratio, FACTORY_STOCK_AGRESSIVENESS)
        if optimal_stock-stock < 0:
            return 0
        else:
            return optimal_stock-stock

    #TODO fix
    @staticmethod
    def updateFactoryWorkers(workers_to_update: dict[Factory,List[Person]]):
        '''Update workers in factories'''
        for factory in Factory.all_factories:
            factory.workers = []
        for factory in workers_to_update:
            factory.workers = workers_to_update[factory]

