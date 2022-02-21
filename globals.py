from __future__ import annotations
from typing import Dict, List, Tuple, TYPE_CHECKING
from numpy import log
from Factory import Factory
from Person import Person
from Markets import *

LUXURY_PRODUCION_COST_MULTIPLIER: float = 1.5 # essencial will always be one, this will define the price relative to essencial

PRODUCTION_PER_PERSON_SCALE: float = 1.0
PRODUCTION_PER_PRODUCT: float = 1.0

FACTORY_STOCK_AGRESSIVENESS: float = 0.3 #could be dynamic for every factory

#- GLOBAL FUNCTIONS -

def transfer_capital(sender: Person|Factory,capital: float,recipient: Person|Factory):
    if sender.capital < capital:
        raise Exception("ATTEMPTED TRANSFER WITH INVALID CAPITAL")
    if type(recipient) != Factory and type(recipient) != Person:
        raise Exception("ATTEMPTED TRANSFER WITH INVALID RECIPIENT")
    if type(sender) != Factory and type(sender) != Person:
        raise Exception("ATTEMPTED TRANSFER WITH INVALID SENDER")        
    recipient.capital += capital
    sender.capital -= capital

def productProductivityCost(is_essential: bool):
    cost = PRODUCTION_PER_PRODUCT
    if is_essential:
        cost *= LUXURY_PRODUCION_COST_MULTIPLIER
    return cost

