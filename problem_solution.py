from dataclasses import dataclass
from queue import PriorityQueue
from math import inf
from collections.abc import Iterable

Graph = list[list[tuple[int, int]]]

@dataclass
class Problem:
    G: Graph
    S: dict[int, tuple[bool, bool, bool]]
    N: dict[str, int]
    Vs: dict[str, int]

    def get_basic_solution(self):
        Paths = {c: [(v, 1)] for c, v in self.Vs.items()}

        path, _ = get_closest(G, self.Vs['a'], [self.Vs['f']])
        for v in path[1:]:
            Paths['a'].append((v, 1))
        
        path, _ = get_closest(G, self.Vs['f'], [self.Vs['p']])
        for v in path[1:]:
            Paths['f'].append((v, 1))
        Paths['a'].extend(Paths['f'][1:])

        to_solve = set(self.S.keys())
        for _ in range(len(to_solve)):
            current = Paths['p'][-1][0]
            path, _ = get_closest(G, current, to_solve)
            to_solve.remove(path[-1])
            for v in path[1:]:
                Paths['p'].append((v, 1))
        Paths['a'].extend(Paths['p'][1:])
        Paths['f'].extend(Paths['p'][1:])

        return Solution(
            self,
            {c: [Paths[c] for _ in range(self.N[c])] for c in ['a', 'f', 'p']}
        )
               

@dataclass
class Solution:
    problem: Problem
    P: dict[str, list[list[tuple[int, int]]]]


def dijkstra(G: Graph, start: int):
    n = len(G)
    
    dist = [inf] * n
    prev = [None] * n
    
    dist[start] = 0
    
    pq = PriorityQueue()
    pq.put((0, start))

    while not pq.empty():
        current_dist, current = pq.get()

        if current_dist > dist[current]:
            continue

        for next, weight in G[current]:
            new_dist = dist[current] + weight
            if new_dist >= dist[next]:
                continue
            
            dist[next] = new_dist
            prev[next] = current
            pq.put((new_dist, next))
    return dist, prev


def get_closest(G: Graph, start: int, ends: Iterable[int]):
    dist, prev = dijkstra(G, start)

    closest = min(ends, key=lambda e: dist[e])
    closest_dist = dist[closest]
    if closest_dist == inf:
        return None, inf

    path = []
    node = closest
    while node is not None:
        path.append(node)
        node = prev[node]
    path.reverse()

    return path, dist[closest]


if __name__ == "__main__":
    n = 5
    E = [(0, 1, 13), (1, 2, 17), (1, 3, 1), (1, 4, 1), (3, 4, 1)]
    G = [[] for _ in range(n)]
    for u, v, dist in E:
        G[u].append((v, dist))
        G[v].append((u, dist))
    S = {3: (True, True, False), 2: (True, True, True)}
    N = {'a': 3, 'f': 2, 'p': 1}
    Vs = {'a': 0, 'f': 4, 'p': 4}

    problem = Problem(G, S, N, Vs)
    solution = problem.get_basic_solution()
    for type, paths in solution.P.items():
        print(type)
        for path in paths:
            print(path)
    
    # path, dist = get_closest(G, 0, [2, 3, 4])
    # print(f"{dist}: {path}")