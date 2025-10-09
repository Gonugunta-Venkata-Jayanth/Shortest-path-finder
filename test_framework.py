import time
from graph import generate_random_graph
from bellman_ford import bellman_ford_sequential, ConcurrentBellmanFord

def test_correctness():
    print("[*] Running correctness tests...")

    # Known graph example
    edges = [
        (0, 1, 5),
        (0, 2, 3),
        (1, 2, 2),
        (1, 3, 6),
        (2, 3, 7),
        (2, 4, 4),
        (3, 4, -1)
    ]
    from graph import Graph
    g = Graph(5, edges)

    dist_seq = bellman_ford_sequential(g, 0)
    print("Sequential distances:", dist_seq)

    c_bf = ConcurrentBellmanFord(g, 0, num_threads=4)
    dist_conc = c_bf.run()
    print("Concurrent distances:", dist_conc)

    assert all(abs(a - b) < 1e-6 for a, b in zip(dist_seq, dist_conc)), "Mismatch between sequential and concurrent!"

    # Test negative cycle detection
    try:
        edges_neg_cycle = [
            (0, 1, 1),
            (1, 2, -1),
            (2, 0, -1)
        ]
        g_neg = Graph(3, edges_neg_cycle)
        bellman_ford_sequential(g_neg, 0)
    except ValueError as e:
        print("Correctly detected negative cycle in sequential:", e)

    try:
        c_bf_neg = ConcurrentBellmanFord(g_neg, 0, num_threads=2)
        c_bf_neg.run()
    except ValueError as e:
        print("Correctly detected negative cycle in concurrent:", e)

def benchmark(num_nodes=1000, edge_prob=0.01, weight_range=(1, 10), num_threads=8, allow_negative=False):
    print(f"[*] Benchmarking: nodes={num_nodes}, edge_prob={edge_prob}, threads={num_threads}, allow_negative={allow_negative}")
    g = generate_random_graph(num_nodes, edge_prob, weight_range, allow_negative=allow_negative)

    # Sequential run
    start = time.time()
    try:
        dist_seq = bellman_ford_sequential(g, 0)
    except ValueError as e:
        print("Sequential detected error:", e)
        dist_seq = None
    end = time.time()
    print(f"Sequential time: {end - start:.3f}s")

    # Concurrent run
    start = time.time()
    try:
        c_bf = ConcurrentBellmanFord(g, 0, num_threads=num_threads)
        dist_conc = c_bf.run()
    except ValueError as e:
        print("Concurrent detected error:", e)
        dist_conc = None
    end = time.time()
    print(f"Concurrent time: {end - start:.3f}s")

    if dist_seq is not None and dist_conc is not None:
        mismatches = sum(1 for a, b in zip(dist_seq, dist_conc) if abs(a - b) > 1e-6)
        print(f"Distance mismatches: {mismatches}")

if __name__ == "__main__":
    test_correctness()
    print("\n[*] Running benchmark on large graph...")
    benchmark(num_nodes=2000, edge_prob=0.005, weight_range=(1, 20), num_threads=8, allow_negative=True)
