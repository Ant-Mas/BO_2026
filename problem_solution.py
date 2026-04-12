from dataclasses import dataclass, asdict
from graph_utils import get_closest, Graph, dijkstra
import json
from queue import PriorityQueue
from random import shuffle, seed
from math import inf

# Graph = list[dict[int, int]]
CARS = ['a', 'f', 'p']

@dataclass
class Problem:
    graph: Graph
    situations: dict[int, set[str]]
    car_amounts: dict[str, int]
    starting_positions: dict[str, int]


    def save_problem(this, filename: str) -> None:
        data = asdict(this)
        data["situations"] = {k: list(v) for k, v in data["situations"].items()}
        with open(filename, "w") as f:
            json.dump(data, f)


def load_problem(filename: str) -> Problem:
    with open(filename, "r") as f:
        data = json.load(f)
    
    data["situations"] = {int(k): set(v) for k, v in data["situations"].items()}
    data["graph"] = [{int(k): int(v) for k, v in dict.items()} for dict in data["graph"]]
    return Problem(**data)


@dataclass
class Solution:
    problem: Problem
    paths: dict[str, list[list[tuple[int, int]]]]
    cost_values: dict[int, int] = None


    def _check_fulfillment(self, v_to_check, unsolved, inhabitants, time) -> dict[int, int]:
        result = dict()
        for v in v_to_check:
            if v in unsolved:
                fulfilled = True
                for car in self.problem.situations[v]:
                    if inhabitants[v][car] == 0:
                        fulfilled = False
                        break
                if fulfilled:
                    result[v] = time
                    unsolved.remove(v)
        v_to_check.clear()
        return result
        

    def calculate_cost_function(self, verbose = False) -> dict[int, int]:
        graph = self.problem.graph
        inhabitants: list[dict[str, int]] = [{car:0 for car in CARS} for _ in graph]
        completion_times: dict[int, int] = dict()
        v_to_check: set[int] = set()
        unsolved = set(self.problem.situations.keys())

        # event =  (time_stamp, event_type, path, on_path_id, car)
        # A = (10, false, p_1, 2, 'a') - w momencie 10 przestań być w wierzchołku 2 z trasy p2
        # B = (12, true, p_1, 2, 'f') - w momencie 12 zacznij być w wierzchołku 2 z trasy p2
        event_queue = PriorityQueue()
        for car in CARS:
            for path in self.paths[car]:
                event_queue.put((0, True, path, 0, car))

        time: int = 0
        while not event_queue.empty() and len(unsolved) > 0:
            time_stamp, if_arrival, path, path_idx, car = event_queue.get()
            current_v, current_wait = path[path_idx]
            if verbose: print(f"[{time_stamp:<3}] v_{current_v} {'ARRIVE' if if_arrival else 'DEPART'} {car}")

            if time != time_stamp:
                new_completions = self._check_fulfillment(v_to_check, unsolved, inhabitants, time)
                completion_times |= new_completions
                time = time_stamp

            if if_arrival:
                if len(path) == path_idx + 1:
                    inhabitants[current_v][car] += 1
                    v_to_check.add(current_v)
                    continue
                if path[path_idx][1] == 0:
                    next_v = path[path_idx + 1][0]
                    if verbose: print(f"[{time_stamp:<3}] v_{current_v} DEPART {car}")
                    event_queue.put((time + graph[current_v][next_v], True, path, path_idx + 1, car))
                    continue
                inhabitants[current_v][car] += 1
                v_to_check.add(current_v)
                event_queue.put((time + current_wait, False, path, path_idx, car))
            else:
                next_v = path[path_idx + 1][0]
                inhabitants[current_v][car] -= 1
                event_queue.put((time + graph[current_v][next_v], True, path, path_idx + 1, car))

        new_completions = self._check_fulfillment(v_to_check, unsolved, inhabitants, time)
        completion_times |= new_completions

        self.cost_values = completion_times
        return completion_times


    def makes_sense(self, verbose = False) -> bool:
        for car in CARS:
            if len(self.paths[car]) != self.problem.car_amounts[car]:
                if verbose: print(f'Given: {self.paths[car]} paths of type <{car}> expected: {self.problem.car_amounts[car]}')
                return False
            for path in self.paths[car]:
                if path[0][0] != self.problem.starting_positions[car]:
                    if verbose: print(f'Wrong starting position for type <{car}>')
                    return False
                for idx, (v, _) in enumerate(path[1:]):
                    prev, _ = path[idx]
                    if v not in self.problem.graph[prev].keys():
                        if verbose: print(f'Not a path in the graph: {path}')
                        return False
        return True


    def is_correct(self) -> bool:
        if self.cost_values.keys() != self.problem.situations.keys():
            return False
        return True
    

    def get_cost(self) -> int:
        return sum(cost**2 for cost in self.cost_values.values())

                

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

def solve_random_order(problem: Problem, seed_int = 2137):
    seed(seed_int)
    order = [k for k in problem.situations.keys()]
    shuffle(order)

    cars_a = [(problem.starting_positions['a'], 0, [(problem.starting_positions['a'], 0)]) for _ in range(problem.car_amounts['a'])]
    cars_f = [(problem.starting_positions['f'], 0, [(problem.starting_positions['f'], 0)]) for _ in range(problem.car_amounts['f'])]
    cars_p = [(problem.starting_positions['p'], 0, [(problem.starting_positions['p'], 0)]) for _ in range(problem.car_amounts['p'])]

    # cars_a = [(problem.starting_positions['a'], 0, []) for _ in range(problem.car_amounts['a'])]
    # cars_f = [(problem.starting_positions['f'], 0, []) for _ in range(problem.car_amounts['f'])]
    # cars_p = [(problem.starting_positions['p'], 0, []) for _ in range(problem.car_amounts['p'])]
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
            if car[1] == situation:
                car[2][-1] = (car[2][-1][0], total_time - car[1])
                cars[type][fastest_id[type]] = (situation, total_time, car[2])
                continue

            node = prev[car[0]]
            while node != situation:
                car[2].append((node, 0))
                path.append(node)
                node = prev[node]
            car[2].append((situation, total_time - car[1] - dist[car[0]]))
            cars[type][fastest_id[type]] = (situation, total_time, car[2])
        
    for type in CARS:
        for i in range(len(cars[type])):
            cars[type][i] = cars[type][i][2]

    return Solution(problem, cars)
        
            
            
        


if __name__ == "__main__":
    n = 5
    E = [(0, 1, 13), (1, 2, 17), (1, 3, 1), (1, 4, 1), (3, 4, 1)]
    G = [dict() for _ in range(n)]
    for u, v, dist in E:
        G[u][v] = dist 
        G[v][u] = dist
    S = {3: {'a', 'f'}, 2: {'a', 'f', 'p'}, 1:{'p'}}
    N = {"a": 1, "f": 1, "p": 1}
    Vs = {"a": 0, "f": 2, "p": 1}

    problem = Problem(G, S, N, Vs)
    # problem.save_problem('test.json')
    # problem = load_problem('test.json')
    # print(problem)


    # solution = solve_flotilla(problem)
    solution = solve_random_order(problem)

    # print(solution)
    # for type, paths in solution.paths.items():
    #     print(type)
    #     for path in paths:
    #         print(path)
    print(f"{solution.makes_sense(verbose=True) = }")
    print(f"cost_values = {solution.calculate_cost_function(verbose=True)}")
    print(f"{solution.is_correct() = }")
    print(f"{solution.get_cost() = }")
