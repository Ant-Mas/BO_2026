from bee_solver import BeeSolver
from problem_solution import Solution, Problem, CARS
import matplotlib.pyplot as plt
from genetic_new_hope import GeneticSolver
from graph_utils import generate_grid_graph
import itertools
import networkx as nx


def show_costs(history: list[tuple[int, float, Solution]]):
    best_costs = [b for b, _, _ in history]
    avg_costs = [a for _, a, _ in history]

    plt.plot(best_costs, label='Best')
    plt.plot(avg_costs, label='Average')

    plt.xlabel("Generation")
    plt.ylabel("Cost")
    plt.legend()

    plt.show()


Graph = list[dict[int, int]]

def show_graph(graph: Graph, paths: list[list[int]] | None = None, grid:bool = False) -> None:
    G = nx.Graph()

    def _grid_layout(side: int):
        return { r * side + c: (c, -r) for r in range(side) for c in range(side) }
    
    for u, neighbors in enumerate(graph):
        for v, weight in neighbors.items():
            if u < v:
                G.add_edge(u, v, weight=weight, inv_weight=1 / weight)
    
    if grid:
        pos = _grid_layout(int(len(graph) ** 0.5))
    else:
        pos = nx.spring_layout(G, weight="inv_weight", seed=42)
    
    nx.draw(G, pos, with_labels=True, node_size=500, font_size=8)
    
    edge_labels = nx.get_edge_attributes(G, "weight")
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7)

    if paths:
        colors = itertools.cycle(["red", "blue", "green", "orange", "purple", "cyan", "magenta"])
        
        for path, color in zip(paths, colors):
            # Convert node path → edge list
            path_edges = list(zip(path, path[1:]))
            
            nx.draw_networkx_edges(
                G,
                pos,
                edgelist=path_edges,
                edge_color=color,
                width=3
            )
    
    plt.show()


def vis_genetic():
    graph = generate_grid_graph(5, 1, 6)

    problem = Problem.random_given_graph(graph, 10, 1, 1, seed=213)
    print(f"{problem.check_validity(True) = }")

    solver = GeneticSolver(problem, population_size=10, mutation_rate=0.5)
    solution = solver.evolve(generations=20, verbose=True, save_history=True)

    history = solver.history
    show_costs(history)

    paths = []
    for car in CARS:
        for p in history[-1][2].paths[car]:
            paths.append([v for v, w in p])

    print(history[-1][2])
    show_graph(graph, paths, grid=True)


def vis_bee():
    graph = generate_grid_graph(5, 1, 6)

    problem = Problem.random_given_graph(graph, 10, 1, 1, seed=213)
    print(f"{problem.check_validity(True) = }")

    solver = BeeSolver(problem, bees_cnt=20, good_elite_cnt=8, elite_cnt=3, local_elite_cnt=10, local_good_cnt=4)
    solution = solver.evolve(iterations=20, verbose=True)

    history = solver.history
    show_costs(history)

    paths = []
    for car in CARS:
        for p in history[-1][2].paths[car]:
            paths.append([v for v, w in p])

    print(history[-1][2])
    show_graph(graph, paths, grid=True)


if __name__ == "__main__":
    vis_genetic()
    vis_bee()
