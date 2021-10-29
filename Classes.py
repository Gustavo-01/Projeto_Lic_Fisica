from typing import List

class Person:
    pass

class Factory:
    all_factories = []
    def __init__(self,owner: Person,workers: List[Person],product: bool ,id: int):
        self.id = id
        self.owner = owner
        self.workers = workers
        self.product = product

class Person:
    all_persons = []
    def __init__(self, name: str, capital: int,employer: Person = None, ownedFactory:Factory = None):
        self.name = name
        self.capital = capital
        self.employer = employer
        self.ownedFactory = ownedFactory