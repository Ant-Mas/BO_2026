from queue import PriorityQueue
from math import inf
from collections.abc import Iterable
import random
from itertools import combinations
import networkx as nx

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

    all_edges = list(combinations(range(num_vertices), 2))
    remaining_edges = [e for e in all_edges if e not in used_edges]

    random.shuffle(remaining_edges)
    needed = num_edges - len(used_edges)

    for u, v in remaining_edges[:needed]:
        weight = random.randint(min_weight, max_weight)
        graph[u][v] = weight
        graph[v][u] = weight

    return graph


def _is_connected(graph: Graph, n: int) -> bool:
    if n == 0:
        return True
    visited = set()
    queue = [0]
    visited.add(0)
    while queue:
        node = queue.pop()
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return len(visited) == n


def generate_city_graph(
        rows: int,
        cols: int,
        min_weight: int,
        max_weight: int,
        remove_pct: float = 0.15,
        diagonal_pct: float = 0.12,
) -> tuple[Graph, dict[int, tuple[float, float]]]:
    n = rows * cols
    graph: Graph = [{} for _ in range(n)]

    def nid(r: int, c: int) -> int:
        return r * cols + c

    h_weights: dict[tuple[int, int], int] = {}  
    v_weights: dict[tuple[int, int], int] = {}  

    for r in range(rows):
        for c in range(cols - 1):
            w = random.randint(min_weight, max_weight)
            u, v = nid(r, c), nid(r, c + 1)
            graph[u][v] = w
            graph[v][u] = w
            h_weights[(r, c)] = w

    for r in range(rows - 1):
        for c in range(cols):
            w = random.randint(min_weight, max_weight)
            u, v = nid(r, c), nid(r + 1, c)
            graph[u][v] = w
            graph[v][u] = w
            v_weights[(r, c)] = w

    removable = []
    for r in range(rows):
        for c in range(cols - 1):
            removable.append(('h', r, c))
    for r in range(rows - 1):
        for c in range(cols):
            removable.append(('v', r, c))

    random.shuffle(removable)
    num_remove = int(remove_pct * len(removable))
    removed = 0

    for edge_type, r, c in removable:
        if removed >= num_remove:
            break
        if edge_type == 'h':
            u, v = nid(r, c), nid(r, c + 1)
        else:
            u, v = nid(r, c), nid(r + 1, c)

        w = graph[u][v]
        del graph[u][v]
        del graph[v][u]

        if _is_connected(graph, n):
            removed += 1
            if edge_type == 'h':
                del h_weights[(r, c)]
            else:
                del v_weights[(r, c)]
        else:
            graph[u][v] = w
            graph[v][u] = w

    diagonals = []
    for r in range(rows - 1):
        for c in range(cols):
            if c + 1 < cols:
                diagonals.append((nid(r, c), nid(r + 1, c + 1)))
            if c - 1 >= 0:
                diagonals.append((nid(r, c), nid(r + 1, c - 1)))
    random.shuffle(diagonals)
    num_diag = max(1, int(diagonal_pct * len(diagonals)))
    for u, v in diagonals[:num_diag]:
        if v not in graph[u]:
            w = random.randint(min_weight, max_weight)
            graph[u][v] = w
            graph[v][u] = w

    positions: dict[int, tuple[float, float]] = {}

    h_vals = list(h_weights.values())
    avg_h = sum(h_vals) / len(h_vals) if h_vals else (min_weight + max_weight) / 2
    v_vals = list(v_weights.values())
    avg_v = sum(v_vals) / len(v_vals) if v_vals else (min_weight + max_weight) / 2

    row_xs = []
    for r in range(rows):
        xs = [0.0] * cols
        for c in range(1, cols):
            w = h_weights.get((r, c - 1), avg_h)
            xs[c] = xs[c - 1] + w
        row_xs.append(xs)

    col_ys = []
    for c in range(cols):
        ys = [0.0] * rows
        for r in range(1, rows):
            w = v_weights.get((r - 1, c), avg_v)
            ys[r] = ys[r - 1] + w
        col_ys.append(ys)

    for r in range(rows):
        for c in range(cols):
            positions[nid(r, c)] = (row_xs[r][c], col_ys[c][r])

    return graph, positions


def generate_grid_graph(side: int, min_weight: int, max_weight: int) -> Graph:
    n = side * side
    graph: Graph = [{} for _ in range(n)]

    def node_id(r: int, c: int) -> int:
        return r * side + c

    for r in range(side):
        for c in range(side):
            u = node_id(r, c)

            if c + 1 < side:
                v = node_id(r, c + 1)
                w = random.randint(min_weight, max_weight)
                graph[u][v] = w
                graph[v][u] = w
                
            if r + 1 < side:
                v = node_id(r + 1, c)
                w = random.randint(min_weight, max_weight)
                graph[u][v] = w
                graph[v][u] = w

    return graph

