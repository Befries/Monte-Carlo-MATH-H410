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
3. More efficient estimator than a counter and Simple bias
4. Add antithetic variates (for each sampling: take $\xi$ and $1 -  \xi$)
5. Add various biasing strategies (sample more the neutron going towards the other side)
6. Adaptation to variable macroscopic cross-sections (change in absorption-scattering ratio and total cross-section)
7. Randomization of composition

### Benchmarking

#### Efficiency
The efficiency of a monte-carlo simulation can be calculated as $E  = 1 / (s^2 \tau)$ where $s^2$ is the variance of the
estimation for one incident neutron ($D^2(I)/N$) and $\tau$ the average run time for a neutron (total time $/N$).

For small thickness ($0 \rightarrow 10$), the efficiency is roughly the same for the simple counter and the more
advanced variant. However, for larger thickness, the simple counter lacks precision for small amounts of incident neutrons
and isn't able to evaluate the probability.

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

#### Estimator and Simple bias
(No speed dependence)
Each neutron now has a weight associated to it (starting with a single neutron of weight 1).
Rather than losing neutron in Absorption, we keep all of them but multiply their weights by the scattering probability:
$w_{k+1} = w_k p_{\text{scatter}}$.

Also, contribution is now gained by various estimation of the estimator at each point of the simulation:
We'd like to estimate the reaction rate
$$R = \int f(P)\psi(P) dP = \int \phi(P) \delta(x - L)H(\Omega_x) dP$$
Where $H(\Omega_x)$ is the heaviside function applied to the director cosine (only neutron going forward contributes).
As $\psi(P) = \Sigma_t \phi(P)$, we can deduce that $f(P) = \frac{1}{\Sigma_t}\delta(x - L)H(\Omega_x)$

The reaction rate is given by the total score of the source:
$$R = \int Q(P) M_1(P) dP, \qquad M_1(P) = \int T(P \rightarrow P')f(P') dP' + \int L(P \rightarrow P') M_1(P') dP'$$
The integral over the source Q is simply the sum over the contribution of the incident neutrons 
($Q(P) = N\delta(x)\delta(\Omega_x - 1)$), the probability is given by the reaction rate normalized by the total source
meaning $p = R/N$. The first term in the definition of the score is $I_0(P) = \int T(P \rightarrow P')f(P') dP'$, the
estimation of the score of a neutron that would start from $P$ and have no collision until $P'$.

The transport Kernel $T(P \rightarrow P') = \Sigma_t e^{-\Sigma_t |x-x'|/\Omega_x}\delta(\Omega_x - \Omega_x')$, enables to
compute this estimator:
$$I_0(P) = \int T(P \rightarrow P')f(P') dP' = H(\Omega_x)\exp\left(-\Sigma_t \frac{L-x}{\Omega_x}\right)$$

Another way to understand this, is that for a neutron that goes forward (those who have a chance to escape), 
if we consider all of its possible free flights, the estimator is the fraction that passes the wall. It is given by the 
integral of the PDF over the escaped portion 
$$\int_{L}^{\infty} \frac{\Sigma_t}{\Omega}\exp\left(-\Sigma_t \frac{x'-x}{\Omega_x}\right) = 
\exp\left(-\Sigma_t \frac{x'-x}{\Omega_x}\right), \quad \Omega_x > 0$$
We can therefore understand this as: "The neutron had a fraction of itself that escaped", the remaining weight of the
neutron is simply the complementary (fraction that stayed inside). In the same way, instead of eliminating neutron
to simulate capture, we multiply the weight by the probability to continue the journey, meaning the scattering probability

For Neutrons that goes backward, they have no contribution but we can in the same way keep them and diminish their weight
by the fraction that would have stayed in: $e^{-\Sigma_t \frac{x}{\Omega_x}}$

Now as we consider that the neutron stays inside (with its diminished weight), we have to sample a free flight accordingly.
We have to re-normalize the PDF (reasoning for forward neutrons, same for backward neutrons):

$$\int_0^{L-x} A\frac{\Sigma_t}{\Omega_x}\exp\left(-\Sigma_t s / \Omega_x\right) ds \: \Rightarrow \: A =
\frac{1}{\left(1 - \exp\left(-\Sigma_t (L-x)/ \Omega_x\right)\right)}$$

Then you simply need to inverse the CDF: $F(s) = A(1 - \exp\left(-\Sigma_t s / \Omega_x\right)) = \xi$ which gives
$$s = F^{-1}(\xi) = - \frac{\Omega_x}{\Sigma_t} \ln\left[1 -
(1 - \exp[-\Sigma_t (L-x)/ \Omega_x])\xi\right]$$

The change of PDF for the free flight and scattering is a simple bias, we remove the possibility of losing the neutron
and modify their weight to remove the bias.


#### Antithetic variable
The uniform sampling is replaced with an antithetic sampling: half is $\xi$ the other $1 - \xi$ (had math proof)

#### Variance computation
$D^2(I) = D^2\left(\frac{1}{N} \sum_k h(n_k)\right)$ where $n_k$ are the incident neutrons,
$s^2 = \frac{1}{N} \sum_k (h(n_k))^2 - I^2$. Note that we need to know the result for each incident neutron at the end:
We keep track of their respective descendants to differentiate their contributions.

One could remark that the variance evolves in the same way as the transmission probability as a function of the thickness
This is perfectly normal, consider the simple counter code: the result of each neutron can be $h(n_k) = 0, 1$, therefore
$(h(n_k))^2 = h(n_k)$.

$$s^2 = \frac{1}{N} \sum_k (h(n_k))^2 - I^2 = \frac{1}{N} \sum_k h(n_k) - I^2 = I - I^2 = I (1 - I)$$

For a small transmission probability, $1 - I \approx 1$, therefore $s^2 \approx I$, which explains this tendency for
the counter algorithm
