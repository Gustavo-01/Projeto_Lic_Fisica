from __future__ import annotations
from typing import TYPE_CHECKING

from Markets import GoodsMarket, SharesMarket, WorkersMarket
if TYPE_CHECKING:
    from typing import Dict, List, Tuple
    from globals import Factory, SharesMarket, WorkersMarket, GoodsMarket


class Person:
    '''Controls consumption and maximum investment'''

    all_persons: List[Person] = []

    def __init__(self, name: str, capital: int, employer: Factory = None):
        self.name: str = name
        self.capital: int = capital
        self.employer: Factory = employer
        self.owned_factories: List[Factory] = []
        self.share_catalog: Dict[Factory,float] = {}
        self.LUXURY_CAPITAL_PERCENTAGE :float = 0.01 #TODO placeholder - if person filled its luxury_capital_percentage, percentage should increase
        self.SHAREMARKET_CAPITAL_PERCENTAGE :float = 0.01 #TODO placeholder - if person could not buy any shares and, percentage should increase, if person is owner, percentage should grow slower
        Person.all_persons.append(self)

    @staticmethod
    def essential_capital_projection():
        #TODO - return capital needed to (survive?) -> minimum capital needed to enter GoodsMarket
        #Used 1 as placeholder
        return 1

    def luxury_capital_projection(self):
        ''' Calculated after essential market Timestep (essential capital already withdrawn) '''
        return self.capital * self.LUXURY_CAPITAL_PERCENTAGE

    def shareMarket_capital_investment_projection(self):
        ''' Calculated after essential market Timestep (essential capital already withdrawn) '''
        return self.capital * self.SHAREMARKET_CAPITAL_PERCENTAGE

    def factory_capital_investment_projection(self):
        ''' capital avaliable  '''
        return self.capital - (self.luxury_capital_projection() + self.shareMarket_capital_investment_projection())

    def max_capital_investment_per_factory(self):
        #TODO test this
        if len(self.owned_factories) > 0:
            return self.factory_capital_investment_projection()/len(self.owned_factories)
        else:
            return 0