from __future__ import annotations
from typing import List, Literal
from Factory import Factory
from Person import Person
from Markets import GoodsMarket, SharesMarket, WorkersMarket
from numpy import e, sort
from math import isnan
import enum


rho: float = 2/3

FLOATING_POINT_ERROR_MARGIN = 10**-10

#- production set as the salary necessary to produce one product -#
# one worker with 1 (unit of capital) salary produces one essential product -#
# one worker with LUXURY_PRODUCTION_COST (unit of capital) salary produces one luxury product -#
LUXURY_PRODUCION_COST: Literal = 1  # price relative to essencial (defined as 1)

PRODUCTION_PER_PERSON_SCALE: Literal = 1 #if bigger, everyone produces more

k: Literal = 0.5  #factory aggressiveness

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
        return 0.7 * total_capital


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

def set_k(_k: float):
    global k
    k = _k

def set_rho(_rho: float):
    global rho
    rho = _rho

#-----------------
#Data collection
#-----------------

def saveState(persons: List[Person], factories: List[Factory]):

    #Initial conditions
    """
    #Gini index
    g_sum = 0
    for p_i in persons:
        for p_j in persons:
            g_sum += abs(p_i.capital-p_j.capital)
    g_sum = g_sum/(2*sum([p.capital for p in persons])*len(persons))
    
    #Mean salary
    mean_salary = WorkersMarket.meanSalary(persons)
    
    #Total stock production
    stock = sum([factory.new_stock for factory in factories])

    #Essential satisfaction
    essential_sat = sum([person.essential_satisfaction for person in persons]) / len(persons)

    #gini share index
    def share_vals(p: Person):
        return sum([SharesMarket.share_value(p.share_catalog[f],f) for f in list(p.share_catalog.keys())])
    g_sum_share = 0
    for p_i in persons:
        for p_j in persons:
            g_sum_share += abs(share_vals(p_i)-share_vals(p_j))
    g_sum_share = g_sum_share/(2*sum([share_vals(p) for p in persons])*len(persons))
    
    #Luxury satisfaction
    luxury_sat = sum([person.luxury_satisfaction for person in persons]) / len(persons)
    
    #Unemployment
    unemployment = len([p for p in Person.all_persons if p.employer == None])
    
    #luxury gini index
    g_sum_l = 0
    if sum([p.luxury_satisfaction for p in persons]) == 0:
        g_sum_l = 0
    else:
        for p_i in persons:
            for p_j in persons:
                g_sum_l += abs(p_i.luxury_satisfaction-p_j.luxury_satisfaction)
        g_sum_l = g_sum_l/(2*sum([p.luxury_satisfaction for p in persons])*len(persons))

    return [g_sum, mean_salary, stock, essential_sat, g_sum_share, luxury_sat, unemployment, g_sum_l]
    #"""
    
    # Stock detailed
    """
    #Essential
    ess_stock = sum([factory.new_stock for factory in factories if factory.product_is_essential == True])

    ess_consumption = sum([person.essential_satisfaction for person in persons])

    ess_salaries = sum([factory.salary for factory in factories if factory.product_is_essential == True])

    ess_employee_n = sum([len(factory.workers) for factory in factories if factory.product_is_essential == True])

    #Luxury
    lux_stock = sum([factory.new_stock for factory in factories if factory.product_is_essential == False])

    lux_consumption = sum([person.luxury_satisfaction for person in persons])

    lux_salaries = sum([factory.salary for factory in factories if factory.product_is_essential == False])

    lux_employee_n = sum([len(factory.workers) for factory in factories if factory.product_is_essential == False])

    return [ess_stock, lux_stock, ess_consumption, lux_consumption, ess_salaries, lux_salaries, ess_employee_n, lux_employee_n]
    #"""
    
    #Capital gini index
    """
    g_sum = 0
    for p_i in persons:
        for p_j in persons:
            g_sum += abs(p_i.capital-p_j.capital)
    g_sum = g_sum/(2*sum([p.capital for p in persons])*len(persons))
    
    return [g_sum]
    #"""

    #deep Stock
    #"""
    ess_leftover_stock = sum([factory.avaliable_stock for factory in factories if factory.product_is_essential == True])
    lux_leftover_stock = sum([factory.avaliable_stock for factory in factories if factory.product_is_essential == False])

    ess_profits = [0] * len([f for f in factories if f.product_is_essential])
    lux_profits = [0] * (len(factories) - len(ess_profits))
    i=0
    j=0
    for f in factories:
        if f.product_is_essential and not isnan(f.profit_margin_per_product):
            ess_profits[i] = f.profit_margin_per_product
            i += 1
        elif (not f.product_is_essential) and not isnan(f.profit_margin_per_product):
            lux_profits[j] = f.profit_margin_per_product
            j += 1
    ess_profit_margin = sum(ess_profits)/len(ess_profits)-1
    lux_profit_margin = sum(lux_profits)/len(lux_profits)-1

    #lux giri index
    g_sum_l = 0
    if sum([p.luxury_satisfaction for p in persons]) == 0:
        g_sum_l = 0
    else:
        for p_i in persons:
            for p_j in persons:
                g_sum_l += abs(p_i.luxury_satisfaction-p_j.luxury_satisfaction)
        g_sum_l = g_sum_l/(2*sum([p.luxury_satisfaction for p in persons])*len(persons))

    #ess giri index
    g_sum_e = 0
    if sum([p.essential_satisfaction for p in persons]) == 0:
        g_sum_e = 0
    else:
        for p_i in persons:
            for p_j in persons:
                g_sum_e += abs(p_i.essential_satisfaction-p_j.essential_satisfaction)
        g_sum_e = g_sum_e/(2*sum([p.essential_satisfaction for p in persons])*len(persons))

    return [ess_leftover_stock, lux_leftover_stock, g_sum_e, g_sum_l, ess_profit_margin, lux_profit_margin]
    #"""
    
    #Customization analysis
    """
    #Gini index
    g_sum = 0
    for p_i in persons:
        for p_j in persons:
            g_sum += abs(p_i.capital-p_j.capital)
    if (2*sum([p.capital for p in persons])*len(persons)) == 0:
        g_sum = 0
    else:
        g_sum = g_sum/(2*sum([p.capital for p in persons])*len(persons))

    
    #Mean salary
    mean_salary = WorkersMarket.meanSalary(persons)
    
    #Essential satisfaction
    essential_sat = sum([person.essential_satisfaction for person in persons]) / len(persons)
    
    #Luxury satisfaction
    luxury_sat = sum([person.luxury_satisfaction for person in persons]) / len(persons)
    
    ess_leftover_stock = sum([factory.avaliable_stock for factory in factories if factory.product_is_essential == True])
    lux_leftover_stock = sum([factory.avaliable_stock for factory in factories if factory.product_is_essential == False])
    
    ess_stock = sum([factory.new_stock for factory in factories if factory.product_is_essential == True])
    lux_stock = sum([factory.new_stock for factory in factories if factory.product_is_essential == False])
    
    return[g_sum, mean_salary, essential_sat, luxury_sat, ess_leftover_stock, lux_leftover_stock, ess_stock, lux_stock]
    #"""
    
    #No luxury analysis
    """
    #Gini index
    g_sum = 0
    for p_i in persons:
        for p_j in persons:
            g_sum += abs(p_i.capital-p_j.capital)
    g_sum = g_sum/(2*sum([p.capital for p in persons])*len(persons))
    
    #Total stock production
    stock = sum([factory.new_stock for factory in factories])
    
    #Essential satisfaction
    essential_sat = sum([person.essential_satisfaction for person in persons]) / len(persons)
    
    #luxury gini index
    g_sum_e = 0
    if sum([p.essential_satisfaction for p in persons]) == 0:
        g_sum_e = 0
    else:
        for p_i in persons:
            for p_j in persons:
                g_sum_e += abs(p_i.essential_satisfaction-p_j.essential_satisfaction)
        g_sum_e = g_sum_e/(2*sum([p.essential_satisfaction for p in persons])*len(persons))

    ess_profits = [0] * len([f for f in factories if f.product_is_essential])
    i=0
    for f in factories:
        if not isnan(f.profit_margin_per_product):
            ess_profits[i] = f.profit_margin_per_product
            i += 1

    mean_salary = WorkersMarket.meanSalary(persons)
    
    unemployment = len([p for p in Person.all_persons if p.employer == None])

    return [g_sum, g_sum_e, stock, essential_sat, mean_salary, unemployment]
    #"""
