# MATH-410 Monte-Carlo Project
This is the repository of some university project regarding Monte-Carlo algorithm for:
- neutron transport
- genetic algorithm

## Neutron transport

### Plan

A benchmarking code to test the simulation at the different levels of development, characterize each step from now on
Do multiple code file for the different versions of the codes, following the different steps:
1. Simple Monte-Carlo algorithm to compute the transmission probability, without variance reduction techniques
2. Add splitting strategies (+ russian roulette)
3. More efficient estimator than a counter
4. Add antithetic variates (for each sampling: take $\xi$ and $1 -  \xi$)
5. Add various biasing strategies (sample more the neutron going towards the other side)
6. Adaptation to variable macroscopic cross-sections (change in absorption-scattering ratio and total cross-section)
7. Randomization of composition

### Benchmarking

### Simulation

#### Simple counter
You simply need to iterate `population_size` times and follow the life of a neutron of initial position 0:
- Free flight, but it goes at an angle so its x-displacement is smaller than expected
- Check for a capture
- If it is scatter, sample isotropically the angle and start again

#### Splitting
We can define a weight for neutrons, but has they all still have the same for the moment, we can use a single variable:
`general_weight`. Every so often (at a given frequency), we split every neutron into several others, and the weight is
updated. To avoid too many unrepresentative neutrons, a russian roulette is performed beforehand.

#### Estimator
Each neutron now has a weight associated to it (starting with a single neutron of weight 1).
Rather than losing neutron in Absorption, we keep all of them but multiply their weights by the scattering probability.
Also, contribution is now gained by various estimation of the estimator at each point of the simulation

#### Antithetic variable
The uniform sampling is replaced with an antithetic sampling: half is $\xi$ the other $1 - \xi$ (had math proof)

#### Variance computation
$D^2(I) = D^2\left(\frac{1}{N} \sum_k h(n_k)\right)$ where $n_k$ are the incident neutrons,
$s^2 = \frac{1}{N} \sum_k (h(n_k))^2 - I^2$. Note that we need to know the result for each incident neutron at the end:
We keep track of their respective descendants to differentiate their contributions.