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
        t = - np.log(ksi) * 1/failureRate
    return t

def simulator_transition(M,Y,T):
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
    dictionnaire_temps = {} # the key is the transmission time, the content is the new state 

    while clock_time < T and ligne_etat < Y :  
        # as long as the mission time is not exced and the system is not failed 
        tmin = 1000
        for colonne in range(size):

            if colonne == ligne_etat : 
                continue # a state can never transition to himself 

            elif M.item((ligne_etat,colonne)) == 0:
                continue # 0 corresponds to impossible transitions 

            else :
                failureRate = M.item((ligne_etat, colonne))
                t = sample_time(failureRate,T)
                dictionnaire_temps[t] = colonne
                if t < tmin : 
                    tmin = t 
        ligne_etat = dictionnaire_temps[tmin] # the system transitions 
        clock_time += tmin 

    if ligne_etat >= Y : 
        system_operating = False

    return system_operating

"""
Input variables : 
"""
Tmission = 1 
Y = 3 # the failure zone (4 is for 2 parallele components )
mu = 1
lamb = 1
M = np.matrix([[-lamb-lamb,lamb,lamb,0],
               [mu,-lamb-mu,0,lamb],
               [mu,0,-lamb-mu,lamb],
               [0,mu,mu,-mu-mu]])

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

counter = 0 
for i in range(N):
    if simulator_transition(M,Y,Tmission):
        counter += 1 
estimation = counter/N
variance = estimation*(1-estimation)

print("estimation",estimation)
print("variance", variance)