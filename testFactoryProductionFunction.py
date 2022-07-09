
def step(rest, lastStock, stock):
    lastTwoMean = stock + ((lastStock - stock)/2)
    print("lastStock: " + str(lastStock))
    print("stock: " + str(stock))
    print("lastTwoMean: " + str(lastTwoMean))
    if stock == 0:
        leftOverStock = 0
    else:
        leftOverStock = rest/stock
    newStockAttempt = round(lastTwoMean * (1 - ((leftOverStock)**(3/2)-0.3)))
    print("newStock: " + str(newStockAttempt))
    print("-------------------")
    rest = round(int(input("rest?: ")))
    print("-------------------")
    step(rest, stock, newStockAttempt)


step(0, 5, 0)
