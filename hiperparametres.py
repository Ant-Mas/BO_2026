import optuna
from genetic_new_hope import GeneticSolver
from problem_solution import Solution, Problem
import time
import math

PROBLEM = Problem.random(60, 400, 1, 10, 20, 2, 5, seed=213)

def objective(trial: optuna.Trial):
    problem = PROBLEM
    print(f"{problem.check_validity(True) = }")

    population_size = 50 # trial.suggest_int("Population size", 10, 150)
    mutation_rate = trial.suggest_float("Mutation rate", 0.0, 1.0)
    generations = 50 # trial.suggest_int("Generations", 5, 100)

    solver = GeneticSolver(problem, population_size, mutation_rate)
    start = time.perf_counter()
    solution = solver.evolve(generations, verbose=False)
    end = time.perf_counter()

    solution.calculate_cost_function()
    cost = solution.get_cost()
    elapsed = end - start

    return cost * cost * math.sqrt(elapsed)

study = optuna.create_study()
study.optimize(objective, n_trials=50)

print(study.best_params)  # E.g. {'x': 2.002108042}