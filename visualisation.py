from problem_solution import Solution, Problem
import matplotlib.pyplot as plt
from genetic_new_hope import GeneticSolver


def show_costs(history: list[tuple[int, float, Solution]]):
    best_costs = [b for b, _, _ in history]
    avg_costs = [a for _, a, _ in history]

    plt.plot(best_costs, label='Best')
    plt.plot(avg_costs, label='Average')

    plt.xlabel("Generation")
    plt.ylabel("Cost")
    plt.legend()

    plt.show()


if __name__ == "__main__":
    problem = Problem.random(30, 100, 1, 10, 20, 2, 5, seed=213)
    print(f"{problem.check_validity(True) = }")
    history = []

    solver = GeneticSolver(problem, population_size=30, mutation_rate=0.5)
    solution = solver.evolve(generations=100, verbose=True, history=history)

    show_costs(history)


