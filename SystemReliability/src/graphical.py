import numpy as np 
import random
import time 
import matplotlib.pyplot as plt
from systemBased import simulator
import systemBased

def variance_estimate(Tmission,M,Y):
    N = 1000
    space_range = 100
    # to estimate over a time window 
    time_window = np.logspace(0.0, np.log10(Tmission), num=space_range)
    estimation_window = np.empty(space_range)
    variance_window = np.empty(space_range)
    simulation_time = np.empty(space_range)

    for j, t in enumerate(time_window) :
        start = time.perf_counter()
        counter = 0 
        for i in range(N):
            if simulator(M,Y,t):
                counter += 1 
        estimation_window[j] = counter/N
        variance_window[j] = estimation_window[j]*(1-estimation_window[j])
        simulation_time[j] = time.perf_counter() - start

    total_time = np.sum(simulation_time)
    print("all simulation run in", total_time, "seconds")

    fig, axs = plt.subplots(2)
    axs[0].plot(time_window, variance_window)
    axs[0].set_title("variances")
    axs[0].set_yscale('linear')
    axs[0].set_xlabel("time")
    axs[0].set_xscale('log')
    axs[0].grid(visible=True, which='both', axis='both')

    color = 'tab:red'
    axs[1].plot(time_window, estimation_window, color=color)
    axs[1].set_title("Reliability")
    axs[1].set_ylabel("Reliability", color=color)
    axs[1].tick_params(axis='y', labelcolor=color)
    axs[1].set_xlabel("time")
    axs[1].set_xscale('log')
    axs[1].grid(visible=True, which='both', axis='both')

    plt.tight_layout()
    plt.show()
    return

def parameter_impact(Tmission, Y, mu):
    N = 1000
    space_range = 100
    
    # to evalute the impact of different repair and failure rates
    parameter_range = np.array([1e-5,1e-4,0.1])

    # to estimate over a time window 
    time_window = np.logspace(0.0, np.log10(Tmission), num=space_range)
    estimation_window = np.array([np.empty(space_range),np.empty(space_range),np.empty(space_range)])
    variance_window = np.array([np.empty(space_range),np.empty(space_range),np.empty(space_range)])

    simulation_time = np.empty(space_range)

    for k, parameter in enumerate(parameter_range) : 
        lamb = parameter # defines wich parameter we will make vary 
        M = np.matrix([[-lamb-lamb,lamb,lamb,0],
               [mu,-lamb-mu,0,lamb],
               [mu,0,-lamb-mu,lamb],
               [0,mu,mu,-mu-mu]])
        

        for j, t in enumerate(time_window) :
            start = time.perf_counter()
            counter = 0 
            for i in range(N):
                operation = simulator(M,Y,Tmission)
                if operation:
                    counter += 1
            estimation_window[k][j] = counter/N
            variance_window[k][j] = estimation_window[k][j]*(1-estimation_window[k][j])
            simulation_time[j] = time.perf_counter() - start

        total_time = np.sum(simulation_time)
        print("all simulation run in", total_time, "seconds")

    fig, axs = plt.subplots(2)
    axs[0].plot(time_window, variance_window[0], 'r', label="1e-5")
    axs[0].plot(time_window, variance_window[1], 'b', label="1e-4")
    axs[0].plot(time_window, variance_window[2], 'g', label="0.1")
    #axs[0].plot(time_window, variance_window[3], 'm', label="0.01")
    #axs[0].plot(time_window, variance_window[4], 'y', label="0.1")
    axs[0].set_title("Variance")
    axs[0].set_yscale('linear')
    axs[0].set_xlabel("time")
    axs[0].set_xscale('log')
    axs[0].grid(visible=True, which='both', axis='both')
    axs[0].legend(title= "failure/repaire rate ratio")


    color = 'tab:red'
    axs[1].plot(time_window, estimation_window[0], 'r', label= "1e-5")
    axs[1].plot(time_window, estimation_window[1], 'b', label= "1e-4")
    axs[1].plot(time_window, estimation_window[2], 'g', label="0.1")
    #axs[1].plot(time_window, estimation_window[3], 'm', label="0.01")
    #axs[1].plot(time_window, estimation_window[4], 'y', label="0.1")
    axs[1].set_title("Reliability")
    axs[1].set_ylabel("Reliability", color=color)
    axs[1].tick_params(axis='y', labelcolor=color)
    axs[1].set_xlabel("time")
    axs[1].set_xscale('log')
    axs[1].grid(visible=True, which='both', axis='both')
    axs[1].legend(title= "failure/repaire rate ratio")

    plt.tight_layout()
    fig.suptitle("Results for a system based approach")
    plt.show()
    return


Tmission = 1000
Y = 3 # the failure zone (3 is for 2 parallele components )
mu = 1
lamb = 0.5
M = np.matrix([[-lamb-lamb,lamb,lamb,0],
               [mu,-lamb-mu,0,lamb],
               [mu,0,-lamb-mu,lamb],
               [0,mu,mu,-mu-mu]])
"""
M = np.matrix([[-2,1,1,0],
               [1,-2,0,1],
               [1,0,-2,1],
               [0,1,1,-2]])
"""

variance_estimate(Tmission,M,Y)
#parameter_impact(Tmission,Y,1)
