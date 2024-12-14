import numpy as np 
import random

def sample_time(failureRate):
    """
    This function sample the time of a component. 

    :failureRate: the failure/repaire rate of the component 
    :return: the time at which the failure occurs 
    """
    ksi = random.uniform(0,1)
    t = - np.log(ksi) * 1/failureRate
    return t

def transition(M, ligne_etat, column,T,tmin):
    failureRate = M.item((ligne_etat, column))
    t = sample_time(failureRate)
    if t < tmin : 
        tmin = t 
        column_transition = column
    else : 
        column_transition = ligne_etat 
    return tmin , column_transition

def simulator(M,Y,T):
    """
    This function simulates the transitions of the system. 

    :M: transition rate matrix
    :Y: the failure boundary
    :T: mission time 
    :return: True if the system is still operating when the simulation stops 
    """
    clock_time = 0 
    system_operating = True # we always start with an operating system
    size = M.shape[0]
    ligne_etat = 0 # initially the state is at line 0 

    # if you want to evaluate the availability you have to erase the second condition
    while clock_time < T and ligne_etat < Y :
        # as long as the mission time is not exced and the system is not failed the simulation keeps going
        tmin = T 

        for column in range(size):

            if column == ligne_etat : 
                continue # a state can never transition to himself 
            elif M.item((ligne_etat,column)) == 0:
                continue # 0 corresponds to impossible transitions 
            else :
                tmin, column_transition = transition(M,ligne_etat, column, T, tmin)
    
        ligne_etat = column_transition # the system transitions 
        clock_time += tmin 

    if ligne_etat >= Y : 
        system_operating = False

    return system_operating

"""
Input variables : 
"""
Tmission = 1000
Y = 3 # the failure zone (3 is for 2 parallele components )
mu = 1
lamb = 1
M = np.matrix([[-lamb-lamb,lamb,lamb,0],
               [mu,-lamb-mu,0,lamb],
               [mu,0,-lamb-mu,lamb],
               [0,mu,mu,-mu-mu]])


N = 10000
counter = 0 
for i in range(N):
    if simulator(M,Y,Tmission):
        counter +=1
estimation = counter/N
variance = estimation*(1-estimation)
print(estimation)
print(variance)