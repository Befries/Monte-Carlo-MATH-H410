import numpy as np 
import random
"""
This code forces the failure of a component by increasing the failure rate. 
The estimation is keeped unbaised by multiplying the contribution by a weight.
"""

def sample_time(failureRate):
    """
    This function sample the time of a component. 

    :failureRate: the failure rate of the component 
    :return: the tima at wich the failure occurs 
    """
    ksi = random.uniform(0,1)
    t = - np.log(ksi) * 1/failureRate
    return t

def construct_weight(M_proba,newM_proba):
    result = np.zeros_like(M_proba, dtype=float)
    np.divide(M_proba, newM_proba, out=result, where=newM_proba != 0)
    return result

def transition(M_proba, ligne_etat):
    """
    This function samples the state the system will transition to. 
    """
    return np.random.choice(a=np.arange(M_proba.shape[0]), p=M_proba[ligne_etat, :])

def simulator(M,Y,T,M_weight,newM_proba):
    """
    This function simulates the transitions of the system. 

    :M: transition rate matrix
    :Y: the failure boundary
    :T: mission time 
    :M_proba: matrix containing the probabilities of transitionning from one state to another
    :return: True if the system is still operating 
    """
    clock_time = 0 
    system_operating = True 
    ligne_etat = 0 # initially the state is at line 0
    weight = 1 
    while clock_time < T and ligne_etat < Y :  
        # as long as the mission time is not exced and the system is not failed 
        # before each transition we sample the transition time 

        a = -M[ligne_etat,ligne_etat]
        t = sample_time(a)
        column_transition = transition(newM_proba,ligne_etat)
        weight = weight * M_weight[ligne_etat][column_transition]

        ligne_etat = column_transition # the system transitions 
        clock_time += t

    if ligne_etat >= Y : 
        system_operating = False

    return system_operating, weight

"""
Input variables : 
"""
Tmission = 10
Y = 3 # the failure zone (3 is for 2 parallele components )
mu = 1
lamb = 0.001
newlamb = 0.1
M = np.asarray([[-lamb-lamb,lamb,lamb,0],
               [mu,-lamb-mu,0,lamb],
               [mu,0,-lamb-mu,lamb],
               [0,mu,mu,-mu-mu]])

def M_proba(lamb,mu): 
    return np.asarray([[0,lamb/(lamb+lamb),lamb/(lamb+lamb),0],
                      [mu/(mu+lamb),0,0,lamb/(mu+lamb)],
                      [mu/(mu+lamb),0,0,lamb/(lamb+mu)],
                      [0,mu/(mu+mu), mu/(mu+mu),0]])

M_weight = construct_weight(M_proba(lamb,mu),M_proba(newlamb,mu))
print(M_weight)
"""
Running the simulation N times : 
"""


N = 1000
counter = 0 
variance = 0 
for i in range(N):
    working, weight = simulator(M,Y,Tmission,M_weight,M_proba(newlamb,mu))
    if working:
        counter += weight
        variance += weight**2
estimation = counter/N
variance = variance/N - estimation**2
variance1 = estimation*(1 - estimation)
print("biased estimator with forced failure : ",estimation)
print("associated variance1 : ",variance1)
print("associated variance : ",variance)
