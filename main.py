import argparse
from test_framework import test_correctness, benchmark

def main():
    parser = argparse.ArgumentParser(description="Concurrent Shortest Path Finder - Bellman-Ford")
    parser.add_argument('--test', action='store_true', help="Run correctness tests")
    parser.add_argument('--nodes', type=int, default=1000, help="Number of nodes")
    parser.add_argument('--edge_prob', type=float, default=0.01, help="Edge probability")
    parser.add_argument('--threads', type=int, default=8, help="Number of threads")
    parser.add_argument('--allow_negative', action='store_true', help="Allow negative edges")

    args = parser.parse_args()

    if args.test:
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
