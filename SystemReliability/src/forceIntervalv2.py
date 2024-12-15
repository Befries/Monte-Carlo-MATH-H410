import numpy as np 
import random

def sample_time(failureRate, currentT,T):
    """
    This function sample the time of a component for a modified CDF. 

    :failureRate: the failure/repaire rate of the component 
    :return: the time at which the failure occurs 
    """
    ksi = random.uniform(0,1)
    if currentT == 0 :
        t = - np.log(ksi) * 1/failureRate
    else : 
        # cette fonction ne donne que des valeurs de temps négatif ....
        t = - np.log(1- ksi*np.exp(-failureRate*T))/failureRate
    if t > T :
        t = 0 
    return t

def construct_weight(t,currentT,failureRate,T):
    if t < T and currentT != 0 : 
        weight = np.exp(-(T)*failureRate)
    elif currentT == 0 : 
        weight = 1
    elif t > T : 
        weight = 0 
    return weight

def transition(dicot):
    """
    This function adds the possible transitions and its associated times to the dictonnary. 
    Next the function selectes the transition with the minimum transition time. 

    :dicot: {possible transition : time of the transition}
    :return: the minimum transition time, the associated transition 
    """
    sorted_dict = dict(sorted(dicot.items(), key=lambda item: item[1]))
    column_transition = next(iter(sorted_dict.keys()))
    tmin = sorted_dict[column_transition]
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
    weight = 0 
    # if you want to evaluate the availability you have to erase the second condition
    while clock_time < T and ligne_etat < Y :
        # as long as the mission time is not exced and the system is not failed the simulation keeps going
        dicot = {} # contains all the possible transitions and the associated transition time
        for column in range(size):
            if column == ligne_etat : 
                continue # a state can never transition to himself 
            elif M.item((ligne_etat,column)) == 0:
                continue # 0 corresponds to impossible transitions 
            else :
                dicot[column] = sample_time(M[ligne_etat,column],clock_time,T)
        
        tmin, column_transition = transition(dicot)
        weight += construct_weight(tmin, clock_time, M[ligne_etat,column_transition],T)

        ligne_etat = column_transition # the system transitions 
        clock_time += tmin 

    if ligne_etat >= Y : 
        system_operating = False

    return system_operating, weight

"""
Input variables : 
"""
Tmission = 1000
Y = 3 # the failure zone (3 is for 2 parallele components )
mu = 1
mu1 = 1
lamb = 1e-6
lamb1 = 1 

M = np.matrix([[-lamb-lamb,lamb,lamb,0],
               [mu,-lamb-mu,0,lamb],
               [mu,0,-lamb-mu,lamb],
               [0,mu,mu,-mu-mu]])
"""
Matrix exercise 2 chap 6 safety :
"""
"""
M = np.asarray([[-lamb1, lamb1, 0, 0,0,0],
                [mu1,-mu1-lamb,0,lamb,0,0],
                [mu,0,-mu-lamb1,lamb1,0,0],
                [0,mu,mu1,-mu-mu1-lamb,0,lamb],
                [0,0,2*mu, 0,-2*mu-lamb1,lamb1],
                [0,0,0,2*mu,mu1,-mu1-2*mu]])
"""
N = 10000
counter = 0
variance = 0 
for i in range(N):
    working, weight = simulator(M,Y,Tmission)
    if working : 
        counter += weight
        variance += weight**2
estimation = counter/N
variance = variance/N - estimation**2
print(estimation)
print(variance)
