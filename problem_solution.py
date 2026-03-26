from dataclasses import dataclass
from graph_utils import * 

# Graph = list[dict[int, int]]
CARS = ['a', 'f', 'p']

@dataclass
class Problem:
    G: Graph
    S: dict[int, set[str]]
    N: dict[str, int]
    Vs: dict[str, int]


@dataclass
class Solution:
    problem: Problem
    P: dict[str, list[list[tuple[int, int]]]]

    def calculate_cost_function(self, verbose=False) -> list[int]:
        graph = self.problem.G
        vertice_inhabitants: list[dict[str, int]] = [{c:0 for c in CARS} for _ in graph]
        f_situations = {s:inf for s in self.problem.S.keys()}
        event_queue = PriorityQueue()
        time = 0
        unchecked_vertices = []
        unsolved_situations = set(f_situations.keys())

        # event =  (time_stamp, event_type, path, on_path_id, car)
        # A = (10, false, p_1, 2, 'a') - w momencie 10 przestań być w wierzchołku 2 z trasy p2
        # B = (12, true, p_1, 2, 'f') - w momencie 12 zacznij być w wierzchołku 2 z trasy p2
        for c in CARS:
            for p in self.P[c]:
                event_queue.put((0, True, p, 0, c))

        while not event_queue.empty() and len(unsolved_situations) > 0:
            time_stamp, event_type, path, on_path_id, car = event_queue.get()
            current_v = path[on_path_id][0]
            if verbose: print(f"t[{time_stamp}]: {'przyjezdza' if event_type else 'odjezdza'} w v:{current_v} typu {car}")

            if time != time_stamp:
                for v in unchecked_vertices:
                    if v in unsolved_situations:
                        fulfilled = True
                        for c in self.problem.S[v]:
                            if vertice_inhabitants[v][c] == 0:
                                fulfilled = False
                                break
                        if fulfilled:
                            f_situations[v] = time
                            unsolved_situations.remove(v)
                unchecked_vertices = []
                time = time_stamp


            if event_type: # Przyjeżdża
                if len(path) == on_path_id + 1:
                    vertice_inhabitants[current_v][car] += 1
                    unchecked_vertices.append(current_v)
                    continue
                if path[on_path_id][1] == 0:
                    next_v = path[on_path_id + 1][0]
                    event_queue.put((time + graph[current_v][next_v], True, path, on_path_id + 1, car))
                    continue
                vertice_inhabitants[current_v][car] += 1
                unchecked_vertices.append(current_v)
                event_queue.put((time + path[on_path_id][1], False, path, on_path_id, car))
            else: # Odjeżdża
                next_v = path[on_path_id + 1][0]
                vertice_inhabitants[current_v][car] -= 1
                event_queue.put((time + graph[current_v][next_v], True, path, on_path_id + 1, car))

        for v in unchecked_vertices:
            if v in unsolved_situations:
                fulfilled = True
                for c in self.problem.S[v]:
                    if vertice_inhabitants[v][c] == 0:
                        fulfilled = False
                        break
                if fulfilled:
                    f_situations[v] = time
                    unsolved_situations.remove(v)
        return f_situations
                

def solve_flotilla(problem: Problem):
    Paths = {c: [(v, 1)] for c, v in problem.Vs.items()}

    path, _ = get_closest(problem.G, problem.Vs['a'], [problem.Vs['f']])
    for v in path[1:]:
        Paths['a'].append((v, 1))
    
    path, _ = get_closest(problem.G, problem.Vs['f'], [problem.Vs['p']])
    for v in path[1:]:
        Paths['f'].append((v, 1))
    Paths['a'].extend(Paths['f'][1:])

    to_solve = set(problem.S.keys())
    for _ in range(len(to_solve)):
        current = Paths['p'][-1][0]
        path, _ = get_closest(problem.G, current, to_solve)
        to_solve.remove(path[-1])
        for v in path[1:]:
            Paths['p'].append((v, 1))
    Paths['a'].extend(Paths['p'][1:])
    Paths['f'].extend(Paths['p'][1:])

    return Solution(
        problem,
        {c: [Paths[c] for _ in range(problem.N[c])] for c in CARS}
    )


if __name__ == "__main__":
    n = 5
    E = [(0, 1, 13), (1, 2, 17), (1, 3, 1), (1, 4, 1), (3, 4, 1)]
    G = [dict() for _ in range(n)]
    for u, v, dist in E:
        G[u][v] = dist 
        G[v][u] = dist
    S = {3: {'a', 'f'}, 2: {'a', 'f', 'p'}, 1:{'p'}}
    N = {"a": 1, "f": 1, "p": 1}
    Vs = {"a": 4, "f": 4, "p": 4}

    problem = Problem(G, S, N, Vs)
    solution = solve_flotilla(problem)
    for type, paths in solution.P.items():
        print(type)
        for path in paths:
            print(path)

    print(solution.calculate_cost_function(verbose=True))

    # path, dist = get_closest(G, 0, [2, 3, 4])
    # print(f"{dist}: {path}")
