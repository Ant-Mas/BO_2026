import time
import random
from compare_shared_population import generate_initial_population
from flask import Flask, request, jsonify, send_from_directory
from problem_solution import Problem, CARS
from genetic_new_hope import GeneticSolver
from bee_solver import BeeSolver
from graph_utils import generate_city_graph

app = Flask(__name__, static_folder='static')


@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


@app.route('/api/solve', methods=['POST'])
def solve():
    """
    Single endpoint: generate a random city-like problem and solve it
    with both algorithms.  Returns a DTO designed for easy graph + path
    visualisation on the frontend.
    """
    data = request.get_json()

    # --- City grid parameters ---
    grid_rows = int(data.get('grid_rows', 6))
    grid_cols = int(data.get('grid_cols', 8))
    min_weight = int(data.get('min_weight', 1))
    max_weight = int(data.get('max_weight', 10))
    num_situations = int(data.get('num_situations', 10))
    min_car_amount = int(data.get('min_car_amount', 2))
    max_car_amount = int(data.get('max_car_amount', 4))
    seed = int(data.get('seed', 42))

    # --- Genetic parameters ---
    generations = int(data.get('generations', 40))
    population_size = int(data.get('population_size', 50))
    mutation_rate = float(data.get('mutation_rate', 0.25))

    # --- Bee parameters ---
    bees_cnt = int(data.get('bees_cnt', 30))
    good_elite_cnt = int(data.get('good_elite_cnt', 10))
    elite_cnt = int(data.get('elite_cnt', 3))
    local_elite_cnt = int(data.get('local_elite_cnt', 10))
    local_good_cnt = int(data.get('local_good_cnt', 4))

    # --- Generate city graph ---
    random.seed(seed)
    try:
        graph, positions = generate_city_graph(
            rows=grid_rows,
            cols=grid_cols,
            min_weight=min_weight,
            max_weight=max_weight,
        )
    except Exception as e:
        return jsonify({'error': f'Graph generation failed: {str(e)}'}), 400

    num_vertices = grid_rows * grid_cols
    if num_situations > num_vertices:
        return jsonify({'error': f'Too many situations ({num_situations}) for {num_vertices} vertices'}), 400

    # --- Build problem on the city graph ---
    try:
        problem = Problem.random_given_graph(
            graph,
            num_situations=num_situations,
            min_car_amount=min_car_amount,
            max_car_amount=max_car_amount,
            seed=seed,
        )
    except Exception as e:
        return jsonify({'error': f'Problem generation failed: {str(e)}'}), 400

    if not problem.check_validity():
        return jsonify({'error': 'Generated problem is not valid. Try different parameters.'}), 400
    
    initial_population = generate_initial_population(problem, population_size)

    # ---------- Run Genetic Algorithm ----------
    ga_solver = GeneticSolver(problem, population_size=population_size, mutation_rate=mutation_rate)

    t0 = time.perf_counter()
    ga_solution = ga_solver.evolve(
        generations=generations,
        initial_population=initial_population,
        save_history=True,
        verbose=False
    )
    ga_solution.calculate_cost_function()
    ga_time = time.perf_counter() - t0

    ga_cost = ga_solution.get_cost()
    ga_history = [h[0] for h in ga_solver.history]

    # ---------- Run Bee Algorithm ----------
    bee_solver = BeeSolver(
        problem,
        bees_cnt=population_size,
        good_elite_cnt=good_elite_cnt,
        elite_cnt=elite_cnt,
        local_elite_cnt=local_elite_cnt,
        local_good_cnt=local_good_cnt
    )

    t0 = time.perf_counter()
    ba_solution = bee_solver.evolve(
        iterations=generations,
        initial_population=initial_population,
        verbose=False
    )
    ba_time = time.perf_counter() - t0

    ba_cost = ba_solution.get_cost()
    ba_history = [h[0] for h in bee_solver.history]

    # ---------- Build DTO ----------

    # Graph DTO: nodes with fixed positions & edges
    # Scale positions so graph fills the full-width 600px-tall container
    nodes = []
    situation_set = set(problem.situations.keys())
    starting_set = set(problem.starting_positions.values())

    # Normalize positions to [0,1] then scale to container-like coords
    all_x = [positions[i][0] for i in range(len(graph))]
    all_y = [positions[i][1] for i in range(len(graph))]
    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = min(all_y), max(all_y)
    range_x = max_x - min_x if max_x != min_x else 1
    range_y = max_y - min_y if max_y != min_y else 1

    # Target canvas: make both axes use similar pixel range
    target_w = 1000
    target_h = 500

    for i in range(len(graph)):
        label = str(i)
        group = 'normal'
        if i in situation_set:
            group = 'situation'
            cars_needed = list(problem.situations[i])
            label = f"{i} ({','.join(cars_needed)})"
        if i in starting_set:
            group = 'start'
        nx = (positions[i][0] - min_x) / range_x * target_w
        ny = (positions[i][1] - min_y) / range_y * target_h
        nodes.append({'id': i, 'label': label, 'group': group, 'x': nx, 'y': ny})

    edges = []
    seen = set()
    for u, neighbors in enumerate(graph):
        for v, w in neighbors.items():
            edge_key = (min(u, v), max(u, v))
            if edge_key not in seen:
                seen.add(edge_key)
                edges.append({'from': u, 'to': v, 'label': str(w), 'weight': w})

    # Paths DTO helper
    def extract_paths(solution):
        result = {}
        for car in CARS:
            result[car] = []
            for path in solution.paths[car]:
                result[car].append([v for v, _wait in path])
        return result

    ga_paths = extract_paths(ga_solution)
    ba_paths = extract_paths(ba_solution)

    dto = {
        'graph': {'nodes': nodes, 'edges': edges},
        'situations': {str(k): list(v) for k, v in problem.situations.items()},
        'starting_positions': problem.starting_positions,
        'car_amounts': problem.car_amounts,
        'genetic': {
            'cost': ga_cost,
            'time': round(ga_time, 4),
            'is_correct': ga_solution.is_correct(),
            'history': ga_history,
            'paths': ga_paths,
        },
        'bee': {
            'cost': ba_cost,
            'time': round(ba_time, 4),
            'is_correct': ba_solution.is_correct(),
            'history': ba_history,
            'paths': ba_paths,
        },
    }

    return jsonify(dto)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
