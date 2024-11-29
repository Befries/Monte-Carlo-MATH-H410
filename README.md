# MATH-410 Monte-Carlo Project
This is the repository of some university project regarding Monte-Carlo algorithm for:
- neutron transport
- genetic algorithm

## Neutron transport

### Plan

Do multiple code file for the different versions of the codes, following the different steps:
1. Simple Monte-Carlo algorithm to compute the transmission probability, without variance reduction techniques
2. A benchmarking code to test the simulation at the different levels of development, characterize each step from now on
3. Add splitting strategies (+ russian roulette)
4. More efficient estimator than a counter
5. Add antithetic variates (for each sampling: take $\xi$ and $1 -  \xi$)
6. Add various biasing strategies (sample more the neutron going towards the other side)
7. Adaptation to variable macroscopic cross-sections (change in absorption-scattering ratio and total cross-section)
8. Randomization of composition

### Benchmarking



### Simulation

#### Variance computation
$D^2(I) = D^2\left(\frac{1}{N} \sum_k h(n_k)\right)$ where $n_k$ are the incident neutrons,
$s^2 = \frac{1}{N} \sum_k (h(n_k))^2 - I^2$. Note that we need to know the result for each incident neutron at the end:
We keep track of their respective descendants to differentiate their contributions.