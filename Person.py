from __future__ import annotations
from typing import TYPE_CHECKING

#from Markets import GoodsMarket, SharesMarket, WorkersMarket
if TYPE_CHECKING:
    from typing import Dict, List
    from globals import Factory#, SharesMarket, WorkersMarket, GoodsMarket


class Person:
    '''Controls consumption and maximum investment'''

    all_persons: List[Person] = []

    def __init__(self, name: str, capital: int, employer: Factory = None):
        self.name: str = name
        self.capital: int = capital
        self.original_capital: int = capital
        self.employer: Factory = employer
        self.share_catalog: Dict[Factory, float] = {}
        self.essential_satisfaction: float = 1
        self.luxury_satisfaction: float = 0.5  #if > 1, spend less on luxury, if < 0.5?, spend more
        self.timestep_initial_capital = capital
        self.LUXURY_CAPITAL_PERCENTAGE: float = 0.4  #TODO placeholder - if person filled its luxury_capital_percentage, percentage should increase
        self.__SHAREMARKET_CAPITAL_PERCENTAGE: float = 0.4  #TODO placeholder - if person could not buy any shares and, percentage should increase, if person is owner, percentage should grow slower
        Person.all_persons.append(self)

    @staticmethod
    def essential_capital_projection():
        #TODO - return capital needed to (survive?) -> minimum capital needed to enter GoodsMarket
        #Used 1 as placeholder
        return 1

    def luxury_capital_projection(self):
        ''' Calculated after essential market Timestep (essential capital already withdrawn) '''
        return self.timestep_initial_capital * self.LUXURY_CAPITAL_PERCENTAGE

    def shareMarket_capital_investment_projection(self):
        ''' Calculated after essential market Timestep (essential capital already withdrawn) '''
        return self.timestep_initial_capital * self.__SHAREMARKET_CAPITAL_PERCENTAGE

    def update_timestep_capital(self):
        '''update avaliable capital at beggining of timestep'''
        self.timestep_initial_capital = self.capital
