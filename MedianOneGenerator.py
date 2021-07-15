import numpy as np
import matplotlib.pyplot as pyplot

def generate(max_number,numbers_size):
    numbers = []
    for i in range(0,numbers_size):
        numbers.append(abs(round(np.random.normal(1/max_number, 2/(max_number**0.8))*max_number)))
    return numbers

def testGenerator(max_number,numbers_size):
    numbers = []
    for i in range(0,numbers_size):
        numbers.append(abs(round(np.random.normal(1/max_number, 2/(max_number**0.8))*max_number)))
    occurrences = []
    for i in range(0,max(numbers)):
        occurrences.append(numbers.count(i))
    pyplot.plot(range(0,max(numbers)),occurrences)
    pyplot.show()
    print("done")

#testGenerator(900,1000000)