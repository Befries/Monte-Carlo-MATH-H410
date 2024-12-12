from componentBasedv2 import sample_time
import numpy as np
import matplotlib.pyplot as plt 

lamb = np.array([0.00001,0.0001,0.001,0.01,0.1,1])
time = np.empty(6)
for t in range(6) : 
    time[t] = sample_time(lamb[t],40)

fig, ax = plt.subplots()
ax.plot(lamb,time )
ax.set_xscale('log')
ax.set_yscale('log')
ax.set(xlabel='lambda', ylabel='sampled time',
       title='sampled time')
ax.grid()

fig.savefig("test.png")
plt.show()
print(time)