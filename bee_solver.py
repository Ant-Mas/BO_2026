import random
import copy
from problem_solution import Solution, Problem
from solving import solve_given_order


def get_neighborhood(order: list[int], intensity: int = 1) -> list[int]:
    """
    Szukanie sąsiadującego rozwiązania. Mutacja - swap.
    :param order: kolejność zdarzeń
    :param intensity: jak mocno zmieniamy oryginalną kolejność (1 = jedna zamiana)
    """
    neighbor = copy.copy(order)
    for _ in range(intensity):
        i, j = random.sample(range(len(neighbor)), 2)
        neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
    return neighbor


class BeeSolver:
    def __init__(self,
                 problem: Problem,
                 bees_cnt: int = 30,
                 good_elite_cnt: int = 10,
                 elite_cnt: int = 4,
                 local_elite_cnt: int = 15,
                 local_good_cnt: int = 10,
                 ):
        """
        Solver wykorzystujący algorytm pszczeli.
        :param problem: Problem
        :param bees_cnt: Liczba pszczół
        :param good_elite_cnt: Liczba dobrych i elitarnych pszczół
        :param elite_cnt: Liczba elitarnych pszczół
        :param local_elite_cnt: Liczba iteracji dla elitarnych pszczół
        :param local_good_cnt: Liczba iteracji dla dobrych pszczół
        """
        self.problem = problem
        self.bees_cnt = bees_cnt
        self.good_elite_cnt = max(1, min(good_elite_cnt, bees_cnt))
        self.elite_cnt = max(1, min(elite_cnt, self.good_elite_cnt))
        self.local_elite_cnt = local_elite_cnt
        self.local_good_cnt = local_good_cnt
        self.history: list[tuple[int, float, Solution]] = []

    def _evaluate_cost(self, order: list[int]) -> float:
        solution = solve_given_order(self.problem, order)
        solution.calculate_cost_function()
        return solution.get_cost()

    def evolve(self, iterations: int, verbose: bool = False) -> Solution:
        # Inicjalizacja populacji
        keys = list(self.problem.situations.keys())
        population = []
        for _ in range(self.bees_cnt):
            order = copy.copy(keys)
            random.shuffle(order)
            cost = self._evaluate_cost(order)
            population.append({"order": order, "cost": cost})

        for gen in range(iterations):
            population.sort(key=lambda x: x["cost"])

            next_generation = []

            # Faza elitarnych pszczół
            for i in range(self.elite_cnt):
                best_site = population[i]
                for _ in range(self.local_elite_cnt):
                    neighbor_order = get_neighborhood(best_site["order"], intensity=1)
                    neighbor_cost = self._evaluate_cost(neighbor_order)
                    if neighbor_cost < best_site["cost"]:
                        best_site = {"order": neighbor_order, "cost": neighbor_cost}
                next_generation.append(best_site)

            # Faza dobrych pszczół
            for i in range(self.elite_cnt, self.good_elite_cnt):
                best_site = population[i]
                for _ in range(self.local_good_cnt):
                    neighbor_order = get_neighborhood(best_site["order"], intensity=2)
                    neighbor_cost = self._evaluate_cost(neighbor_order)
                    if neighbor_cost < best_site["cost"]:
                        best_site = {"order": neighbor_order, "cost": neighbor_cost}
                next_generation.append(best_site)

            # Faza pozostałych pszczół - szukanie losowe
            remaining_scouts = self.bees_cnt - self.good_elite_cnt
            for _ in range(remaining_scouts):
                order = copy.copy(keys)
                random.shuffle(order)
                cost = self._evaluate_cost(order)
                next_generation.append({"order": order, "cost": cost})

            # Update aktualnej populacji rozwiązań
            population = next_generation
            population.sort(key=lambda x: x["cost"])

            best_current_cost = population[0]["cost"]
            if verbose:
                print(f"Iteration {gen + 1:03d} | Best cost: {best_current_cost}")
            avg_cost = sum(p["cost"] for p in population) / len(population)

            best_sol_object = solve_given_order(self.problem, population[0]["order"])
            self.history.append((best_current_cost, avg_cost, best_sol_object))

        best_overall_order = population[0]["order"]
        final_solution = solve_given_order(self.problem, best_overall_order)
        final_solution.calculate_cost_function()

        return final_solution


def main():
    problem = Problem.random(
        num_vertices=60,
        num_edges=400,
        min_weight=1,
        max_weight=10,
        num_situations=20,
        min_car_amount=2,
        max_car_amount=5,
        seed=42
    )
    print(f"Problem valid: {problem.check_validity()}")

    solver = BeeSolver(problem, bees_cnt=20, good_elite_cnt=8, elite_cnt=3, local_elite_cnt=10, local_good_cnt=4)

    best_solution = solver.evolve(iterations=30, verbose=True)

    print(f"\nMake sense? {best_solution.makes_sense()}")
    print(f"Cost values: {best_solution.cost_values}")
    print(f"Cost: {best_solution.get_cost()}")


if __name__ == "__main__":
    main()
