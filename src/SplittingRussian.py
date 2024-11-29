import numpy as np
import matplotlib.pyplot as plt


def free_flight_sampling(coefficient, cos_theta, sample_size):
    # antithetic variables
    sample = np.random.rand(sample_size)
    return -np.abs(cos_theta) / coefficient * np.log(sample)

"""
return false if an absorption occurred
true if it is a scattering
"""
def interaction_sampling(p_absorption, sample_size):
    sample = np.random.rand(sample_size)
    return sample > p_absorption

def splitting(subthickness, m, neutron_position, neutron_weight, neutron_angle):
    splitting = neutron_position > subthickness  
    
    split_positions = neutron_position[splitting]
    split_weights = neutron_weight[splitting]
    split_angles = neutron_angle[splitting]
    
    new_positions = np.repeat(split_positions, m)
    new_weights = np.repeat(split_weights / m, m)
    new_angles = np.repeat(split_angles, m)
    
    # maintain the non split neutrons
    retained_positions = neutron_position[~splitting]
    retained_weights = neutron_weight[~splitting]
    retained_angles = neutron_angle[~splitting]
    
    updated_positions = np.concatenate([retained_positions, new_positions])
    updated_weights = np.concatenate([retained_weights, new_weights])
    updated_angles = np.concatenate([retained_angles, new_angles])
    
    return updated_positions, updated_weights, updated_angles

def russion_roulette(threshold, neutron_weight, sample_size):
    sample = np.random.rand(np.size(neutron_weight))
    charger = neutron_weight < threshold  # returns boolean array 
    gachette = sample < threshold

    adjusted_weight = np.where(
        charger,                             # if charger is True
        np.where(gachette, neutron_weight / threshold, 0),  # If gachette is True: adjust weight; else: 0
        neutron_weight                      # if charger is False: keep weight unchanged
    )
    return adjusted_weight


def simulate_transport(sigma_a, sigma_s, thickness, sample_size,m, subthickness):
    sigma_t = sigma_s + sigma_a
    living_neutron = sample_size
    neutron_position = np.zeros(sample_size)
    neutron_angle = np.ones(sample_size)
    neutron_weight = np.ones(sample_size)

    p_absorption = sigma_a / sigma_t

    passed = 0
    print( "at the begining of the while, living neutron " + str(living_neutron)) 

    while living_neutron > 0:
        # is the neutron still in the wall ? 
        # better estimator here + change sampling
        free_flight = free_flight_sampling(sigma_t, neutron_angle, living_neutron)
        neutron_position = np.sign(neutron_angle) * free_flight + neutron_position
        alive = neutron_position <= thickness # if the neutron_position is less than the thickness the alive is true

        neutron_position = neutron_position[alive] # the history survives or not 
        neutron_weight = neutron_weight[alive] 
        print( "after the position check, position" + str(np.size(neutron_position)))
        print( "after the position check, weight" + str(np.size(neutron_weight)))

        # updating the number of transmitted neutrons
        transmitted = living_neutron - np.size(neutron_position)
        living_neutron = living_neutron - transmitted
        for weight in neutron_weight : 
            passed += weight
        
        print("living neutron after transmission" + str(living_neutron))

        # better estimator for scattering & absorption + russian roulette?
        neutron_weight = russion_roulette(0.5, neutron_weight,sample_size)
        not_dead = (neutron_position >= 0) | interaction_sampling(p_absorption, living_neutron) | (neutron_weight >= 0) # zéro virtuel ? 
        neutron_position = neutron_position[not_dead]
        neutron_weight = neutron_weight[not_dead]
        #living_neutron = np.size(neutron_position)

        print( "after the russian, position" + str(np.size(neutron_position)))
        print( "after the russian, weight" + str(np.size(neutron_weight)))

        # splitting strategies
        neutron_position, neutron_weight, neutron_angle = splitting(subthickness, m, neutron_position, neutron_weight,neutron_angle)
        living_neutron = np.size(neutron_weight)
        print( "after the splitting, position" + str(np.size(neutron_position)))
        print( "after the spilliting, weight" + str(np.size(neutron_weight)))
        print( "living neutron after splitting"+ str(living_neutron))

        # biasing strategies
        neutron_angle = np.random.uniform(low=-1, high=1, size=living_neutron)


    return passed / sample_size

thickness = 0.1

proba = simulate_transport(500, 200, thickness, int(100),2, 7*thickness/8)

print(proba)
