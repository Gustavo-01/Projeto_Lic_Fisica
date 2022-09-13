from __future__ import annotations
from typing import Dict, List, Tuple

from matplotlib import pyplot as plt

from globals import Person, Factory, GoodsMarket, SharesMarket, WorkersMarket

def printPersonsAndFactories(all_persons: List[Person], all_factories: List[Factory], day: int = 0, f: TextIO = None):
    f.write("\n\n")
    f.write("\n\n")
    f.write("\t"*3 + "day:{:<20d}".format(day) + "\n")
    f.write("\n\n")
    f.write("\n\n")
    f.write("PERSONS\n")
    f.write("{0:<25s} - {1:<10s} - {2:<4s} - {3:<6s} - {4:<6s} \n".format("Name", "Capital", "Employed", "Ess_sat", "Lux_sat"))
    f.write("-"*50 + "\n")
    for person in sorted(all_persons, key=lambda p: p.name):
        employed = "None"
        if(person.employer is not None):
            employed = str(person.employer.fact_id)
        f.write("{0:<25s} - {1:>10.2f}$ - {2:<4s} - {3:>5.0f}% - {4:>5.0f}% \n".format(
            person.name, person.capital, employed, person.essential_satisfaction*100, person.luxury_satisfaction*100))
    f.write("\n")
    f.write("-FACTORIES-\n")
    f.write("{0:<3s} - {1:<6s} - {2:<4s} - {3:>10s}  - {4:>7s} - {5:>7s} - {6:>5s} - {7:>2s} - {8:>4s} \n".format(
        "ID", "Essen", "Wok.", "Salary", "left_stk", "new_stk", "price", "profit", "share_val"))
    f.write("-"*80 + "\n")
    for factory in sorted(all_factories, key=lambda f: f.fact_id):
        f.write("{0:<3d} - {1:<6s} - {2:<4d} - {3:>10.2f}$ - {4:>7.2f} - {5:>7.2f} - {6:>5.2f} - {7:>2.0f}% - {8:<4.2f}$ \n".format(
            factory.fact_id, str(factory.product_is_essential), len(factory.workers), factory.salary, factory.avaliable_stock,
            factory.new_stock, factory.product_price, (factory.profit_margin_per_product-1) * 100, SharesMarket.share_value(1, factory)))
    f.write("\n\n")

def process_state(state: List[List[float]],cycle_n: int):
    days: List[int] = []
    vals_n: int = len(state[0])
    vals: List[List[float]] = [None] * vals_n
    for i in range(vals_n):
        vals[i] = [None] * len(state)
    for i in range(len(state)):
        days.append(i*cycle_n/200)
        for j in range(len(state[i])):
            vals[j][i] = state[i][j]
    return(days, vals)

def process_multistate(runs: Tuple[List[int]],cycle_n):
    days_n = len(runs[0][0])
    runs_n = len(runs)
    all_lines:List[List[float]] = [None] * days_n
    for x in range(0,days_n):
        runs_lines = [None] * runs_n
        run_i = 0
        for run in runs:
            run_state = run[1]
            run_lines = [None] * len(run[1])
            line_i = 0
            for line in run_state:
                run_lines[line_i] = line[x]
                line_i += 1
            runs_lines[run_i] = run_lines
            run_i += 1
        all_lines[x] = [None] * len(run[1])
        line_i = 0
        for line in all_lines[x]:
            all_lines[x][line_i] = [None] * runs_n
            line_i+=1
        line_i = 0
        for line in all_lines[x]:
            run_i = 0
            for run_lines in runs_lines:
                all_lines[x][line_i][run_i] = run_lines[line_i]
                run_i += 1
            line_i += 1
        for line_i in range(0,len(all_lines[x])):
            all_lines[x][line_i] = sum([run for run in all_lines[x][line_i]])/len(all_lines[x][line_i])
    return process_state(all_lines, cycle_n)

