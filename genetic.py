import copy
from problem_solution import Solution, Problem, CARS
import random
from solving import solve_flotilla

class GeneticSolver:
    def __init__(self, problem: Problem, population_size: int = 20, mutation_rate: float = 0.2):
        self.problem = problem
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.population: list[Solution] = []


    def _generate_random_path(self, start_node: int, max_steps: int, max_wait: int) -> list[tuple[int, int]]:
        path = [(start_node, random.randint(0, max_wait))]
        current = start_node
        
        for _ in range(random.randint(1, max_steps)):
            neighbors = list(self.problem.graph[current].keys())
            if not neighbors:
                break
            current = random.choice(neighbors)
            wait_time = random.randint(0, max_wait)
            path.append((current, wait_time))
        return path


    def create_initial_population(self):
        self.population.append(solve_flotilla(self.problem))
        for _ in range(self.population_size - 1):
            sol = solve_flotilla(self.problem)
            self.population.append(sol)


    def mutate(self, solution: Solution):
        for _ in range(3):
            car_to_mutate = random.choice(CARS)
            idx = random.randrange(len(solution.paths[car_to_mutate]))
            start_pos = self.problem.starting_positions[car_to_mutate]
            max_len = max(len(p) for c in CARS for p in solution.paths[c])
            max_wait = max(w for c in CARS for p in solution.paths[c] for _, w in p)
            solution.paths[car_to_mutate][idx] = self._generate_random_path(start_pos, max_len + 1, max_wait + 1)


    # def crossover(self, parent_a: Solution, parent_b: Solution) -> Solution:
    #     """Combines paths from two parents to create a child."""
    #     child_paths = {}
    #     for car in CARS:
    #         all_paths = parent_a.paths[car] + parent_b.paths[car]
    #         child_paths[car] = random.sample(all_paths, len(all_paths)//2)
    #     return Solution(self.problem, child_paths)


    def evolve(self, generations: int, verbose: bool = False) -> Solution:
        self.create_initial_population()

        for gen in range(generations):
            for sol in self.population:
                if not sol.makes_sense(verbose=False):
                    print(f"Invalid solution found in generation {gen}, skipping cost calculation.")
                    continue
                sol.calculate_cost_function()

            valid_solutions = [s for s in self.population if s.cost_values and s.is_correct()]
            if verbose:
                print(f"Generation {gen}: {len(valid_solutions)} of {len(self.population)}, {len(valid_solutions) / len(self.population) * 100:.2f}% valid")

            self.population = valid_solutions
            
            self.population.sort(key=lambda s: s.get_cost())

            best_cost = self.population[0].get_cost()
            print(f"Generation {gen}: {best_cost = }")

            old_parents = (len(self.population) + 9) // 10
            new_population = self.population[:old_parents]

            while len(new_population) < self.population_size:
                breeding_count = old_parents * 3
                parent_a = random.choice(self.population[:breeding_count])
                parent_b = random.choice(self.population[:breeding_count])
                child = copy.deepcopy(random.choice([parent_a, parent_b]))
                
                if random.random() < self.mutation_rate:
                    self.mutate(child)
                
                new_population.append(child)

            self.population = new_population

        return self.population[0]
    

def main():
    problem = Problem.random(20, 30, 1, 10, 8, 2, 4, seed=2137)
    print(f"{problem.check_validity(True) = }")

    solver = GeneticSolver(problem, population_size=100, mutation_rate=1.0)
    solution = solver.evolve(generations=200, verbose=True)

    print(f"{solution.makes_sense(verbose=True) = }")
    solution.calculate_cost_function(verbose=False)
    print(f"{solution.cost_values = }")
    print(f"{solution.is_correct() = }")
    print(f"{solution.get_cost() = }")


if __name__ == "__main__":
    main()