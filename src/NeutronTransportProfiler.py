import numpy as np
import matplotlib.pyplot as plt

import time

from NeutronTransport1 import simulate_transport

thickness_tests = 10
thicknesses = np.linspace(2, 10, thickness_tests)
pop_size = int(1e4)
penetrations = np.empty(thickness_tests)
variances = np.empty(thickness_tests)
simulation_time = np.empty(thickness_tests)

for i, thickness in enumerate(thicknesses):
    start = time.perf_counter()
    penetrations[i], variances[i] = simulate_transport(0.3, 0.8, thickness, pop_size)
    simulation_time[i] = time.perf_counter() - start

total_time = np.sum(simulation_time)
Efficiency = 1 / (variances * simulation_time) * pop_size

print("all simulation run in", total_time, "seconds")

fig, axs = plt.subplots(2)
axs[0].scatter(thicknesses, penetrations * 100)
axs[0].set_title("penetration probability")
axs[0].set_ylabel("[%]")
axs[0].set_xlabel("thickness [cm]")

color = 'tab:red'
axs[1].plot(thicknesses, Efficiency, color=color)
axs[1].set_title("Efficiency and Variance")
axs[1].set_ylabel("Efficiency", color=color)
axs[1].tick_params(axis='y', labelcolor=color)
axs[1].set_xlabel("thickness [cm]")

color = 'tab:blue'
var_ax = axs[1].twinx()
var_ax.scatter(thicknesses, variances, color=color)
var_ax.set_ylabel("Variance s²", color=color)
var_ax.tick_params(axis='y', labelcolor=color)

for ax in axs:
    ax.grid(visible=True)

plt.tight_layout()
plt.show()
