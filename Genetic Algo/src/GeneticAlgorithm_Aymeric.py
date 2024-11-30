import string
import textwrap
import random
import functools
from audioop import reverse

ALLELE_POOL = string.ascii_letters + ' ' + string.punctuation
TARGET_SOLUTION = "Ground control to major Tom. Planet earth is blue and there's nothing i can do"

class GeneticAlgorithm():

    class Individual():
        def __init__(self, chromosome):
            """
            :param chromosome: A string the same size as TARGET_SOLUTION
            """
            self.chromosome = chromosome
            self.fitness = self.get_fitness()
            
        def get_fitness(self):
            """
            :return: A numerical value being the fitness of the individual.
            the fitness is defined has the number of character that match/mismatch in
            character & position
            """


            #fitness = 0
            #for allele, target_char in zip(self.chromosome, TARGET_SOLUTION):
            #    fitness += 1 if allele is target_char else 0
            return functools.reduce(lambda fit, char: fit + (1 if char[0] is char[1] else 0),
                          zip(self.chromosome, TARGET_SOLUTION), 0)
        
        def get_chromosome(self):
            """
            :return: A string, the chromosome of the individual. 
            """
            return self.chromosome
        
    def __init__(self, pop_size = 500, pm = 0.01, elitism = 0.05):
        """
        :param pop_size: An integer defining the size of the population
        :param pm: A float defining the mutation rate
        :param elitism: A float definism the elitism rate
        """
        self.pop_size = pop_size
        self.allele_pool = ALLELE_POOL
        self.mutation_rate = pm
        self.elitism = elitism

    def generate_generation_zero(self):
        """
        :return: A list of size self.pop_size
                 containing randomly generated instances
                 of the class Individual
        """
        chromosome_size = len(TARGET_SOLUTION)
        chromosomes = textwrap.wrap(
            ''.join(random.choices(ALLELE_POOL, k=chromosome_size*self.pop_size)), chromosome_size
        )
        return [self.Individual(chromosome) for chromosome in chromosomes]


    def mutation(self, individual):
        """
        :param chromosome: An instance of the class Individual
                           whose chromosome is to mutate
        :return:  An instance of the class Individual
                  whose chromosome has been mutated
        """

        # Each gene has a probability pm to undergo a mutation
        mutated_chromosome = ''.join(
            [(allele if random.random() > self.mutation_rate
             else random.choice(ALLELE_POOL)) for allele in individual.chromosome]
        )
        return self.Individual(mutated_chromosome)
    
    def selection(self, population):
        """
        :param population : A list of instances of the class Individuals
        :return: The mating pool constructed from
                the 50% fittest individuals in the population
        """
        # note: // does an integer division -> instead of int(x/2)
        return sorted(population, key=lambda ind: ind.get_fitness(), reverse=True)[:self.pop_size//2]

    def create_offspring(self, parent1, parent2):
        """
        :param parent1: An instance of the class Individual
        :param parent2: An instance of the class Individual
        :return: Two chromosomes/strings created by
                single-point crossover of the parents'
                chromosomes
        """

        # crossover that switch at least one elem
        crossover = random.randint(1, len(TARGET_SOLUTION) - 2)
        chromosome1, chromosome2 = parent1.get_chromosome(), parent2.get_chromosome()
        offspring1 = chromosome1[:crossover] + chromosome2[crossover:]
        offspring2 = chromosome2[:crossover] + chromosome1[crossover:]

        return offspring1,offspring2
        
    
    def run_genetic_algorithm(self, seed, 
                              tol = 0.0,
                              display = True):
        """
        :param seed: An integer to set the random seed
        :param tol: A tolerance on the fitness function
        :param display: A boolean. If True, the fitness 
                        of the best performing individual
                        is displayed at the end of each 
                        generation
        """

        random.seed(seed)
        generation = 0

        # 1. Random generation of the initial population
        population = self.generate_generation_zero()
 

        # --- the convergence criteria --- #
        """
        Tp check for the next time, define specific convergence criteria
        """
        while population[0].get_fitness() < tol and generation < 200:
        
            if display:
                print("Generation {} : {} \n".format(
                    generation,
                    population[0].get_chromosome()))

            # 2. Creation of the mating pool
            mating_pool = self.selection(population)

            # 3. Apply the elistist strategy
            elit_fraction = int(self.pop_size * self.elitism)
            new_population = mating_pool[:elit_fraction]

            # 4. Continuing the breeding process until
            # the population is entirely renewed
            while len(new_population) < self.pop_size:
                    
                    # 4.1 Select the parent in the mating pool 
                    # random choices again


                    # 4.2 Make them reproduce
                    chromosome1, chromosome2 = self.create_offspring(*random.choices(mating_pool, k=2))
                    # 4.3 Mutate the offsprings
                    child1 = self.mutation(self.Individual(chromosome1))
                    child2 = self.mutation(self.Individual(chromosome2))

                    # 4.4 Append the new solutions to the new population
                    new_population += [child1, child2]
            

            # The (sorted) new population replace the previous one. 
            population = sorted(new_population, key= lambda x : x.get_fitness(), reverse=True)
            generation += 1

        if display: 
            print("Generation {} : {}, fitness = {} \n".format(
                    generation,
                    population[0].get_chromosome(), 
                    population[0].get_fitness()))

        return generation, population[0].fitness, population[0].get_chromosome()



# test run:

algo = GeneticAlgorithm(pm=0.1, elitism=0.1)
print()

import numpy as np
import matplotlib.pyplot as plt

# test for different mutation rate and p_m = 0.05 (base)
# should actually use the same seed for all
N = 6
averaging_sample = 3
elitisms = np.logspace(-4, -0.5, N)
convergence_time = np.empty(N)
for i, elitism in enumerate(elitisms):
    algo = GeneticAlgorithm(elitism=elitism, pop_size=1000, pm=0.05)
    for j in range(averaging_sample):
        res, check_fit, check_str = algo.run_genetic_algorithm(
            j,
            tol=len(TARGET_SOLUTION),
            display=False)
        convergence_time[i] += res
    print("done", elitism)
    convergence_time[i] /= averaging_sample


plt.semilogx(elitisms, convergence_time)
plt.grid(visible=True, which='both')
plt.title("convergence time vs elitism")
plt.ylabel("average number of generation")
plt.xlabel("elitism")
plt.show()
# put family name in the document name, max 15 pages least is the best
# send report for 7th december to Emily Delvaux

# if pm = 0.05 (base): no visible effect of elitism
