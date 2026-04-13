
from graph_utils import get_closest, dijkstra
from problem_solution import Problem, Solution, CARS
import random
from math import inf


def solve_flotilla(problem: Problem):
    paths = {'a': [(problem.starting_positions['a'], 0)]}

    dij_path, _ = get_closest(problem.graph, problem.starting_positions['a'], [problem.starting_positions['f']])
    p_wait = 0
    f_wait = 0
    for idx, current_v in enumerate(dij_path[1:]):
        prev_v = dij_path[idx]
        paths['a'].append((current_v, 1))
        f_wait += problem.graph[prev_v][current_v] + 1
        p_wait += problem.graph[prev_v][current_v] + 1


    paths['f'] = [(problem.starting_positions['f'], f_wait)]
    dij_path, _ = get_closest(problem.graph, problem.starting_positions['f'], [problem.starting_positions['p']])
    for idx, current_v in enumerate(dij_path[1:]):
        prev_v = dij_path[idx]
        paths['f'].append((current_v, 1))
        p_wait += problem.graph[prev_v][current_v] + 1
    paths['a'].extend(paths['f'][1:])

    paths['p'] = [(problem.starting_positions['p'], p_wait)]

    to_solve = set(problem.situations.keys())
    for _ in range(len(to_solve)):
        current = paths['p'][-1][0]
        dij_path, _ = get_closest(problem.graph, current, to_solve)
        to_solve.remove(dij_path[-1])
        for v in dij_path[1:]:
            paths['p'].append((v, 1))
    paths['a'].extend(paths['p'][1:])
    paths['f'].extend(paths['p'][1:])

    return Solution(
        problem,
        {car: [paths[car] for _ in range(problem.car_amounts[car])] for car in CARS}
    )


def solve_random_order(problem: Problem, seed = 2137):
    random.seed(seed)
    order = [k for k in problem.situations.keys()]
    random.shuffle(order)
    return solve_given_order(problem, order)

def solve_given_order(problem: Problem, order:list[int]) -> Solution:
    cars_a = [(problem.starting_positions['a'], 0, [(problem.starting_positions['a'], 0)]) for _ in range(problem.car_amounts['a'])]
    cars_f = [(problem.starting_positions['f'], 0, [(problem.starting_positions['f'], 0)]) for _ in range(problem.car_amounts['f'])]
    cars_p = [(problem.starting_positions['p'], 0, [(problem.starting_positions['p'], 0)]) for _ in range(problem.car_amounts['p'])]

    cars = {
        'a': cars_a,
        'f': cars_f,
        'p': cars_p
    }

    for situation in order:
        needed = problem.situations[situation]
        dist, prev = dijkstra(problem.graph, situation)
        fastest_time = dict()
        fastest_id = dict()
        for type in needed:
            fastest_time[type] = inf
            fastest_id[type] = -1
            for i, car in enumerate(cars[type]):
                time = car[1] + dist[car[0]]
                if(time < fastest_time[type]):
                    fastest_time[type] = time
                    fastest_id[type] = i

        total_time = max(fastest_time.values()) + 1

        for type in needed:
            path = []
            car = cars[type][fastest_id[type]]
            if car[0] == situation:
                car[2][-1] = (car[2][-1][0], total_time - car[1] + car[2][-1][1])
                cars[type][fastest_id[type]] = (situation, total_time, car[2])
                continue

            node = prev[car[0]]
            while node != situation:
                car[2].append((node, 0))
                path.append(node)
                node = prev[node]
            car[2].append((situation, total_time - car[1] - dist[car[0]]))
            cars[type][fastest_id[type]] = (situation, total_time, car[2])
      
    result_paths = dict()
    for type in CARS:
        result_paths[type] = []
        for i in range(len(cars[type])):
            result_paths[type].append(cars[type][i][2])

    return Solution(problem, result_paths)#cars)


if __name__ == "__main__":
    n = 5
    E = [(0, 1, 13), (1, 2, 17), (1, 3, 1), (1, 4, 1), (3, 4, 1)]
    G = [dict() for _ in range(n)]
    for u, v, dist in E:
        G[u][v] = dist 
        G[v][u] = dist
    S = {3: {'a', 'f'}, 2: {'a', 'f', 'p'}, 1:{'p'}}
    N = {"a": 1, "f": 1, "p": 1}
    Vs = {"a": 0, "f": 3, "p": 1}

    # problem = Problem(G, S, N, Vs)
    # problem.save_problem('test.json')
    # problem = load_problem('test.json')
    problem = Problem.random(50, 200, 1, 10, 15, 2, 4)
    print(f"{type(problem) = }")
    print(f"{problem.check_validity(True) = }")


    # solution = solve_flotilla(problem)
    solution = solve_random_order(problem)

    # print(solution)
    # for type, paths in solution.paths.items():
    #     print(type)
    #     for path in paths:
    #         print(path)
    print(f"{solution.makes_sense(verbose=True) = }")
    solution.calculate_cost_function(verbose=False)
    print(f"{solution.cost_values = }")
    print(f"{solution.is_correct() = }")
    print(f"{solution.get_cost() = }")
