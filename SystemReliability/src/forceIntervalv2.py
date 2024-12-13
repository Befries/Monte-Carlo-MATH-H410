import numpy as np 
import random

"""
If we force the occurence of the failure in a specific time, then we cannot 
employ a simple counter anymore. The weight of a failure or succes of a system
has to be adapted. 
The weight and the sample time varies with time 
"""

def sample_time(failureRate,T,currentT):
    """
    This function sample the time of a component with a probability density 
    function forced to a failure in the mission time. 

    :failureRate: the failure rate of the component 
    :T: the mission time 
    :return: the tima at wich the failure occurs 
    """
    ksi = random.uniform(0,1)
    t = ksi/ lamb / np.exp(-lamb*currentT) # here the current time corresponds to the last time at wich an evenement appeared 
    return t

def transition(M, ligne_etat, column,T,tmin, column_transition, currentT):
    failureRate = M.item((ligne_etat, column))
    t = sample_time(failureRate,T,currentT)
    if t < tmin : 
        tmin = t 
        column_transition = column
    return tmin , column_transition

def calculate_weight(t,failureRate,currentT): #t is the time at wich the evenement appears
    return np.exp(-failureRate*(t))

def simulator(M,Y,T):
    """
    This function simulates the transitions of the system with the adapyted weight. 

    :M: transition rate matrix
    :Y: the failure boundary
    :T: mission time 
    :return: True if the system is still operating 
    """
    clock_time = 0 
    system_operating = True # we always start with an operating system
    size = M.shape[0]
    ligne_etat = 0 # initially the state is at line 0 
    weight = 1 # at the beginning the weight is 1 

    while clock_time < T and ligne_etat < Y : # if you want to evaluate the availability you have to erase the second condition
        # as long as the mission time is not exced and the system is not failed 
        tmin = 1000
        column_transition = 10
        for column in range(size):

            if column == ligne_etat : 
                continue # a state can never transition to himself 
            elif M.item((ligne_etat,column)) == 0:
                continue # 0 corresponds to impossible transitions 
            else :
                failureRate = M.item((ligne_etat, column))
                tmin, column_transition = transition(M,ligne_etat, column, T, tmin, column_transition, clock_time)
                weight *=  calculate_weight(tmin,failureRate, clock_time)

    
        ligne_etat = column_transition # the system transitions 
        clock_time += tmin 

    if ligne_etat >= Y : 
        system_operating = False

    return system_operating, weight

"""
Input variables : 
"""
Tmission = 1000
Y = 3 # the failure zone (4 is for 2 parallele components )
mu = 1
lamb = 1e-4
M = np.matrix([[-lamb-lamb,lamb,lamb,0],
               [mu,-lamb-mu,0,lamb],
               [mu,0,-lamb-mu,lamb],
               [0,mu,mu,-mu-mu]])


N = 10000
counter = 0 
variance = 0 # the vraince must be adapted 
for i in range(N):
    operation, weight = simulator(M,Y,Tmission)
    if operation:
        counter += weight
        variance += weight**2
estimation = counter/N
variance = variance/N
variance = variance - estimation**2
print(estimation)
print(variance)