import time
import matplotlib.pyplot as plt
from problem_solution import Problem
from bee_solver import BeeSolver


def eval_bee_solver(
        problem: Problem,
        generations: int = 40,
        bees_cnt: int = 30,
        good_elite_cnt: int = 10,
        elite_cnt: int = 3,
        local_elite_cnt: int = 10,
        local_good_cnt: int = 4
):
    bee_solver = BeeSolver(problem, bees_cnt=bees_cnt, good_elite_cnt=good_elite_cnt,
                           elite_cnt=elite_cnt, local_elite_cnt=local_elite_cnt, local_good_cnt=local_good_cnt)

    start_time_ba = time.perf_counter()
    ba_solution = bee_solver.evolve(iterations=generations, verbose=False)
    end_time_ba = time.perf_counter()

    time_ba = end_time_ba - start_time_ba

    ba_solution.calculate_cost_function()
    cost_ba = ba_solution.get_cost()

    ba_best_costs = [h[0] for h in bee_solver.history]

    print(f"  Time: {time_ba:.3f} s | Cost: {cost_ba} | Is correct?: {ba_solution.is_correct()}")

    return time_ba, cost_ba, ba_solution, ba_best_costs


def main():
    problem = Problem.random(
        num_vertices=60,
        num_edges=400,
        min_weight=1,
        max_weight=20,
        num_situations=20,
        min_car_amount=3,
        max_car_amount=6,
        seed=676967
    )

    if not problem.check_validity():
        print("Problem is not valid")
        return

    generations = 40

    configurations = [
        {
            "name": "Zbalansowany",
            "params": {"bees_cnt": 30, "good_elite_cnt": 10, "elite_cnt": 3, "local_elite_cnt": 10, "local_good_cnt": 4}
        },
        {
            "name": "Dużo losowości",
            "params": {"bees_cnt": 100, "good_elite_cnt": 5, "elite_cnt": 2, "local_elite_cnt": 2, "local_good_cnt": 1}
        },
        {
            "name": "Wiele pszczół koło elity",
            "params": {"bees_cnt": 10, "good_elite_cnt": 5, "elite_cnt": 2, "local_elite_cnt": 30, "local_good_cnt": 15}
        },
        {
            "name": "Tylko elitarne wyniki",
            "params": {"bees_cnt": 30, "good_elite_cnt": 3, "elite_cnt": 3, "local_elite_cnt": 40, "local_good_cnt": 0}
        },
        {
            "name": "Rój",
            "params": {"bees_cnt": 60, "good_elite_cnt": 15, "elite_cnt": 5, "local_elite_cnt": 20, "local_good_cnt": 8}
        }
    ]

    plt.figure(figsize=(12, 7))
    markers = ['o', 's', '^', 'D', 'v']
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

    results_summary = []

    print(f"Testowanie {len(configurations)} wariantów")

    for idx, config in enumerate(configurations):
        print(f"\n{config['name']}")

        t, cost, sol, history = eval_bee_solver(
            problem,
            generations=generations,
            **config["params"]
        )

        results_summary.append({
            "name": config["name"],
            "time": t,
            "cost": cost
        })

        plt.plot(history, label=f"{config['name']} (Koszt: {cost})",
                 color=colors[idx], marker=markers[idx], markersize=5, linewidth=2, alpha=0.85)


    plt.title('Porównanie strategii Algorytmu Pszczelego', fontsize=16, fontweight='bold')
    plt.xlabel('Generacje', fontsize=12)
    plt.ylabel('Koszt', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(fontsize=11)

    plt.xticks(range(0, generations + 1, max(1, generations // 10)))
    plt.tight_layout()

    print("\n" + "=" * 65)
    print(" PODSUMOWANIE WYNIKÓW (CZAS vs KOSZT)")
    print("=" * 65)
    print(f"{'Konfiguracja':<40} | {'Czas [s]':<10} | {'Koszt':<10}")
    print("-" * 65)
    for res in results_summary:
        print(f"{res['name']:<40} | {res['time']:<10.3f} | {res['cost']:<10}")
    print("=" * 65)

    plt.show()


if __name__ == "__main__":
    main()
