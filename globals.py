from __future__ import annotations
from ast import Constant
from typing import Dict, List, Literal, Tuple, TYPE_CHECKING
from numpy import log
from Factory import Factory
from Person import Person
from Markets import *

FLOATING_POINT_ERROR_MARGIN = 10**-10

#- production set as the salary necessary to produce one product -#
# one worker with 1 (unit of capital) salary produces one essential product -#
# one worker with LUXURY_PRODUCTION_COST (unit of capital) salary produces one luxury product -#
LUXURY_PRODUCION_COST: Literal = 1.5 # price relative to essencial (defined as 1)

PRODUCTION_PER_PERSON_SCALE: Literal = 1.0 #if bigger, everyone produces more

FACTORY_STOCK_AGRESSIVENESS: Literal = 0.5 #could be dynamic for every factory

#- GLOBAL FUNCTIONS -

def transfer_capital(sender: Person|Factory,capital: float,recipient: Person|Factory):
    if sender.capital < capital - FLOATING_POINT_ERROR_MARGIN:
        raise Exception("ATTEMPTED TRANSFER WITH INVALID CAPITAL")
    if type(recipient) != Factory and type(recipient) != Person:
        raise Exception("ATTEMPTED TRANSFER WITH INVALID RECIPIENT")
    if type(sender) != Factory and type(sender) != Person:
        raise Exception("ATTEMPTED TRANSFER WITH INVALID SENDER")        
    recipient.capital += capital
    sender.capital -= capital


