from __future__ import annotations
from typing import List, Literal
from Factory import Factory
from Person import Person
from Markets import GoodsMarket, SharesMarket, WorkersMarket
from numpy import e, sort
import enum


rho: float = 2/3

FLOATING_POINT_ERROR_MARGIN = 10**-10

#- production set as the salary necessary to produce one product -#
# one worker with 1 (unit of capital) salary produces one essential product -#
# one worker with LUXURY_PRODUCTION_COST (unit of capital) salary produces one luxury product -#
LUXURY_PRODUCION_COST: Literal = 1  # price relative to essencial (defined as 1)

PRODUCTION_PER_PERSON_SCALE: Literal = 1.2 #if bigger, everyone produces more

FACTORY_STOCK_AGRESSIVENESS: Literal = 0.5  #could be dynamic for every factory

MINIMUM_WAGE: Literal = 1/e #Workers will not join a factory if the wage is lower than this value

#- Government variables -#


class Gov(enum.Enum):
    NONE = 1
    TRANSATION = 2
    WEALTH_CAP = 3
    BOTH = 4


class Government():
    type = Gov.NONE
    raised_capital = 0
    transation_tax_rate = 0.1

    @staticmethod
    def wealth_cap(persons: List[Person]):
        total_capital = sum([p.capital for p in persons]) + sum([f.capital for f in Factory.all_factories])
        return 4 * total_capital / len(persons)


def act_government(persons: List[Person]):
    if Government.type == Gov.NONE:
        return

    if Government.type == Gov.WEALTH_CAP or Government.type == Gov.BOTH:

        def distribute(capital):
            for p in persons:
                p.capital += capital/len(persons)

        wealth_cap = Government.wealth_cap(persons)
        for p in Person.all_persons:
            if p.capital > wealth_cap:
                capital = p.capital - wealth_cap
                p.capital = wealth_cap
                distribute(capital)

    if Government.type == Gov.TRANSATION or Government.type == Gov.BOTH:

        raised_capital = Government.raised_capital
        for p in Person.all_persons:
            p.capital += raised_capital / len(Person.all_persons)
        Government.raised_capital = 0

#- GLOBAL FUNCTIONS -

def transfer_capital(sender: Person | Factory, capital: float, recipient: Person | Factory,desctiption: str):
    if sender.capital < capital - FLOATING_POINT_ERROR_MARGIN:
        raise Exception("ATTEMPTED TRANSFER WITH INVALID CAPITAL")
    if type(recipient) != Factory and type(recipient) != Person:
        raise Exception("ATTEMPTED TRANSFER WITH INVALID RECIPIENT")
    if type(sender) != Factory and type(sender) != Person:
        raise Exception("ATTEMPTED TRANSFER WITH INVALID SENDER")
    sender.capital -= capital
    if Government.type == Gov.TRANSATION or Government.type == Gov.BOTH:
        Government.raised_capital += capital * Government.transation_tax_rate
        capital = capital * (1-Government.transation_tax_rate)
    recipient.capital += capital
    if(sender.capital < 0):
        sender.capital = 0  #if capital is negative but smaller than FLOATING_POINT_ERROR_MARGIN - set it to 0


def cleanup(persons: List[Person], factories: List[Factory]):
    for shareholder in [person for person in persons if len(person.share_catalog) > 0]:
        for factory, share in shareholder.share_catalog.items():
            if share < FLOATING_POINT_ERROR_MARGIN:
                shareholder.share_catalog.pop(factory)
                factory.share_holders.pop(shareholder)
                newSum = sum(factory.share_holders.values())
                for person, value in factory.share_holders.items():
                    person.share_catalog[factory] = value/newSum
                    factory.share_holders[person] = value/newSum
                break
    for factory in [factory for factory in factories if sum(factory.share_holders.values()) > 1 + FLOATING_POINT_ERROR_MARGIN or sum(factory.share_holders.values()) < 1 - FLOATING_POINT_ERROR_MARGIN]:
        total = sum(factory.share_holders.values())
        for person, value in factory.share_holders.items():
            person.share_catalog[factory] = value/total
            factory.share_holders[person] = value/total

#-----------------
#Data collection
#-----------------

def saveState(persons: List[Person], factories: List[Factory]):
    #Inequality: capital of top 50% - capital of bottom 50%
    #capitals = sort([person.capital for person in persons])
    #top50 = sum(capitals[round(len(capitals)/2):])
    #bot50 = sum(capitals[:round(len(capitals)/2)])
    
    #Total stock production
    #stock = sum([factory.stock for factory in factories])
    
    #Essential satisfaction
    #essential_sat = sum([person.essential_satisfaction for person in persons]) / len(persons)
    
    #Luxury satisfaction
    #luxury_sat = sum([person.luxury_satisfaction for person in persons]) / len(persons)

    
    """Diferent plot"""

    #Mean salary
    mean_salary = WorkersMarket.meanSalary(persons)

    #Unemployment
    unemployment = len([p for p in Person.all_persons if p.employer == None])

    #Monopoly percentage
    share_vals = [sum(list(p.share_catalog.values())) for p in Person.all_persons]
    monopoly_p = max(share_vals) / sum(share_vals)

    #capital / person !DIFERENT PLOT


    #return [(top50 - bot50)/sum(capitals), stock,essential_sat, luxury_sat]
    return [unemployment,monopoly_p,mean_salary]

