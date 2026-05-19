from genetic_new_hope import GeneticSolver
import matplotlib.pyplot as plt
from problem_solution import Problem
from genetic_new_hope import GeneticSolver
from bee_solver import BeeSolver

def compare_solvers(solvers: list[GeneticSolver | BeeSolver], solver_names: list[str], generations: int, tries: int = 1):

    plt.figure(figsize=(10, 6))
    # def evolve(self, generations: int, save_history: bool = False, verbose: bool = False) -> Solution:
    # def evolve(self, iterations: int, verbose: bool = False) -> Solution:
    
    for name, solver in zip(solver_names, solvers):
        print(f"Now running {name}")
        best_avg = []
        best_costs = []
        for i in range(tries):
            solver.evolve(generations)
            print(f"{i} out of {tries}")
            best_costs.append([h[0] for h in solver.history])
            solver.reset()
        for i in range(len(best_costs[0])):
            best_avg.append(sum(best_costs[j][i] for j in range(tries)) / tries)

        print()
        plt.plot(best_avg, label=f'{name} (minimal cost: {min(min(best_costs[i]) for i in range(tries))})', markersize=4)

    plt.xlabel('Generations', fontsize=12)
    plt.ylabel('Cost', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(fontsize=12)

    plt.xticks(range(0, generations + 1, max(1, generations // 10)))

    plt.tight_layout()
    plt.show()
    pass

def compare_mutation_rates():
        problem = Problem.random(
        num_vertices=60,
        num_edges=150,
        min_weight=1,
        max_weight=10,
        num_situations=15,
        min_car_amount=2,
        max_car_amount=4,
        seed=2137
        )
        solvers = []
        names = []
        for mutation_rate in [0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0]:
             solvers.append(GeneticSolver(problem, population_size=40, mutation_rate=mutation_rate))
             names.append(f"Rate = {mutation_rate}")
        compare_solvers(solvers, names, 50, 5)

def compare_mutation_modes():
        problem = Problem.random(
        num_vertices=60,
        num_edges=200,
        min_weight=1,
        max_weight=10,
        num_situations=20,
        min_car_amount=2,
        max_car_amount=4,
        seed=2137
        )
        solvers = []
        names = []
        for mutation_mode in ["swap", "reinsert"]:
             solvers.append(GeneticSolver(problem, population_size=40, mutate_mode=mutation_mode, mutation_rate=0.5))
             names.append(f"Mode = {mutation_mode}")
        compare_solvers(solvers, names, 50, 5)

def main():
    # compare_mutation_rates()
    compare_mutation_modes()

if __name__ == "__main__":
    main()