import numpy as np
import matplotlib.pyplot as plt

import time

from NeutronTransport import simulate_transport


thickness_tests = 10
thicknesses = np.linspace(0.01, 0.1, thickness_tests)
penetration = np.empty(thickness_tests)

start = time.perf_counter()
for i, thickness in enumerate(thicknesses):
    penetration[i] = simulate_transport(500, 200, thickness, int(1e5))
elapsed = time.perf_counter() - start

print("simulation run in", elapsed, "seconds")

plt.scatter(thicknesses, penetration)
plt.grid(visible=True)
plt.show()