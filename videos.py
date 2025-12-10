import sys
import os
import gurobipy as gp
from gurobipy import GRB

def parse_input(filename):
    """
    Parses the input file for Hashcode 2017.
    """
    print(f"Reading data from {filename}...")
    with open(filename, 'r') as f:
        # Header: Videos, Endpoints, Request descriptions, Caches, Cache capacity
        V, E, R, C, X = map(int, f.readline().split())
        
        # Video sizes
        video_sizes = list(map(int, f.readline().split()))
        
        # Endpoints
        endpoints = []
        for i in range(E):
            L_D, K = map(int, f.readline().split())
            cache_latencies = {}
            for _ in range(K):
                c, L_c = map(int, f.readline().split())
                cache_latencies[c] = L_c
            endpoints.append({'L_D': L_D, 'caches': cache_latencies})
            
        # Requests
        requests = []
        for _ in range(R):
            v, e, n = map(int, f.readline().split())
            requests.append({'video': v, 'endpoint': e, 'count': n})
            
    return {
        'V': V, 'E': E, 'R': R, 'C': C, 'X': X,
        'video_sizes': video_sizes,
        'endpoints': endpoints,
        'requests': requests
    }

def solve_check_and_save(data):
    """
    Builds the model, writes MPS, solves it, and saves output.
    """
    V = data['V']
    E = data['E']
    C = data['C']
    X = data['X']
    video_sizes = data['video_sizes']
    endpoints = data['endpoints']
    requests = data['requests']
    
    # Ensure output directory exists
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Create model
    m = gp.Model("streaming_videos")
    
    # --- Requirements: Set MIP Gap to 0.5% ---
    m.Params.MIPGap = 0.005
    
    # Variables
    print("Creating model variables...")
    # x[c, v] = 1 if video v is in cache c
    x = m.addVars(C, V, vtype=GRB.BINARY, name="x")
    
    # Pre-calculate relevant requests and gains
    # y[r, c] = 1 if request r served by cache c
    y_keys = []
    gains = {}
    
    # Optimization: Only created variables for useful cache-endpoint links
    for r_idx, req in enumerate(requests):
        v = req['video']
        e = req['endpoint']
        n = req['count']
        ep_data = endpoints[e]
        L_D = ep_data['L_D']
        
        for c, L_c in ep_data['caches'].items():
            saving = L_D - L_c
            if saving > 0:
                y_keys.append((r_idx, c))
                gains[(r_idx, c)] = saving * n
    
    y = m.addVars(y_keys, vtype=GRB.BINARY, name="y")

    m.update()
    
    # Objective: Maximize total savings
    print("Building objective function...")
    obj = gp.quicksum(gains[(r_idx, c)] * y[r_idx, c] for r_idx, c in y_keys)
    m.setObjective(obj, GRB.MAXIMIZE)
    
    # Constraints
    print("Adding constraints...")
    
    # 1. Cache capacity
    m.addConstrs(
        (gp.quicksum(video_sizes[v] * x[c, v] for v in range(V)) <= X for c in range(C)),
        name="Capacity"
    )
    
    # 2. Logic: If served by c, video must be in c
    # y[r, c] <= x[c, v]
    for r_idx, c in y_keys:
        v = requests[r_idx]['video']
        m.addConstr(y[r_idx, c] <= x[c, v], name=f"Link_r{r_idx}_c{c}")
        
    # 3. Single source per request
    from collections import defaultdict
    req_to_caches = defaultdict(list)
    for r_idx, c in y_keys:
        req_to_caches[r_idx].append(c)
        
    for r_idx, connected_caches in req_to_caches.items():
        m.addConstr(gp.quicksum(y[r_idx, c] for c in connected_caches) <= 1, name=f"OneSource_r{r_idx}")

    # --- Write MPS file to output folder ---
    mps_path = os.path.join(output_dir, "videos.mps")
    print(f"Writing {mps_path}...")
    m.write(mps_path)
        
    # Solve
    print("Solving model...")
    m.optimize()
    
    # Extract solution
    solution = {} 
    if m.solCount > 0:
        for c in range(C):
            videos_in_c = []
            for v in range(V):
                if x[c, v].X > 0.5:
                    videos_in_c.append(v)
            if videos_in_c:
                solution[c] = videos_in_c
                
    # --- Write videos.out to output folder ---
    output_filename = os.path.join(output_dir, "videos.out")
    print(f"Writing solution to {output_filename}...")
    with open(output_filename, 'w') as f:
        f.write(f"{len(solution)}\n")
        for c, videos in solution.items():
            f.write(f"{c} {' '.join(map(str, videos))}\n")
    

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/videos.py <path_to_dataset>")
        sys.exit(1)
        
    dataset_path = sys.argv[1]
    
    try:
        data = parse_input(dataset_path)
        solve_check_and_save(data)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
