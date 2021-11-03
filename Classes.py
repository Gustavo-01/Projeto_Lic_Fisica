from __future__ import annotations
from typing import List

from numpy import product #necessary for pyton3 version < 10.0

luxuryProducePrice = 1.5 # essencial will always be one, this will define the price relative to essencial

class Factory:
    all_factories : List[Factory] = []

    def __init__(self, owner: Person, workers: List[Person], product: bool, id: int, productivity :int = 1):
        self.id :int = id
        self.owner :Person = owner
        self.workers :List[Person] = workers
        self.product :bool = product
        self.productivity :int = productivity
        self.productAmmount :int = None
        self.salary :int= None
        self.stock : int = int(owner.capital/2)
        self.lastStock :int = self.stock
        self.avaliableStock :int = self.stock
    
    def paySalary(self, worker :Person):
        if self.owner.capital >= self.salary:
            self.owner.capital -= self.salary
            worker.capital += self.salary
        else:
            self.__fire(worker)
            #worker.capital += self.salary #?
            pass


    def produce(self):
        #Use last two stock values and leftOverStock to decide production
        lastTwoMean = self.stock + (self.lastStock - self.stock)/2

        if self.stock != 0: #division by 0 problem
            leftOverStock = self.avaliableStock/self.stock
        else:
            leftOverStock = 0

        def stockFunction(base,leftOver,aggressiveness):
            return round(base * (1 - ((leftOver)**(3/2)-aggressiveness)))

        newStockAttempt = stockFunction(lastTwoMean,leftOverStock,0.3)

        if newStockAttempt <= 0: #Factory is not selling at all
            pass
        self.newStockAttempt = newStockAttempt
        pass

    def __fire(self,person :Person):
        person.employer = None

    def invest(self,maxAmmount: int):
        if(maxAmmount > self.newStockAttempt):        
            investment = self.newStockAttempt
        else:
            investment = maxAmmount
        self.stock = investment * (luxuryProducePrice * self.product)  # will add to production price if is not essencial
        return investment

    

class Person:
    all_persons :List[Person] = []
    def __init__(self, name: str, capital: int,employer: Person = None, ownedFactory:Factory = None):
        self.name :str = name
        self.capital :int = capital
        self.employer :Person = employer
        self.ownedFactory :Factory = ownedFactory

    def __consume_ess(self):
        #trade with factories
        print("traded essential")

    def __consume_lux(self):
        #trade with factories
        print("invested")

    def consume(self):
        self.__consume_ess()
        if(self.ownedFactory != None): #is a factory owner
            self.capital -= self.ownedFactory.invest(self.capital*0.8) #Will invest up to 80% of remaining wealth
        self.__consume_lux()


