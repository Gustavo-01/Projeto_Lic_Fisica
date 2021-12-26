import numpy as np
import matplotlib.pyplot as pyplot

def generate(max_number,numbers_size,decay_speed = 0.8):
    numbers = []
    for i in range(0,numbers_size):
        number = abs(int(np.random.normal(1/max_number, 2/(max_number**decay_speed))*max_number))
        while(number > max_number):
            number = abs(int(np.random.normal(1/max_number, 2/(max_number**decay_speed))*max_number))
        numbers.append(number)
    return numbers

def plot_occurrences(numbers):
    occurrences = []
    for i in range(0,max(numbers)):
        occurrences.append(numbers.count(i))
    pyplot.plot(range(0,max(numbers)),occurrences)
    pyplot.show()

def testGenerator(max_number,numbers_size):
    numbers = generate(max_number,numbers_size)
    plot_occurrences(numbers)

#testGenerator(10,1000)