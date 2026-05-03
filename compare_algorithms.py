import time
import matplotlib.pyplot as plt
from problem_solution import Problem
from genetic_new_hope import GeneticSolver
from bee_solver import BeeSolver


def compare_solvers(
        num_vertices: int = 60,
        num_edges: int = 400,
        min_weight: int = 1,
        max_weight: int = 10,
        num_situations: int = 20,
        min_car_amount: int = 2,
        max_car_amount: int = 5,
        seed: int = 42,
        generations: int = 40,
        population_size: int = 50,
        mutation_rate: float = 0.25,
        bees_cnt: int = 30,
        good_elite_cnt: int = 10,
        elite_cnt: int = 3,
        local_elite_cnt: int = 10,
        local_good_cnt: int = 4
):
    problem = Problem.random(
        num_vertices=num_vertices,
        num_edges=num_edges,
        min_weight=min_weight,
        max_weight=max_weight,
        num_situations=num_situations,
        min_car_amount=min_car_amount,
        max_car_amount=max_car_amount,
        seed=seed
    )

    if not problem.check_validity():
        print("Problem is not valid")
        return

    # Genetic
    ga_solver = GeneticSolver(problem, population_size=population_size, mutation_rate=mutation_rate)

    start_time_ga = time.perf_counter()
    ga_solution = ga_solver.evolve(generations=generations, save_history=True, verbose=False)
    ga_solution.calculate_cost_function()
    end_time_ga = time.perf_counter()

    time_ga = end_time_ga - start_time_ga
    cost_ga = ga_solution.get_cost()

    ga_best_costs = [h[0] for h in ga_solver.history]

    # Bee
    bee_solver = BeeSolver(problem, bees_cnt=bees_cnt, good_elite_cnt=good_elite_cnt, elite_cnt=elite_cnt,
                           local_elite_cnt=local_elite_cnt, local_good_cnt=local_good_cnt)

    start_time_ba = time.perf_counter()
    ba_solution = bee_solver.evolve(iterations=generations, verbose=False)
    end_time_ba = time.perf_counter()

    time_ba = end_time_ba - start_time_ba
    cost_ba = ba_solution.get_cost()

    ba_best_costs = [h[0] for h in bee_solver.history]

    print("=" * 40)
    print(f"Genetic alghoritm:")
    print(f"  Time: {time_ga:.3f} s")
    print(f"  Cost: {cost_ga}")
    print(f"  Is correct?: {ga_solution.is_correct()}")

    print(f"\nBee alghoritm:")
    print(f"  Time: {time_ba:.3f} s")
    print(f"  Cost: {cost_ba}")
    print(f"  Is correct?: {ba_solution.is_correct()}")

    plt.figure(figsize=(10, 6))

    plt.plot(ga_best_costs, label=f'Genetic (cost: {cost_ga})', color='blue', marker='o', markersize=4)
    plt.plot(ba_best_costs, label=f'Bee (cost: {cost_ba})', color='orange', marker='s', markersize=4)

    plt.title('Alghoritms compare', fontsize=14)
    plt.xlabel('Generations', fontsize=12)
    plt.ylabel('Cost', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(fontsize=12)

    plt.xticks(range(0, generations + 1, max(1, generations // 10)))

    plt.tight_layout()
    plt.show()


def example1():
    compare_solvers(
        seed=78,
        generations=50,
        population_size=70,
        mutation_rate=0.25,
        bees_cnt=30,
        good_elite_cnt=10,
        elite_cnt=3,
        local_elite_cnt=10,
        local_good_cnt=4
    )


def example2():
    compare_solvers(
        seed=67,
        generations=50,
        mutation_rate=0.5,
        population_size=100,
        bees_cnt=50,
        good_elite_cnt=7,
        elite_cnt=3,
        local_elite_cnt=7,
        local_good_cnt=3
    )

if __name__ == "__main__":
    compare_solvers()
    example1()
    example2()
