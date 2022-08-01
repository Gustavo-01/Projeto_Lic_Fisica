import numpy as np
import matplotlib.pyplot as plt

max_number = 100
min_number = 1
decay_speed = 0.8
numbers_size = 100000


def medianOneGenerate(max_number, numbers_size, decay_speed=0.8, min_number=0):
    '''Generate numbers between 0 and max_number (included)'''
    if(max_number == 0):
        return [0] * numbers_size
    if max_number <= min_number:
        raise Exception("Generating impossible numbers")
    numbers = np.random.normal(1/max_number, 2/(max_number**decay_speed), numbers_size)*max_number
    for i in range(0,len(numbers)):
        number = int(abs(numbers[i]))
        while number > max_number or number < min_number:
            number = abs(int(np.random.normal(1/max_number, 2/(max_number**decay_speed))*max_number))
        numbers[i] = int(number)
    return numbers.astype(int)

from numpy import log, linspace, e

"""
n = 20
Max = 100
l = list(medianOneGenerate(Max,n,min_number=1))
occurrences = []
for i in range(0,max(l)):
    occurrences.append(l.count(i))

"""
"""
Min = 1/e
print(Min)
X = linspace(0.1,5,num=1000)
Y=[]
for x in X:
    y = log(x/Min)
    if y <= 0:
        y = 0
    Y.append(y)
plt.plot(X,Y)
plt.plot(X,0*X,'k--')
plt.plot((Min, Min), (log(0.1*e), log(10*e)), 'k--')
plt.xlabel('Salary')
plt.ylabel('Production')
plt.title('Worker productivity')
plt.show()
"""
#"""
X = np.linspace(0,5,10000)
k=0.5
Y = e**(-(X**2)/k+k)
plt.plot(X,Y)
plt.plot([0,5],[0,0],'k--')
plt.xlabel('stock ratio')
plt.ylabel('production/stock')
plt.title('production estimation')
plt.show()
#"""
"""
X = np.linspace(0,100,10000)
Y = (1-0.4)*(1-(1/(X+1.4)))
plt.plot(X,Y)
plt.plot([0,100],[0.6,0.6],'k--')
plt.xlabel('luxury consumed')
plt.ylabel('production projection')
plt.title('production estimation')
plt.show()
"""