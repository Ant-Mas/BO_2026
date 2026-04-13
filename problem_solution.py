from dataclasses import dataclass, asdict
from graph_utils import Graph, dijkstra, generate_random_graph
import json
from queue import PriorityQueue
from math import inf
import random

# Graph = list[dict[int, int]]
CARS = ['a', 'f', 'p']

@dataclass
class Problem:
    graph: Graph
    situations: dict[int, set[str]]
    car_amounts: dict[str, int]
    starting_positions: dict[str, int]

    def check_validity(self, verbose: bool = False) -> bool:
        for v, cars in self.situations.items():
            if v >= len(self.graph):
                if verbose:
                    print(f"Invalid situation vertex: {v}")
                return False
            for car in cars:
                if car not in CARS:
                    if verbose:
                        print(f"Invalid car type in situation: {car}")
                    return False

        for car, amount in self.car_amounts.items():
            if car not in CARS:
                if verbose:
                    print(f"Invalid car type in car_amounts: {car}")
                return False
            if amount < 0:
                if verbose:
                    print(f"Negative amount for car type {car}: {amount}")
                return False

        for car, pos in self.starting_positions.items():
            if car not in CARS:
                if verbose:
                    print(f"Invalid car type in starting_positions: {car}")
                return False
            if pos < 0 or pos >= len(self.graph):
                if verbose:
                    print(f"Invalid starting position for car {car}: {pos}")
                return False
        
        for row in self.graph:
            for weight in row.values():
                if weight < 0:
                    if verbose:
                        print(f"Negative edge weight: {weight}")
                    return False

        dist, _ = dijkstra(self.graph, 0)
        if any(d == inf for d in dist):
            if verbose:
                print("Graph is not fully connected")
            return False

        return True


    def save(self, filename: str) -> None:
        data = asdict(self)
        data["situations"] = {k: list(v) for k, v in data["situations"].items()}
        with open(filename, "w") as f:
            json.dump(data, f)


    @staticmethod
    def load(filename: str) -> "Problem":
        with open(filename, "r") as f:
            data = json.load(f)
        
        data["situations"] = {int(k): set(v) for k, v in data["situations"].items()}
        data["graph"] = [{int(k): int(v) for k, v in dict.items()} for dict in data["graph"]]
        return Problem(**data)


    @staticmethod
    def random(num_vertices: int, num_edges: int, min_weight: int, max_weight: int, num_situations: int, min_car_amount: int, max_car_amount: int, seed=2137) -> "Problem":
        if num_vertices < num_situations:
            raise ValueError("Number of situations must be less than or equal to num of vertices")
        

        random.seed(seed)
        graph = generate_random_graph(num_vertices, num_edges, min_weight, max_weight)

        situations = dict()
        vertices = list(range(num_vertices))
        random.shuffle(vertices)
        def num_to_cars(n):
            cars = []
            pos = 0
            while n:
                if n & 1: cars.append(CARS[pos])
                n >>= 1
                pos += 1
            return cars
        for i in range(num_situations):
            random_cars = num_to_cars(random.randint(1, 7))
            situations[vertices[i]] = random_cars

        car_amounts = dict()
        for car in CARS:
            car_amounts[car] = random.randint(min_car_amount, max_car_amount)

        starting_positions = {car:random.randint(0, num_vertices-1) for car in CARS}

        return Problem(graph, situations, car_amounts, starting_positions)
    


@dataclass
class Solution:
    problem: Problem
    paths: dict[str, list[list[tuple[int, int]]]]
    cost_values: dict[int, int] | None = None


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
        if self.cost_values is None:
            raise RuntimeError("Cost values not calculated yet")
        if self.cost_values.keys() != self.problem.situations.keys():
            return False
        return True
    

    def get_cost(self) -> int:
        if self.cost_values is None:
            raise RuntimeError("Cost values not calculated yet")
        return sum(cost**2 for cost in self.cost_values.values())