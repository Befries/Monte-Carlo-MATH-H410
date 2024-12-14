import numpy as np 
import random

def sample_time(failureRate,T):
    """
    This function sample the time of a component. 

    :failureRate: the failure rate of the component 
    :return: the tima at wich the failure occurs 
    """
    ksi = random.uniform(0,1)
    t = - np.log(ksi) * 1/failureRate
    return t

def transition(M_proba, ligne_etat):
    """
    This function samples the state the system will transition to. 
    """
    return np.random.choice(a=np.arange(M_proba.shape[0]), p=M_proba[ligne_etat, :])

def simulator(M,Y,T,M_proba):
    """
    This function simulates the transitions of the system. 

    :M: transition rate matrix
    :Y: the failure boundary
    :T: mission time 
    :return: True if the system is still operating 
    """
    clock_time = 0 
    system_operating = True 
    ligne_etat = 0 # initially the state is at line 0 
    while clock_time < T and ligne_etat < Y :  
        # as long as the mission time is not exced and the system is not failed 
        # before each transition we sample the transition time 

        a = -M[ligne_etat,ligne_etat]
        t = sample_time(a,T)
        column_transition = transition(M_proba,ligne_etat)
            
        ligne_etat = column_transition # the system transitions 
        clock_time += t

    if ligne_etat >= Y : 
        system_operating = False

    return system_operating

"""
Input variables : 
"""
Tmission = 10
Y = 3 # the failure zone (3 is for 2 parallele components )
mu = 1
lamb = 1
M = np.asarray([[-lamb-lamb,lamb,lamb,0],
               [mu,-lamb-mu,0,lamb],
               [mu,0,-lamb-mu,lamb],
               [0,mu,mu,-mu-mu]])
M_proba = np.asarray([[0,lamb/(lamb+lamb),lamb/(lamb+lamb),0],
                      [mu/(mu+lamb),0,0,lamb/(mu+lamb)],
                      [mu/(mu+lamb),0,0,lamb/(lamb+mu)],
                      [0,mu/(mu+mu), mu/(mu+mu),0]])



N = 10000
counter = 0 
for i in range(N):
    if simulator(M,Y,Tmission,M_proba):
        counter += 1 
estimation = counter/N
variance = estimation*(1-estimation)
print(estimation)
print(variance)
