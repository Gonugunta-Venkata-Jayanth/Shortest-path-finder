"""Reproducible benchmark: sequential vs concurrent Bellman-Ford.

Prints a Markdown table. Usage: python benchmark.py [--repeats N]
"""
import argparse
import platform
import random
import statistics
import time

from graph import generate_random_graph
from bellman_ford import bellman_ford_sequential, ConcurrentBellmanFord

CASES = [
    # (label, nodes, edge_prob, threads, allow_negative)
    ("Small", 100, 0.05, 1, False),
    ("Small", 100, 0.05, 8, False),
    ("Medium", 1000, 0.01, 1, False),
    ("Medium", 1000, 0.01, 8, False),
    ("Large sparse", 5000, 0.001, 8, False),
    ("Medium, ~10% negative edges", 1000, 0.01, 8, True),
]


def timed(fn):
    start = time.perf_counter()
    try:
        result = fn()
    except ValueError:
        result = "negative cycle"
    return time.perf_counter() - start, result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repeats", type=int, default=3)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    print(f"Python {platform.python_version()} on {platform.system()} {platform.machine()}, "
          f"seed={args.seed}, best of {args.repeats}\n")
    print("| Graph | Nodes | Edges | Threads | Negative edges | Sequential (s) | Concurrent (s) | Speedup | Result |")
    print("|---|---|---|---|---|---|---|---|---|")
    for label, n, p, threads, neg in CASES:
        random.seed(args.seed)
        g = generate_random_graph(n, p, (1, 10), allow_negative=neg)
        seq_times, conc_times = [], []
        for _ in range(args.repeats):
            t, seq = timed(lambda: bellman_ford_sequential(g, 0))
            seq_times.append(t)
            t, conc = timed(lambda: ConcurrentBellmanFord(g, 0, num_threads=threads).run())
            conc_times.append(t)
        if isinstance(seq, str) or isinstance(conc, str):
            outcome = f"seq: {seq if isinstance(seq, str) else 'ok'}, conc: {conc if isinstance(conc, str) else 'ok'}"
        else:
            mism = sum(1 for a, b in zip(seq, conc) if abs(a - b) > 1e-6)
            outcome = f"{mism} mismatches"
        s, c = min(seq_times), min(conc_times)
        print(f"| {label} | {n} | {len(g.weights)} | {threads} | {'yes' if neg else 'no'} | "
              f"{s:.4f} | {c:.4f} | {s / c:.2f}x | {outcome} |")


if __name__ == "__main__":
    main()
