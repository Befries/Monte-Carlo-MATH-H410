import numpy as np
import matplotlib.pyplot as plt

import time

from NeutronTransport import simulate_transport


thickness_tests = 10
thicknesses = np.linspace(0.01, 0.1, thickness_tests)
pop_size = int(1e5)
penetrations = np.empty(thickness_tests)
variances = np.empty(thickness_tests)
simulation_time = np.empty(thickness_tests)


for i, thickness in enumerate(thicknesses):
    start = time.perf_counter()
    penetrations[i], variances[i] = simulate_transport(500, 200, thickness, pop_size)
    simulation_time[i] = time.perf_counter() - start

total_time = np.sum(simulation_time)
Efficiency = 1 / (variances * simulation_time) * pop_size

print("all simulation run in", total_time, "seconds")

fig, axs = plt.subplots(2)
axs[0].scatter(thicknesses, penetrations)
axs[0].set_title("penetration probability")
axs[1].scatter(thicknesses, Efficiency)
axs[1].set_title("variance estimation")

for ax in axs:
    ax.grid(visible=True)

plt.tight_layout()
plt.show()