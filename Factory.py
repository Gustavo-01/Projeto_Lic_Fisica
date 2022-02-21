from __future__ import annotations
from typing import TYPE_CHECKING
from numpy import log
if TYPE_CHECKING:
    from typing import Dict, List, Tuple
    from globals import Person, GoodsMarket, WorkersMarket, SharesMarket

class Factory:
    '''Controls production, salary payment, stockValues, and investment'''
    
    all_factories: List[Factory] = []
    __idcounter__ :int = 0

    def __init__(self, product_is_essential: bool, workers: List[Person], shareHolders: Dict[Person,float], capital :float):
        from globals import GoodsMarket, productProductivityCost

        self.fact_id: int = Factory.__idcounter__
        Factory.__idcounter__+=1

        self.capital: int = capital
        self.product_is_essential: bool = product_is_essential
        #--ShareHolders----
        self.share_holders = shareHolders
        for shareHolder in shareHolders:
            shareHolder.share_catalog[self] = shareHolders[shareHolder]
        #--Workers----------
        self.workers: List[Person] = workers
        for worker in workers:
            worker.employer = self
        self.salary: int = len(self.workers) * productProductivityCost(product_is_essential)
        self.product_price: float = (self.salary * len(self.workers))
        #--Stock_variables--
        self.stock: int = capital/2
        self.last_stock: int = self.stock
        self.avaliable_stock: int = self.stock
        self.new_stock_value:int = None
        #-----------
        self.profit_margin_per_product = 0.1 #determined by leftover stock and factory aggressiveness
        #-----------
        if product_is_essential:  # Is esential
            GoodsMarket.essencial_factories.append(self)
        else:
            GoodsMarket.luxury_factories.append(self)
        
        Factory.all_factories.append(self)

    #--------------------------------
    #-- Functions called from main --
    #--------------------------------

    def analyzeMarket(self):
        ''' Find new stock value '''
        from globals import FACTORY_STOCK_AGRESSIVENESS

        self.new_stock_value = Factory.findNewStockValue(self.stock,self.last_stock,self.avaliable_stock)
        self.profit_margin_per_product = (self.stock - self.last_stock) * (FACTORY_STOCK_AGRESSIVENESS/self.stock)

    def getFunding(self):
        ''' Get funding from owner or put factory shares on the SharesMarket '''
        from globals import SharesMarket, transfer_capital

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
        from globals import transfer_capital,productProductivityCost

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
        from globals import productProductivityCost

        stock_to_produce = self.new_stock_value-self.avaliable_stock
        if stock_to_produce < 0:
            stock_to_produce = 0
        needed_productivity: float = stock_to_produce * productProductivityCost(self.product_is_essential)
        return needed_productivity

    def project_salary(self, needed_productivity, test_mode):
        ''' Define new projected salary (attract more workers if bigger salary) '''
        from globals import productProductivityCost

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
        from globals import PRODUCTION_PER_PERSON_SCALE

        if salary is None :
            salary=0
        return log((salary+1)) * 50 * PRODUCTION_PER_PERSON_SCALE

    @staticmethod
    def salary_with_productivity(N: int, productivity: float):
        from globals import PRODUCTION_PER_PERSON_SCALE

        #N must be > 0
        exp = productivity/(N * PRODUCTION_PER_PERSON_SCALE * 50)
        return 10**(exp) -1

    @staticmethod
    def findNewStockValue(stock: int, last_stock: int, leftover_stock: int):
        from globals import FACTORY_STOCK_AGRESSIVENESS

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
        from globals import Person,productProductivityCost

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