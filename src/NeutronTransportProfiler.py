import numpy as np
import matplotlib.pyplot as plt

import time

from NeutronTransport import simulate_transport


thickness_tests = 5
thicknesses = np.linspace(0.01, 0.1, thickness_tests)
penetrations = np.empty(thickness_tests)
variances = np.empty(thickness_tests)

start = time.perf_counter()
for i, thickness in enumerate(thicknesses):
    penetrations[i], variances[i] = simulate_transport(500, 200, thickness, int(1e5))
elapsed = time.perf_counter() - start

print("simulation run in", elapsed, "seconds")

fig, axs = plt.subplots(2)
axs[0].scatter(thicknesses, penetrations)
axs[0].set_title("penetration probability")
axs[1].scatter(thicknesses, variances)
axs[1].set_title("variance estimation")

for ax in axs:
    ax.grid(visible=True)

plt.tight_layout()
plt.show()