import numpy as np
import matplotlib.pyplot as plt
import time
import StateGraphEvolutionVR
import StateGraphEvolution

mu = 1.0
lamb = 1/2
lamb1 = 1/2
mu1 = 1.0
M = np.asarray([[-lamb1, lamb1, 0, 0, 0, 0],
                [mu1, -mu1 - lamb, 0, lamb, 0, 0],
                [mu, 0, -mu - lamb1, lamb1, 0, 0],
                [0, mu, mu1, -mu - mu1 - lamb, 0, lamb],
                [0, 0, 2 * mu, 0, -2 * mu - lamb1, lamb1],
                [0, 0, 0, 2 * mu, mu1, -mu1 - 2 * mu]])
system_fail = 3

max_duration = 20.0
stamp_amount = 100
time_stamp = np.logspace(-1, np.log10(max_duration), stamp_amount)
pop_size = 50000

start = time.perf_counter()
availability, var = StateGraphEvolutionVR.simulate_state_graph_evolution_system_based(M, system_fail, pop_size,
                                                                                      time_stamp,
                                                                                      reliability=False,
                                                                                      failure_boost=100)
end = time.perf_counter()
print(f"Simulation time: {end - start:.3f} seconds")

print(availability)

fig, axs = plt.subplots(2)
axs[0].semilogx(time_stamp, availability)
axs[0].set_title("Availability")
axs[1].loglog(time_stamp, np.sqrt(var/pop_size))
axs[1].set_title("standard_deviation")
plt.tight_layout()
plt.show()
