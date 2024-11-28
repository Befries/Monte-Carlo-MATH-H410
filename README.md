# MATH-410 Monte-Carlo Project
This is the repository of some university project regarding Monte-Carlo algorithm for:
- neutron transport
- genetic algorithm

## Neutron transport

### Benchmarking


### Simulation
The logic should be written to ensure that:
- Large amount of neutron are processed at the same time to facilitate vectorization and avoid the use of python
to process large amount of data (numpy will do it faster)
- The variance should be easily extracted

#### Variance computation
The amount of neutron passing through the wall, is the reaction rate $R$ of neutron crossing the wall at $x=L$. 
From the view point of a Neumann series, one can write:
$$I = R = \int f(P) \psi(p) dP = \sum_{j = 0}^{\infty} \int f(P) \psi_j(P)dP 
= \sum_{j = 0}^{\infty} R_j =\sum_{j = 0}^{\infty} I_j$$

Meaning that the total estimation $I$ is a sum of estimations $I_j$ for $j$ collisions. Therefore 
$D^2(I) = \sum_j D^2(I_j)$ (independent evaluation between collisions). Now, one can estimate $\frac{1}{N} s^2 = D^2(I)$
with the estimator:
$$\frac{1}{N}\bar{\sigma}^2  =
\sum_{j} \frac{1}{N} \left(\frac{1}{N} \sum_k \left(f(x_{jk})w(x_{jk})\right)^2 - \bar{I}_j^2 \right)
\Leftrightarrow \bar{\sigma}^2 = \frac{1}{N} \sum_{j, k} \left(f(x_{jk})w(x_{jk})\right)^2 - \sum_j \bar{I}_j^2$$