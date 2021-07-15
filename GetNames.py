import requests

def getRandomName(quantity):
    URL = "http://names.drycodes.com/"+str(quantity)+"?nameOptions=boy_names"
    response = requests.get(URL)
    responseLst = eval(response.content.decode("utf-8"))
    return(responseLst)
