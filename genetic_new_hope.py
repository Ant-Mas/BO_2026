import copy
from problem_solution import Solution, Problem, CARS
import random
from solving import solve_given_order
from math import inf

class GeneticSolver:
    def __init__(self, problem: Problem, population_size: int = 20, mutation_rate: float = 0.2):
        self.problem = problem
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.population: list[list[int]] = []


    def create_initial_population(self):
        keys = self.problem.situations.keys()
        for _ in range(self.population_size):
            order = list(keys)
            random.shuffle(order)
            self.population.append(order)


    def mutate(self, solution: list[int]):
        return self._mutate_swap(solution)


    def _mutate_swap(self, solution: list[int]):
        i, j = random.sample(range(len(solution)), 2)
        solution[i], solution[j] = solution[j], solution[i]
        return solution
    
    
    def _mutate_reinsert(self, solution:list[int]):
        index = random.randint(0, len(solution) - 1)
        vertice = solution.pop(index)
        solution.insert(random.randint(0, len(solution) - 1), vertice)
        return solution


    def crossover(self, parent_a: Solution, parent_b: Solution) -> Solution:
        """Combines paths from two parents to create a child."""
        size = len(parent_a)
        child = [None] * size

        i, j = sorted(random.sample(range(size), 2))

        child[i:j] = parent_a[i:j]

        p2_idx = 0
        for k in range(size):
            if child[k] is None:
                while parent_b[p2_idx] in child:
                    p2_idx += 1
                child[k] = parent_b[p2_idx]

        return child


    def evolve(self, generations: int, verbose: bool = False) -> Solution:
        self.create_initial_population()
        costs = [inf] * self.population_size
        elitism = (len(self.population) + 9) // 10
        
        for gen in range(generations):
            for i, sol in enumerate(self.population):
                paths = solve_given_order(self.problem, sol)
                paths.calculate_cost_function()
                costs[i] = paths.get_cost() 
            
            sorted_pop = sorted(zip(costs, self.population))
            self.population = [sol for cost, sol in sorted_pop]

            best_cost = sorted_pop[0][0]
            avg_cost = sum(cost for cost, sol in sorted_pop) / self.population_size
            print(f"Generation {gen+1}: {best_cost = }, {avg_cost = }")

            new_population = self.population[:elitism]

            while len(new_population) < self.population_size:
                parent_a, parent_b = random.sample(self.population[:elitism*3], k=2)
                child = self.crossover(parent_a, parent_b)
                
                if random.random() < self.mutation_rate:
                    self.mutate(child)
                
                new_population.append(child)

            self.population = new_population

        return self.population[0]
    

def main():
    problem = Problem.random(100, 99, 1, 10, 30, 2, 2, seed=213)
    print(f"{problem.check_validity(True) = }")

    solver = GeneticSolver(problem, population_size=100, mutation_rate=0.4)
    solution = solver.evolve(generations=50, verbose=True)

    # print(f"{solution.makes_sense(verbose=True) = }")
    # solution.calculate_cost_function(verbose=False)
    # print(f"{solution.cost_values = }")
    # print(f"{solution.is_correct() = }")
    # print(f"{solution.get_cost() = }")


if __name__ == "__main__":
    main()