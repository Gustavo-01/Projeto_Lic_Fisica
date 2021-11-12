from __future__ import annotations
from typing import List
from numpy import log

# necessary for pyton3 version < 10.0

# essencial will always be one, this will define the price relative to essencial
luxuryProducePrice = 1.5


class Factory:
    all_factories: List[Factory] = []

    def __init__(self, owner: Person, workers: List[Person], product: bool, id: int, productivity: int = 1):
        self.id: int = id
        self.owner: Person = owner
        self.workers: List[Person] = workers
        self.product: bool = product
        self.productivity: int = productivity
        self.productAmmount: int = None
        self.salary: int = None
        self.stock: int = int(owner.capital/2)
        self.lastStock: int = self.stock
        self.avaliableStock: int = self.stock
        self.avaliableProductivity = self.__calculateAvaliableProductivity()

        if(product):  # Is esential
            GoodsMarket.essencial_factories.append(self)
        else:
            GoodsMarket.luxury_factories.append(self)

    #--Important-- Will determine how productive every person is 
    def __calculateAvaliableProductivity(self):
        def productivity_with_salary(salary :int) -> int:
            return log(salary+1) * 50

        producivity = 10 + self.salary * len(self.workers) #Base productivity from owner is 10
        return producivity


    def paySalary(self, worker: Person):
        if self.owner.capital >= self.salary:
            self.owner.capital -= self.salary
            worker.capital += self.salary
        else:
            self.__fire(worker)
            # worker.capital += self.salary #?
            pass

    #--Production--#

    def __findNewStockValue(self, stock: int, lastStock: int, avaliableStock: int) -> int:
        # Use last two stock values and leftOverStock to decide production
        lastTwoMean = stock + (lastStock - stock)/2

        if stock != 0:  # division by 0 problem
            leftOverStock = avaliableStock/stock
        else:
            leftOverStock = 0

        def stockFunction(base, leftOver, aggressiveness) -> int:
            return round(base * (1 - ((leftOver)**(3/2)-aggressiveness)))

        return stockFunction(lastTwoMean, leftOverStock, 0.3)

    def produce(self):

        newStockAttempt = self.__findNewStockValue(self.stock, self.lastStock, self.avaliableStock)
        if newStockAttempt <= 0:  # Factory is not selling at all
            pass
        if(newStockAttempt > self.avaliableProductivity):
            #TODO
            pass

    def __fire(self, person: Person):
        person.employer = None

    def invest(self, maxAmmount: int):
        if(maxAmmount > self.newStockAttempt):
            investment = self.newStockAttempt
        else:
            investment = maxAmmount
        # will add to production price if is not essencial
        self.stock = investment * (luxuryProducePrice * self.product)
        return investment


class Person:
    all_persons: List[Person] = []

    def __init__(self, name: str, capital: int, employer: Person = None, ownedFactory: Factory = None):
        self.name: str = name
        self.capital: int = capital
        self.employer: Person = employer
        self.ownedFactory: Factory = ownedFactory

    def __consume_ess(self):
        # trade with factories
        print("traded essential")

    def __consume_lux(self):
        # trade with factories
        print("invested")

    def consume(self):
        self.__consume_ess()
        if(self.ownedFactory != None):  # is a factory owner
            # Will invest up to 80% of remaining wealth
            self.capital -= self.ownedFactory.invest(self.capital*0.8)
        self.__consume_lux()


class GoodsMarket():
    essencial_factories: List[Factory]
    luxury_factories: List[Factory]
