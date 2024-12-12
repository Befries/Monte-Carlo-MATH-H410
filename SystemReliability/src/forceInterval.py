import numpy as np 
import random

"""
If we force the occurence of the failure in a specific time, then we cannot 
employ a simple counter anymore. The weight of a failure or succes of a system
has to be adapted. 
"""

def sample_time(failureRate,T):
    """
    This function sample the time of a component with a probability density 
    function forced to a failure in the mission time. 

    :failureRate: the failure rate of the component 
    :T: the mission time 
    :return: the tima at wich the failure occurs 
    """
    ksi = random.uniform(0,1)
    if ksi == 0 : 
        t = T 
    else :
        t = - np.log(1 - ksi * np.exp(-failureRate*T)) *1/failureRate
    return t

def transition(M, ligne_etat, column,T,tmin, column_transition):
    failureRate = M.item((ligne_etat, column))
    t = sample_time(failureRate,T)
    if t < tmin : 
        tmin = t 
        column_transition = column
    return tmin , column_transition

def weight(T,failureRate):
    return np.exp(-failureRate*T)

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
                weight = weight * np.exp(-failureRate*T)
                tmin, column_transition = transition(M,ligne_etat, column, T, tmin, column_transition)
    
        ligne_etat = column_transition # the system transitions 
        clock_time += tmin 

    if ligne_etat >= Y : 
        system_operating = False

    return system_operating, weight

"""
Input variables : 
"""
Tmission = 1
Y = 3 # the failure zone (4 is for 2 parallele components )
mu = 1
lamb = 1e-4
M = np.matrix([[-lamb-lamb,lamb,lamb,0],
               [mu,-lamb-mu,0,lamb],
               [mu,0,-lamb-mu,lamb],
               [0,mu,mu,-mu-mu]])


N = 1000
counter = 0 
for i in range(N):
    operation, weight = simulator(M,Y,Tmission)
    if operation:
        counter += weight
estimation = counter/N
variance = estimation*(1-estimation)
print(estimation)
print(variance)