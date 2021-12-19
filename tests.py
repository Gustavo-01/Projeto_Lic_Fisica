"""

cte = 1

def F(x: float):
    return log((x+1)) * 50

def d_F(x: float):
    return 50/(log(x)*(x+1))

def d_d_F(x: float):
    return -(50*(x+1+x*log(x)))/(x*(log(x)**2)*(x+1)**2)

def f(x: float):
    return cte * x/F(x)
    
def d_f(x: float):
    return (F(x) - d_F(x)*x)/(F(x))**2

def d_d_f(x: float):
    return ((x*d_d_F(x)*F(x))+(2*d_F(x))*(-x*d_F(x)+F(x)))/(F(x)**3)

def main(x0: float, max_iter: int, epsilon: float):
    xn = x0
    for n in range(0,max_iter):
        fxn = d_f(xn)
        if abs(fxn) < epsilon:
            print('Found solution after',n,'iterations.')
            return xn
        d_fxn = d_d_f(xn)
        if d_fxn == 0:
            print('Zero derivative. No solution found.')
            return None
        xn = xn - fxn/d_fxn
    print('Exceeded maximum iterations. No solution found.')

while(True):
    x0 = input("x0: ")
    max_iter = input("M_iter: ")
    epsilon = input("epsilon: ")
    main(float(x0),int(max_iter),float(epsilon))
"""

from numpy import log

def F(x: float):
    return log((x+1)) * 50

def findSalaryWithApha(apha, c):
    return 10**(c/apha) - 1
"""
def findMinimum(apha,c):
    if(apha == 1):
        apha0 = apha
    else:
        apha0 = round(apha/2)
    apha1 = 2*apha
    
    cost0 = round(findSalaryWithApha(apha0,c)) * apha0
    cost = round(findSalaryWithApha(apha,c)) * apha
    cost1 = round(findSalaryWithApha(apha1,c)) * apha1
    
    print(apha0,apha,apha1)
    print(round(cost0),round(cost),round(cost1))
    
    return
    if(cost0 > cost and cost1 > cost): #Break Condition
        return cost
    elif(cost0 < cost):
        findMinimum(apha0,c)
    else:
        findMinimum(apha1,c)


OG_APHA = 5
DELTAP_NF = 12
findMinimum(OG_APHA,DELTAP_NF)
"""