from __future__ import annotations
from typing import TYPE_CHECKING
from numpy import log, product

if TYPE_CHECKING:
    from typing import Dict, List
    from globals import Person, GoodsMarket, WorkersMarket, SharesMarket


class Factory:
    '''Controls production, salary payment, stockValues, and investment'''

    all_factories: List[Factory] = []
    fact_id: int = 0

    def __init__(self, product_is_essential: bool, workers: List[Person], shares: Dict[Person, float], capital: float):
        from globals import LUXURY_PRODUCION_COST, GoodsMarket

        #- Register factory -#
        self.fact_id = Factory.fact_id
        Factory.fact_id += 1
        Factory.all_factories.append(self)
        if product_is_essential:  # Is esential
            GoodsMarket.essential_factories.append(self)
            self.production_cost_per_product = 1
        else:
            GoodsMarket.luxury_factories.append(self)
            self.production_cost_per_product = LUXURY_PRODUCION_COST

        #- Capital -#
        self.capital: int = capital
        self.original_capital: int = capital  #TEST
        #-- Constants --
        self.product_is_essential: bool = product_is_essential
        #--ShareHolders----
        self.share_holders: Dict[Person, float] = shares
        for share_holder in shares:
            share_holder.share_catalog[self] = shares[share_holder]
        #--Workers----------
        self.workers: List[Person] = workers
        for worker in workers:
            worker.employer = self
        self.salary: int = capital / len(workers)
        #--Stock variables--
        self.stock: int = self.production_cost_per_product * Factory.factory_production(workers, self.salary)  # total stock
        self.last_stock: int = self.stock  # total stock last timestep
        self.avaliable_stock: int = 0  # leftover stock
        self.new_stock: int = 0  # stock created this timestep
        #--Product price---
        self.profit_margin_per_product = 0.4  #determined by leftover stock and factory aggressiveness
        self.product_price: float = (1+self.profit_margin_per_product) * (self.capital/self.stock)
        #-----------

    #--------------------------------
    #-- Functions called from main --
    #--------------------------------

    def getFunding(self, projected_capital):
        ''' Get funding by selling factory shares on the SharesMarket '''
        from globals import transfer_capital, SharesMarket

        if projected_capital > self.capital:
            #ENTER SHARESMARKET
            needed_capital = projected_capital - self.capital

            shares_to_sell = SharesMarket.share_ammount(needed_capital, self)
            if(shares_to_sell > 0.5): #Factory cannot sell more than half of itself in a single timestep
                shares_to_sell = 0.5
            if(shares_to_sell == -1): #Unless it is fully bankrupt, in that special case, a new owner will fully buy this factory
                #Factory is bankrupt (no stock and no capital)
                shares_to_sell = 1
            SharesMarket.factory_shares[self] = shares_to_sell

            #Remove needed percentage from all shareHolders
            for share_holder in self.share_holders:
                held_share = self.share_holders[share_holder]
                self.share_holders[share_holder] -= held_share * shares_to_sell
                share_holder.share_catalog[self] -= held_share * shares_to_sell

        else:
            #factory will distribute leftover capital to investors
            leftover_capital = self.capital - projected_capital
            for share_holder in self.share_holders:
                transfer_capital(self, leftover_capital*self.share_holders[share_holder], share_holder,"investor payback")

    def produce(self):
        ''' Pay salaries, create products and set price '''
        from globals import transfer_capital

        def salary():
            if len(self.workers) == 0:
                return 0
            else:
                return self.labor_avaliable_capital()/len(self.workers)

        self.salary = salary()

        #Pay salaries
        for person in self.workers:
            if person.employer != self:
                raise Exception("Factory is paying salary of a non-worker person!")
            transfer_capital(self, self.salary, person, "salary")

        #produce
        self.new_stock: int = self.production_cost_per_product * self.factory_production(self.workers, self.salary)
        self.stock = self.new_stock + self.avaliable_stock

        #Set price
        new_total_cost = self.salary * len(self.workers)
        self.profit_margin_per_product = 0.2 + (self.stock / self.avaliable_stock)
        if self.profit_margin_per_product > 2:
            self.profit_margin_per_product = 2
        if self.profit_margin_per_product < 1:
            self.profit_margin_per_product = 1
        new_stock_product_price = self.profit_margin_per_product * new_total_cost

        from globals import rho
        self.product_price = (new_stock_product_price * self.new_stock + rho * self.product_price * self.avaliable_stock)/self.stock
        self.avaliable_stock = self.stock

        #last stock is this timestep stock
        self.last_stock = self.stock

        if(self.stock == 0):
            self.product_price = 0.1

    def project_needed_capital(self):
        new_stock_projection = Factory.findNewStockValue(self.stock, self.avaliable_stock)

        return self.project_labor_capital(new_stock_projection)  #TODO + extra costs?

    #-------------------------------
    #------ General Methods --------
    #-------------------------------

    def labor_avaliable_capital(self):
        return self.capital

    def project_labor_capital(self, new_stock_proj):
        ''' project total labor cost (rough estimate) '''

        from globals import FLOATING_POINT_ERROR_MARGIN

        if new_stock_proj == 0:
            return 0

        capital_per_stock_lst = [len(f.workers)*f.salary/f.new_stock for f in Factory.all_factories if f.new_stock > 0 and len(f.workers) > 0]
        if(len(capital_per_stock_lst) == 0):  #Every factory has not produced anything
            return 1  #default wage
        average_capital_per_stock = sum(capital_per_stock_lst)/len(capital_per_stock_lst)
        if(average_capital_per_stock <= FLOATING_POINT_ERROR_MARGIN):  # Average worker is not being paid
            return 1  #default wage
        return average_capital_per_stock * new_stock_proj

    #---------------------------------------
    #------- Static Functions --------------
    #---------------------------------------

    @staticmethod
    def destroy(factory: Factory):
        from globals import transfer_capital, GoodsMarket

        final_capital = factory.capital
        for share_holder in factory.share_holders:
            #Return leftover capital to shareHolders
            transfer_capital(factory, factory.share_holders[share_holder]*final_capital/100, share_holder,"destroyed factory")
            #Delete shares from shareHolders
            share_holder.share_catalog.pop(factory)
        for worker in factory.workers:
            worker.employer = None

        Factory.all_factories.remove(factory)
        if(factory.product_is_essential):
            GoodsMarket.essential_factories.remove(factory)
        else:
            GoodsMarket.luxury_factories.remove(factory)

    @staticmethod
    def factory_production(workers: List[Person], salary: int):
        from globals import PRODUCTION_PER_PERSON_SCALE,MINIMUM_WAGE

        if salary <= MINIMUM_WAGE: #Should not happen
            return 0
        production = 0
        for person in workers:
            production += (log(salary/MINIMUM_WAGE)) * PRODUCTION_PER_PERSON_SCALE * (person.essential_satisfaction + 0.1)
        return production

    @staticmethod
    def findNewStockValue(stock: int, leftover_stock: int):
        '''Returns optimal ammount of new stock production'''
        from globals import k, FLOATING_POINT_ERROR_MARGIN

        if stock > FLOATING_POINT_ERROR_MARGIN:  # division by 0 problem
            leftover_stock_ratio = leftover_stock/stock
        else:
            return 1

        def stockFunction(leftover_ratio):
            '''Return best stock for next step'''

            from numpy import e

            if leftover_ratio == 1:
                return 1

            x = leftover_ratio/(1-leftover_ratio)

            return e**(-(x**2)/k+k)

        return stock * stockFunction(leftover_stock_ratio) + 1

    @staticmethod
    def updateFactoryWorkers(workers_to_update: dict[Factory, List[Person]]):
        '''Update workers in factories'''
        for factory in Factory.all_factories:
            factory.workers = []
            if factory in workers_to_update:
                factory.workers = workers_to_update[factory]
            workers_to_update[factory] = []
