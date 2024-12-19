import numpy as np
import matplotlib.pyplot as plt
import time
import StateGraphEvolutionVR
import StateGraphEvolution

mu = 1.0
lamb = 1.0
lamb1 = 1.0
mu1 = 1.0
M = np.asarray([[-lamb1, lamb1, 0, 0, 0, 0],
                [mu1, -mu1 - lamb, 0, lamb, 0, 0],
                [mu, 0, -mu - lamb1, lamb1, 0, 0],
                [0, mu, mu1, -mu - mu1 - lamb, 0, lamb],
                [0, 0, 2 * mu, 0, -2 * mu - lamb1, lamb1],
                [0, 0, 0, 2 * mu, mu1, -mu1 - 2 * mu]])
system_fail = 5

max_duration = 10.0
stamp_amount = 50
time_stamp = np.logspace(0, np.log10(max_duration), stamp_amount)
pop_size = 20000

start = time.perf_counter()
reliability, var = StateGraphEvolutionVR.simulate_state_graph_reliability_system_based_cropped_pdf(M, system_fail,
                                                                                                   pop_size,
                                                                                                   time_stamp
                                                                                                   )
r2, v2 = StateGraphEvolutionVR.simulate_state_graph_reliability_component_based_cropped_pdf(M, system_fail,
                                                                                            pop_size,
                                                                                            time_stamp)

end = time.perf_counter()
print(f"Simulation time: {end - start:.3f} seconds")

fig, axs = plt.subplots(2)
axs[0].semilogx(time_stamp, 1 - reliability, time_stamp, 1 - r2)
axs[0].set_title("unreliability")
axs[1].semilogx(time_stamp, var, time_stamp, v2)
axs[1].set_title("s²")
axs[0].grid(True)
axs[1].grid(True)
plt.tight_layout()
plt.show()
