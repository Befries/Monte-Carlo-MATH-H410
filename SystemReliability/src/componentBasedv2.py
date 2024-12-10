import numpy as np 
import random

def sample_time(failureRate,T):
    """
    This function sample the time of a component. 

    :failureRate: the failure rate of the component 
    :return: the tima at wich the failure occurs 
    """
    ksi = random.uniform(0,1)
    if ksi == 0 : 
        t = T 
    else :
        t = np.log(failureRate/ksi) * 1/failureRate
    return t

def transition(M, ligne_etat, column,T,tmin, column_transition):
    failureRate = M.item((ligne_etat, column))
    t = sample_time(failureRate,T)
    if t < tmin : 
        tmin = t 
        column_transition = column
    return tmin , column_transition

def simulator(M,Y,T):
    """
    This function simulates the transitions of the system. 

    :M: transition rate matrix
    :Y: the failure boundary
    :T: mission time 
    :return: True if the system is still operating 
    """
    clock_time = 0 
    system_operating = True 
    size = M.shape[0]
    ligne_etat = 0 # initially the state is at line 0 

    while clock_time < T and ligne_etat < Y :  
        # as long as the mission time is not exced and the system is not failed 
        tmin = 1000
        column_transition = 10
        for column in range(size):

            if column == ligne_etat : 
                continue # a state can never transition to himself 
            elif M.item((ligne_etat,column)) == 0:
                continue # 0 corresponds to impossible transitions 
            else :
                tmin, column_transition = transition(M,ligne_etat, column, T, tmin, column_transition)
    
        ligne_etat = column_transition # the system transitions 
        clock_time += tmin 

    if ligne_etat >= Y : 
        system_operating = False

    return system_operating

"""
Input variables : 
"""
Tmission = 1 
Y = 3 # the failure zone (4 is for 2 parallele components )

M = np.matrix([[-2,1,1,0],
               [1,-2,0,1],
               [1,0,-2,1],
               [0,1,1,-2]])

"""
testing matrices 
M = np.matrix([[-3,1,1,1,0,0,0,0],
                [1,-3,0,0,1,1,0,0],
                [1,0,-3,0,1,0,1,0],
                [1,0,0,-3,0,1,1,0],
                [0,1,1,0,-3,0,0,1],
                [0,1,0,1,0,-3,0,1],
                [0,0,1,1,0,0,-3,1],
                [0,0,0,0,1,1,1,-3]]) # the transition rate matrix
"""

N = 10000
#print(simulator_transition(M,Y,Tmission))

counter = 0 
for i in range(N):
    if simulator(M,Y,Tmission):
        counter += 1 
estimation = counter/N
variance = estimation*(1-estimation)

print("estimation",estimation)
print("variance", variance)