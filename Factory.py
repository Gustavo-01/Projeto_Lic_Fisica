from __future__ import annotations
from typing import TYPE_CHECKING
from numpy import log

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
            GoodsMarket.essencial_factories.append(self)
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
        self.stock: int = self.production_cost_per_product * Factory.production_per_worker(self.salary) * len(workers)  # total stock
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
        from globals import transfer_capital, SharesMarket, FLOATING_POINT_ERROR_MARGIN

        if projected_capital > self.capital:
            #ENTER SHARESMARKET
            needed_capital = projected_capital - self.capital

            #Factory cannot sell more than half of itself in a single timestep
            if(needed_capital > self.capital / 2 + 1):
                needed_capital = self.capital / 2 + 1
            shares_to_sell = SharesMarket.share_ammount(needed_capital, self)
            if(shares_to_sell > 1):
                shares_to_sell = 0
            if(shares_to_sell == -1):
                #Factory is bankrupt (no stock and no capital)
                shares_to_sell = 1
            from math import isnan #TODO DELETE
            if isnan(float(shares_to_sell)):
                pass
                shares_to_sell = SharesMarket.share_ammount(needed_capital, self)
                pass
            SharesMarket.factory_shares[self] = shares_to_sell

            #Remove needed percentage from all shareHolders
            for share_holder in self.share_holders:
                held_share = self.share_holders[share_holder]
                self.share_holders[share_holder] -= held_share * shares_to_sell
                share_holder.share_catalog[self] -= held_share * shares_to_sell

        elif self.capital > projected_capital:
            #factory will distribute leftover capital to investors
            leftover_capital = self.capital - projected_capital
            for share_holder in self.share_holders:
                transfer_capital(self, leftover_capital*self.share_holders[share_holder], share_holder,"investor payback")

    def produce(self):
        ''' Pay salaries, create products and set price '''
        from globals import transfer_capital, FACTORY_STOCK_AGRESSIVENESS

        def salary():
            if len(self.workers) == 0:
                return 0
            else:
                return self.labor_avaliable_capital()/len(self.workers)

        #last stock is this timestep stock
        self.last_stock = self.stock

        self.salary = salary()

        #Pay salaries
        for person in self.workers:
            if person.employer != self:
                raise Exception("Factory is paying salary of a non-worker person!")
            transfer_capital(self, self.salary, person, "salary")

        #produce
        self.new_stock: int = self.production_cost_per_product * self.production_per_worker(self.salary) * len(self.workers)
        self.stock = self.new_stock + self.avaliable_stock
        self.avaliable_stock = self.stock

        #Set price
        new_total_cost = self.salary * len(self.workers)
        self.profit_margin_per_product = FACTORY_STOCK_AGRESSIVENESS/10 * (self.avaliable_stock / self.last_stock)
        if(self.avaliable_stock == 0 or self.last_stock == 0):
            self.profit_margin_per_product = 0

        new_stock_product_price = (1+self.profit_margin_per_product) * new_total_cost
        self.product_price = (new_stock_product_price * self.new_stock + self.product_price * self.stock)/(self.new_stock + self.stock)
        if(self.new_stock + self.stock == 0):
            self.product_price = 0

    def project_needed_capital(self):
        new_stock_projection = Factory.findNewStockValue(self.stock, self.last_stock, self.avaliable_stock)

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

        salary_per_stock_lst = [f.salary/f.new_stock for f in Factory.all_factories if f.new_stock > 0 and len(f.workers) > 0]
        if(len(salary_per_stock_lst) == 0):  #Every factory has not produced anything
            return 1  #default wage
        average_salary_per_stock = sum(salary_per_stock_lst)/len(salary_per_stock_lst)
        if(average_salary_per_stock <= FLOATING_POINT_ERROR_MARGIN):  # Average worker is not being paid
            return 1  #default wage
        return average_salary_per_stock * new_stock_proj

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
            GoodsMarket.essencial_factories.remove(factory)
        else:
            GoodsMarket.luxury_factories.remove(factory)

    @staticmethod
    def production_per_worker(salary: int):
        from globals import PRODUCTION_PER_PERSON_SCALE,MINIMUM_WAGE

        if salary <= MINIMUM_WAGE: #Should not happen
            return 0
        return (log(salary/MINIMUM_WAGE)) * PRODUCTION_PER_PERSON_SCALE

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

            from numpy import e

            if leftover_ratio == 1:
                return 10

            x = leftover_ratio/(1-leftover_ratio)

            #examples: (aggressiveness = 0.5)
            # leftover_ratio = 0 -> new_stock ≃ 1.6*stock
            # leftover_ratio = 0.5 -> new_stock = stock
            # leftover_ratio = 0.9 -> new_stock = 4E-18 * stock ≃ 0
            return base * e**(-0.5*(x**2)+aggressiveness) + 10

        return stockFunction(last_two_mean, leftover_stock_ratio, FACTORY_STOCK_AGRESSIVENESS)

    @staticmethod
    def updateFactoryWorkers(workers_to_update: dict[Factory, List[Person]]):
        '''Update workers in factories'''
        for factory in Factory.all_factories:
            factory.workers = []
            if factory in workers_to_update:
                factory.workers = workers_to_update[factory]
            workers_to_update[factory] = []
