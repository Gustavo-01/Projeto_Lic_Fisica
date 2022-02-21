import numpy as np
import time

max_number = 100
min_number = 1
decay_speed = 0.8
numbers_size = 100000

def clock_0():
    clock1 = time.time()
    numbers = np.random.normal(1/max_number, 2/(max_number**decay_speed),numbers_size)*max_number
    for i in range(0,len(numbers)):
        number = int(abs(numbers[i]))
        while number > max_number or number < min_number:
            number = np.random.normal(1/max_number, 2/(max_number**decay_speed))*max_number
        numbers[i] = number
    clock2 = time.time()
    print("TIME1 = " + str(clock2 - clock1))
    return(numbers)


def generate():
    '''Generate numbers between 0 and max_number (included)'''
    numbers = []
    if(max_number == 0):
        return [0] * numbers_size
    clock1 = time.time()
    for i in range(0,numbers_size):
        number = int(abs(int(np.random.normal(1/max_number, 2/(max_number**decay_speed))*max_number)))
        while(number > max_number or number < min_number):
            number = abs(int(np.random.normal(1/max_number, 2/(max_number**decay_speed))*max_number))
        numbers.append(number)
    clock2 = time.time()
    print("TIME1 = " + str(clock2 - clock1))
    return(numbers)
