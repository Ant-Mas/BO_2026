from queue import PriorityQueue
from math import inf
from collections.abc import Iterable
import random
from itertools import combinations

Graph = list[dict[int, int]]

def dijkstra(G: Graph, start: int) -> tuple[list[int], list[int | None]]:
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

        for next, weight in G[current].items():
            new_dist = dist[current] + weight
            if new_dist >= dist[next]:
                continue

            dist[next] = new_dist
            prev[next] = current
            pq.put((new_dist, next))
    return dist, prev


def get_closest(G: Graph, start: int, ends: Iterable[int]) -> tuple[list[int], int]:
    dist, prev = dijkstra(G, start)

    closest = min(ends, key=lambda e: dist[e])
    closest_dist = dist[closest]
    if closest_dist == inf:
        raise RuntimeError("No path from start to any of the ends")

    path: list[int] = []
    node = closest
    while node is not None:
        path.append(node)
        node = prev[node]
    path.reverse()

    return path, dist[closest]


def generate_random_graph(num_vertices: int, num_edges: int, min_weight: int, max_weight: int) -> Graph:
    if num_vertices < 1:
        raise ValueError("Number of vertices must be at least 1")

    max_possible_edges = num_vertices * (num_vertices - 1) // 2
    if num_edges < num_vertices - 1:
        raise ValueError("Need at least (vertices - 1) edges for connectivity")
    if num_edges > max_possible_edges:
        raise ValueError("Too many edges")

    graph = [{} for _ in range(num_vertices)]

    # Step 1: Create a random spanning tree (guarantees connectivity)
    vertices = list(range(num_vertices))
    random.shuffle(vertices)

    used_edges = set()

    for i in range(1, num_vertices):
        u = vertices[i]
        v = vertices[random.randint(0, i - 1)]
        edge = (min(u, v), max(u, v))

        weight = random.randint(min_weight, max_weight)
        graph[u][v] = weight
        graph[v][u] = weight
        used_edges.add(edge)

    # Step 2: Generate all remaining possible edges
    all_edges = list(combinations(range(num_vertices), 2))
    remaining_edges = [e for e in all_edges if e not in used_edges]

    # Shuffle once and pick needed edges
    random.shuffle(remaining_edges)
    needed = num_edges - len(used_edges)

    for u, v in remaining_edges[:needed]:
        weight = random.randint(min_weight, max_weight)
        graph[u][v] = weight
        graph[v][u] = weight

    return graph


def generate_grid_graph(side: int, min_weight: int, max_weight: int) -> Graph:
    n = side * side
    graph: Graph = [{} for _ in range(n)]
    
    def node_id(r: int, c: int) -> int:
        return r * side + c
    
    for r in range(side):
        for c in range(side):
            u = node_id(r, c)
            
            # Connect to the right neighbor
            if c + 1 < side:
                v = node_id(r, c + 1)
                w = random.randint(min_weight, max_weight)
                graph[u][v] = w
                graph[v][u] = w  
            
            # Connect to the bottom neighbor
            if r + 1 < side:
                v = node_id(r + 1, c)
                w = random.randint(min_weight, max_weight)
                graph[u][v] = w
                graph[v][u] = w 
    
    return graph

