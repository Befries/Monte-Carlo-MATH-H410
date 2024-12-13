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

def sample_probability(p):
    return np.random.uniform() < p

def calculate_weight(m):
    return 1/m

def transition(M, transitionRate,T,tmin, column_transition, column, m):
    a = -M.item((0,0))
    t = sample_time(a,T)
    p = transitionRate*m/a
    transition = sample_probability(p)
    if transition : 
        tmin = t 
        column_transition = column
    return transition, tmin , column_transition

def simulator(M,Y,T,m):
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
    weight = 1 # initially the weight is 1 but it is update each time a bias is introduced

    while clock_time < T and ligne_etat < Y :  
        # as long as the mission time is not exced and the system is not failed 
        tmin = T
        column_transition = 10
        for column in range(size):

            if column == ligne_etat : 
                continue # a state can never transition to himself 
            elif M.item((ligne_etat,column)) == 0:
                continue # 0 corresponds to impossible transitions 
            elif column > ligne_etat : # we will see only failures 
                passage, tmin, column_transition = transition(M,M.item(ligne_etat,column),T,tmin,column_transition,column,m)
                if passage : 
                    weight = weight * calculate_weight(m)
                    break
            else :
                passage , tmin, column_transition = transition(M, M.item(ligne_etat,column), T, tmin, column_transition, column ,1)
                if passage : 
                    weight = weight * calculate_weight(m)
                    break
        ligne_etat = column_transition # the system transitions 
        clock_time += tmin 

    if ligne_etat >= Y : 
        system_operating = False

    return weight,  system_operating

"""
Input variables : 
"""
Tmission = 1 
Y = 3 # the failure zone (4 is for 2 parallele components )
mu = 1
lamb = 1e-5
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
m = 10
counter = 0 
variance = 0
for i in range(N):
    weight, operation = simulator(M,Y,Tmission,2) # be careful with the mulitplicative factor 
    if operation:
        counter += weight
        variance += weight**2
estimation = counter/N
variance = variance/N
variance = variance - estimation**2

print("estimation",estimation)
print("variance", variance)