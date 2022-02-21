from random import Random
import numpy as np
import matplotlib.pyplot as pyplot

def medianOneGenerate(max_number,numbers_size,decay_speed = 0.8, min_number = 0):
    '''Generate numbers between 0 and max_number (included)'''
    if(max_number == 0):
        return [0] * numbers_size
    if max_number <= min_number:
        raise Exception("Generating impossible numbers")
    numbers = np.random.normal(1/max_number, 2/(max_number**decay_speed),numbers_size)*max_number
    for i in range(0,len(numbers)):
        number = int(abs(numbers[i]))
        while number > max_number or number < min_number:
            number = abs(int(np.random.normal(1/max_number, 2/(max_number**decay_speed))*max_number))
        numbers[i] = int(number)
    return numbers.astype(int)

def uniformGenerate(max_number,numbers_size, min_number = 0, int_return = True, repetition: bool = True):
    '''Generate numbers between 0 and max_number (included)'''
    if max_number < min_number:
        raise Exception("Generating impossible numbers")
    numbers = np.random.uniform(min_number,max_number+1,numbers_size)
    if(int_return):
        numbers = numbers.astype(int)
        if not repetition:
            numbers = np.unique(numbers)
            needed = numbers_size - len(numbers)
            while needed > 0:
                numbers2 = np.random.uniform(min_number,max_number+1,needed).astype(int)
                numbers = np.unique(np.append(numbers,numbers2))
                needed = numbers_size - len(numbers)
        return numbers
    else:
        return numbers


def plot_occurrences(numbers: np.ndarray):
    occurrences = []
    for i in range(0,np.amax(numbers)):
        occurrences.append(np.count_nonzero(numbers == i))
    pyplot.plot(range(0,max(numbers)),occurrences)
    pyplot.show()

def testGenerator(max_number,numbers_size):
    numbers = medianOneGenerate(max_number,numbers_size)
    plot_occurrences(numbers)


#testGenerator(10,1000)