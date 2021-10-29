import names

def getRandomName(quantity : int):
    nameLst = list()
    for i in range(quantity):
         nameLst.append(names.get_full_name())
    return nameLst
