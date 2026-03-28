from queue import PriorityQueue
from math import inf
from collections.abc import Iterable

Graph = list[dict[int, int]]

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
        return None, inf

    path = []
    node = closest
    while node is not None:
        path.append(node)
        node = prev[node]
    path.reverse()

    return path, dist[closest]