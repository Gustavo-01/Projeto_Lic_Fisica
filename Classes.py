class Factory:
    all_factories = []
    def __init__(self,owner,workers,product,id):
        self.id = id
        self.owner = owner
        self.workers = workers
        self.product = product

class Person:
    all_persons = []
    def __init__(self, name, capital,employer=None,ownedFactory=None):
        self.name = name
        self.capital = capital
        self.employer = employer
        self.ownedFactory = ownedFactory