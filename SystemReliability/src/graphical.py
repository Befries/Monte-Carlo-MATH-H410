import numpy as np 
import random
import time 
import matplotlib.pyplot as plt
from systemBased import simulator

def variance_estimate(Tmission,M,Y,M_proba):
    N = 1000
    space_range = 100
    # to estimate over a time window 
    time_window = np.logspace(-1, np.log10(Tmission), num=space_range)
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
    axs[1].set_title("Availability")
    axs[1].set_ylabel("Availability", color=color)
    axs[1].tick_params(axis='y', labelcolor=color)
    axs[1].set_xlabel("time")
    axs[1].set_xscale('log')
    axs[1].grid(visible=True, which='both', axis='both')

    plt.tight_layout()
    plt.show()
    return

def parameter_impact(Tmission, Y,mu, mu1 ,lamb1 ):
    N = 1000
    space_range = 100
    
    # to evalute the impact of different repair and failure rates
    parameter_range = np.asarray([1e-3,0.01,0.1])

    # to estimate over a time window 
    time_window = np.logspace(0.0, np.log10(Tmission), num=space_range)
    estimation_window = np.array([np.empty(space_range),np.empty(space_range),np.empty(space_range)])
    variance_window = np.array([np.empty(space_range),np.empty(space_range),np.empty(space_range)])

    simulation_time = np.empty(space_range)

    for k, parameter in enumerate(parameter_range) : 
        lamb = parameter # defines wich parameter we will make vary 
        M = np.asarray([[-lamb1, lamb1, 0, 0,0,0],
                [mu1,-mu1-lamb,0,lamb,0,0],
                [mu,0,-mu-lamb1,lamb1,0,0],
                [0,mu,mu1,-mu-mu1-lamb,0,lamb],
                [0,0,2*mu, 0,-2*mu-lamb1,lamb1],
                [0,0,0,2*mu,mu1,-mu1-2*mu]])
        M_proba = np.asarray([[0, 1, 0, 0,0,0],
                [mu1/(mu1+lamb),0,0,lamb/(mu1+lamb),0,0],
                [mu/(mu+lamb1),0,0,lamb1/(mu+lamb1),0,0],
                [0,mu/(mu+mu1+lamb),mu1/(mu+mu1+lamb),0,0,lamb/(mu+mu1+lamb)],
                [0,0,2*mu/(2*mu+lamb1), 0,0,lamb1/(2*mu+lamb1)],
                [0,0,0,2*mu/(2*mu+mu1),mu1/(2*mu+mu1),0]])
        

        for j, t in enumerate(time_window) :
            start = time.perf_counter()
            counter = 0 
            for i in range(N):
                operation = simulator(M,Y,t,M_proba)
                if operation:
                    counter += 1
            estimation_window[k][j] = counter/N
            variance_window[k][j] = estimation_window[k][j]*(1-estimation_window[k][j])
            simulation_time[j] = time.perf_counter() - start

        total_time = np.sum(simulation_time)
        print("all simulation run in", total_time, "seconds")

    fig, axs = plt.subplots(2)
    axs[0].plot(time_window, variance_window[0], 'r', label="1e-3")
    axs[0].plot(time_window, variance_window[1], 'b', label="0.01")
    axs[0].plot(time_window, variance_window[2], 'g', label="0.1")
    #axs[0].plot(time_window, variance_window[3], 'm', label="0.1")
    #axs[0].plot(time_window, variance_window[4], 'y', label="0.1")
    axs[0].set_title("Variance")
    axs[0].set_yscale('linear')
    axs[0].set_xlabel("time")
    axs[0].set_xscale('log')
    axs[0].grid(visible=True, which='both', axis='both')
    axs[0].legend(title= "failure/repaire rate ratio")


    color = 'tab:red'
    axs[1].plot(time_window, estimation_window[0], 'r', label= "1e-3")
    axs[1].plot(time_window, estimation_window[1], 'b', label= "0.01")
    axs[1].plot(time_window, estimation_window[2], 'g', label="0.1")
    #axs[1].plot(time_window, estimation_window[3], 'm', label="0.1")
    #axs[1].plot(time_window, estimation_window[4], 'y', label="0.1")
    axs[1].set_title("Availability")
    axs[1].set_ylabel("Availability", color=color)
    axs[1].tick_params(axis='y', labelcolor=color)
    axs[1].set_xlabel("time")
    axs[1].set_xscale('log')
    axs[1].grid(visible=True, which='both', axis='both')
    axs[1].legend(title= "failure/repaire rate ratio")

    plt.tight_layout()
    fig.suptitle("Results for a component based approach")
    plt.show()
    return


Tmission = 100000
Y = 3 # the failure zone (3 is for 2 parallele components )
mu = 1
lamb = 1
mu1 = 1
lamb1 = 1 

"""
M = np.matrix([[-lamb-lamb,lamb,lamb,0],
               [mu,-lamb-mu,0,lamb],
               [mu,0,-lamb-mu,lamb],
               [0,mu,mu,-mu-mu]])
M_proba = np.asarray([[0,lamb/(lamb+lamb),lamb/(lamb+lamb),0],
                      [mu/(mu+lamb),0,0,lamb/(mu+lamb)],
                      [mu/(mu+lamb),0,0,lamb/(lamb+mu)],
                      [0,mu/(mu+mu), mu/(mu+mu),0]])
"""
M = np.asarray([[-lamb1, lamb1, 0, 0,0,0],
                [mu1,-mu1-lamb,0,lamb,0,0],
                [mu,0,-mu-lamb1,lamb1,0,0],
                [0,mu,mu1,-mu-mu1-lamb,0,lamb],
                [0,0,2*mu, 0,-2*mu-lamb1,lamb1],
                [0,0,0,2*mu,mu1,-mu1-2*mu]])

#variance_estimate(Tmission,M,Y,M_proba)
parameter_impact(Tmission,Y,1,1,1)
