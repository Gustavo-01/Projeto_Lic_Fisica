import numpy as np
import matplotlib.pyplot as pyplot

def generate(max_number,numbers_size):
    numbers = []
    for i in range(0,numbers_size):
        numbers.append(abs(round(np.random.normal(1/max_number, 2/max_number)*max_number)))
    return numbers
