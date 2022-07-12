from __future__ import annotations
from typing import List, Literal
from Factory import Factory
from Person import Person
from Markets import GoodsMarket, SharesMarket, WorkersMarket
from numpy import e

FLOATING_POINT_ERROR_MARGIN = 10**-10

#- production set as the salary necessary to produce one product -#
# one worker with 1 (unit of capital) salary produces one essential product -#
# one worker with LUXURY_PRODUCTION_COST (unit of capital) salary produces one luxury product -#
LUXURY_PRODUCION_COST: Literal = 1.5  # price relative to essencial (defined as 1)

PRODUCTION_PER_PERSON_SCALE: Literal = 1.0  #if bigger, everyone produces more

FACTORY_STOCK_AGRESSIVENESS: Literal = 1.5  #could be dynamic for every factory

MINIMUM_WAGE: Literal = 1/e #Workers will not join a factory if the wage is lower than this value

#- GLOBAL FUNCTIONS -


def transfer_capital(sender: Person | Factory, capital: float, recipient: Person | Factory,desctiption: str):
    if sender.capital < capital - FLOATING_POINT_ERROR_MARGIN:
        raise Exception("ATTEMPTED TRANSFER WITH INVALID CAPITAL")
    if type(recipient) != Factory and type(recipient) != Person:
        raise Exception("ATTEMPTED TRANSFER WITH INVALID RECIPIENT")
    if type(sender) != Factory and type(sender) != Person:
        raise Exception("ATTEMPTED TRANSFER WITH INVALID SENDER")
    recipient.capital += capital
    sender.capital -= capital
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
        break