def plotStates(days: List[int], vals: List[List[float]]):
    line_n = 2
    #column_n = 2
    column_n = 3
    for i in range(0, line_n):
        for j in range(0,column_n):
            plt.subplot(line_n, column_n, column_n*i+j+1)
            plt.plot(days, vals[column_n*i+j])
            if(i != line_n-1):
                ax = plt.gca()
                ax.get_xaxis().set_visible(False) #hide x axis

    _fontsize = 13;
    _fontsize_title = 14;

    #FIGURE 3.1:
    """
    plt.subplot(line_n, column_n, 1)
    plt.title('capital gini coefficient', fontsize=_fontsize_title)
    plt.ylabel('Inequality', fontsize=_fontsize)
    plt.ylim(0.5, 1)
    
    plt.subplot(line_n, column_n, 2)
    plt.title('Production', fontsize=_fontsize_title)
    plt.ylabel('stock', fontsize=_fontsize)
    plt.ylim(0, 100)
    
    plt.subplot(line_n, column_n, 3)
    plt.title('Unemployment', fontsize=_fontsize_title)
    plt.ylabel('unemployed persons', fontsize=_fontsize)
    plt.ylim(0, 0.5)
    
    plt.subplot(line_n, column_n, 4)
    plt.title('Average salary', fontsize=_fontsize_title)
    plt.ylabel('capital', fontsize=15)
    plt.ylim(0, 30)
    plt.xlabel('cycle', fontsize=_fontsize)
    
    plt.subplot(line_n, column_n, 5)
    plt.title('Essential satisfaction', fontsize=_fontsize_title)
    plt.ylabel('essential/person', fontsize=_fontsize)
    plt.ylim(0, 1)
    plt.xlabel('cycle', fontsize=_fontsize)
    
    plt.subplot(line_n, column_n, 6)
    plt.title('Luxury satisfaction', fontsize=_fontsize_title)
    plt.ylabel('luxury/person', fontsize=_fontsize)
    plt.ylim(0, 2.5)
    plt.xlabel('cycle', fontsize=_fontsize)
    #"""

    #Figure 3.2 & 3.13:
    #"""
    plt.subplot(line_n, column_n, 1)
    plt.title('Essential salary', fontsize=_fontsize_title)
    plt.ylabel('capital', fontsize=_fontsize)
    plt.ylim(0, 40)
    
    plt.subplot(line_n, column_n, 2)
    plt.title('Essential Employees', fontsize=_fontsize_title)
    plt.ylabel('persons', fontsize=_fontsize)
    plt.ylim(0, 18)
    
    plt.subplot(line_n, column_n, 3)
    plt.title('Essential Production', fontsize=_fontsize_title)
    plt.ylabel('stock', fontsize=_fontsize)
    plt.ylim(0, 50)

    plt.subplot(line_n, column_n, 4)
    plt.title('Luxury salary', fontsize=_fontsize_title)
    plt.ylabel('capital', fontsize=_fontsize)
    plt.ylim(0, 40)
    plt.xlabel('cycle', fontsize=_fontsize)
    
    plt.subplot(line_n, column_n, 5)
    plt.title('Luxury Employees', fontsize=_fontsize_title)
    plt.ylabel('persons', fontsize=_fontsize)
    plt.ylim(0, 18)
    plt.xlabel('cycle', fontsize=_fontsize)
    
    plt.subplot(line_n, column_n, 6)
    plt.title('Luxury Production', fontsize=_fontsize_title)
    plt.ylabel('stock', fontsize=_fontsize)
    plt.ylim(0, 50)
    plt.xlabel('cycle', fontsize=_fontsize)
    
    #"""

    #Figure 3.5 & 3.6:
    """
    plt.subplot(line_n, column_n, 1)
    plt.title('Giri index', fontsize=_fontsize_title)
    plt.ylabel('inequality', fontsize=_fontsize)
    plt.ylim(0, 1)
    
    plt.subplot(line_n, column_n, 2)
    plt.title('Production', fontsize=_fontsize_title)
    plt.ylabel('stock', fontsize=_fontsize)
    plt.ylim(0, 100)
    
    plt.subplot(line_n, column_n, 3)
    plt.title('Consumption', fontsize=_fontsize_title)
    plt.ylabel('stock', fontsize=_fontsize)
    plt.ylim(0, 100)
    plt.xlabel('cycle', fontsize=_fontsize)
    
    plt.subplot(line_n, column_n, 4)
    plt.title('Leftover', fontsize=_fontsize_title)
    plt.ylabel('stock', fontsize=_fontsize)
    plt.ylim(0, 3000)
    plt.xlabel('cycle', fontsize=_fontsize)
    #"""

    #figure 3.7 & 3.8:
    """
    
    plt.subplot(line_n, column_n, 1)
    plt.title('Giri index', fontsize=_fontsize_title)
    plt.ylabel('inequality', fontsize=_fontsize)
    plt.ylim(0, 1)
    
    plt.subplot(line_n, column_n, 2)
    plt.title('Production', fontsize=_fontsize_title)
    plt.ylabel('stock', fontsize=_fontsize)
    plt.ylim(0, 100)
    
    plt.subplot(line_n, column_n, 3)
    plt.title('Consumption', fontsize=_fontsize_title)
    plt.ylabel('stock', fontsize=_fontsize)
    plt.ylim(0, 100)
    plt.xlabel('cycle', fontsize=_fontsize)
    
    plt.subplot(line_n, column_n, 4)
    plt.title('Average salary', fontsize=_fontsize_title)
    plt.ylabel('capital', fontsize=_fontsize)
    plt.ylim(0, 30)
    plt.xlabel('cycle', fontsize=_fontsize)
    
    #"""

    #Initial conditions
    """
    plt.subplot(line_n, column_n, 1)
    plt.title('capital gini coefficient')
    plt.ylabel('Inequality')
    plt.ylim(0.5, 1)
    plt.subplot(line_n, column_n, 3)
    plt.title('Production')
    plt.ylabel('stock')
    plt.subplot(line_n, column_n, 5)
    plt.title('share values gin index')
    plt.ylabel('Inequality')
    plt.ylim(0.5, 1)
    plt.subplot(line_n, column_n, 7)
    plt.title('Unemployment')
    plt.ylabel('unemployed persons')
    plt.xlabel('cycle')

    plt.subplot(line_n, column_n, 2)
    plt.title('Mean salary')
    plt.ylabel('capital')
    plt.subplot(line_n, column_n, 4)
    plt.title('Essential satisfaction')
    plt.ylabel('essential/person')
    plt.ylim(0, 1)
    plt.subplot(line_n, column_n, 6)
    plt.title('Luxury satisfaction')
    plt.ylabel('luxury/person')
    plt.ylim(0, None)
    plt.subplot(line_n, column_n, 8)
    plt.title('Luxury gini coefficient')
    plt.ylabel('inequality')
    plt.ylim(0.5, 1)
    plt.xlabel('cycle')
    #"""
    #Stock detailed
    """
    plt.subplot(line_n, column_n, 1)
    plt.title('Essential Production')
    plt.ylabel('stock')
    plt.ylim(0, None)
    plt.subplot(line_n, column_n, 3)
    plt.title('Essential consumption')
    plt.ylabel('stock')
    plt.ylim(0, None)
    plt.subplot(line_n, column_n, 5)
    plt.title('Essential salaries')
    plt.ylabel('capital')
    plt.ylim(0, None)
    plt.subplot(line_n, column_n, 7)
    plt.title('Employees')
    plt.ylabel('persons')
    plt.ylim(0, None)
    plt.xlabel('cycle')
    
    plt.subplot(line_n, column_n, 2)
    plt.title('Luxury Production')
    plt.ylim(0, None)
    plt.ylabel('stock')
    plt.subplot(line_n, column_n, 4)
    plt.title('Luxury consumption')
    plt.ylim(0, None)
    plt.ylabel('stock')
    plt.subplot(line_n, column_n, 6)
    plt.title('Luxury salaries')
    plt.ylim(0, None)
    plt.ylabel('capital')
    plt.subplot(line_n, column_n, 8)
    plt.title('Employees')
    plt.ylim(0, None)
    plt.ylabel('persons')
    plt.xlabel('cycle')
    #"""
    #MONOPOLY alone
    """
    plt.subplot(1, 1, 1)
    plt.title('giri index')
    plt.ylabel('inequality')
    plt.ylim(0.5, 1)
    plt.xlabel('cycle')
    #"""
    #Deep stock
    """
    plt.subplot(line_n, column_n, 1)
    plt.title('essential leftover')
    plt.ylabel('stock')
    plt.subplot(line_n, column_n, 2)
    plt.title('luxury leftover')
    plt.ylabel('stock')
    plt.subplot(line_n, column_n, 3)
    plt.title('essential giri index')
    plt.ylabel('inequality')
    plt.ylim(0, 1)
    plt.subplot(line_n, column_n, 4)
    plt.title('luxury giri index')
    plt.ylabel('inequality')
    plt.ylim(0, 1)
    plt.subplot(line_n, column_n, 5)
    plt.title('luxury median price')
    plt.ylabel('capital')
    plt.ylim(0, None)
    plt.subplot(line_n, column_n, 6)
    plt.title('essential median price')
    plt.ylabel('capital')
    plt.ylim(0, None)
    plt.subplot(line_n, column_n, 7)
    plt.title('essential profit margin')
    plt.ylabel('cost %')
    plt.ylim(0.2, 0.6)
    plt.xlabel('cycle')
    plt.subplot(line_n, column_n, 8)
    plt.title('luxury profit margin')
    plt.ylabel('cost %')
    plt.ylim(0.2, 0.6)
    plt.xlabel('cycle')
    """
    #Customization analysis
    """
    plt.subplot(line_n, column_n, 1)
    plt.title('capital gini coefficient')
    plt.ylabel('Inequality')
    plt.ylim(0.5, 1)
    plt.subplot(line_n, column_n, 2)
    plt.title('Mean salary')
    plt.ylabel('capital')
    plt.ylim(0, None)
    plt.subplot(line_n, column_n, 3)
    plt.title('Essential satisfaction')
    plt.ylabel('essential/person')
    plt.ylim(0, None)
    plt.subplot(line_n, column_n, 4)
    plt.title('Luxury satisfaction')
    plt.ylabel('luxury/person')
    plt.ylim(0, None)
    plt.subplot(line_n, column_n, 5)
    plt.title('essential leftover')
    plt.ylabel('stock')
    plt.ylim(0, None)
    plt.subplot(line_n, column_n, 6)
    plt.title('luxury leftover')
    plt.ylabel('stock')
    plt.ylim(0, None)
    plt.subplot(line_n, column_n, 7)
    plt.title('essential production')
    plt.ylabel('stock')
    plt.ylim(0, None)
    plt.xlabel('cycle')
    plt.subplot(line_n, column_n, 8)
    plt.title('luxury production')
    plt.ylabel('stock')
    plt.ylim(0, None)
    plt.xlabel('cycle')
    #"""
    # No luxury
    """
    plt.subplot(line_n, column_n, 1)
    plt.title('capital gini coefficient')
    plt.ylabel('inequality')
    plt.ylim(0.5, 1)
    plt.subplot(line_n, column_n, 2)
    plt.title('essential gini coefficient')
    plt.ylabel('inequality')
    plt.ylim(0, 1)
    plt.subplot(line_n, column_n, 3)
    plt.title('essential production')
    plt.ylabel('stock')
    plt.ylim(0, None)
    plt.subplot(line_n, column_n, 4)
    plt.title('essential satisfaction')
    plt.ylabel('essential/person')
    plt.ylim(0, None)
    plt.subplot(line_n, column_n, 5)
    plt.title('mean salary')
    plt.ylabel('capital')
    plt.ylim(0, None)
    plt.xlabel('cycle')
    plt.subplot(line_n, column_n, 6)
    plt.title('Unemployment')
    plt.ylabel('unemployed persons')
    plt.ylim(0, None)
    plt.xlabel('cycle')
    #"""
    return plt
