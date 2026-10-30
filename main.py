import argparse
import random
from test_framework import test_correctness, benchmark

def main():
    parser = argparse.ArgumentParser(description="Concurrent Shortest Path Finder - Bellman-Ford")
    parser.add_argument('--test', action='store_true', help="Run correctness tests")
    parser.add_argument('--nodes', type=int, default=1000, help="Number of nodes")
    parser.add_argument('--edge_prob', type=float, default=0.01, help="Edge probability")
    parser.add_argument('--threads', type=int, default=8, help="Number of threads")
    parser.add_argument('--allow_negative', action='store_true', help="Allow negative edges")
    parser.add_argument('--input', help="Solve a graph file (format of sample/input.txt) and print distances")
    parser.add_argument('--source', type=int, default=0, help="Source node for --input (default 0)")
    parser.add_argument('--seed', type=int, default=None, help="Random seed for a reproducible benchmark graph")

    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    if args.input:
        from utils import load_graph, format_distance
        from bellman_ford import ConcurrentBellmanFord
        graph = load_graph(args.input)
        try:
            dist = ConcurrentBellmanFord(graph, args.source, num_threads=args.threads).run()
        except ValueError as e:
            print(f"Error: {e}")
            raise SystemExit(1)
        for d in dist:
            print(format_distance(d))
    elif args.test:
        test_correctness()
    else:
        benchmark(
            num_nodes=args.nodes,
            edge_prob=args.edge_prob,
            num_threads=args.threads,
            allow_negative=args.allow_negative
        )

if __name__ == "__main__":
    main()
