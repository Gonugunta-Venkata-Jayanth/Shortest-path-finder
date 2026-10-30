# Design Document: Concurrent Shortest Path Finder

## Overview
This project is a pure-Python single-source shortest path finder based on Bellman-Ford. It ships
two solvers with identical results, a sequential one and a thread-pool one, supports negative edge
weights, and detects negative-weight cycles. See `performance_report` for measured timings.

## Modules
| File | Responsibility |
|---|---|
| `graph.py` | `Graph` class (CSR-style storage) and `generate_random_graph` |
| `bellman_ford.py` | `bellman_ford_sequential` and `ConcurrentBellmanFord` |
| `utils.py` | `load_graph` (reads the `sample/input.txt` format) and `format_distance` |
| `main.py` | CLI: `--input` file solving, `--test` correctness check, or random-graph benchmark |
| `test_framework.py` | `test_correctness()` and `benchmark()` used by the CLI |
| `benchmark.py` | Reproducible multi-case benchmark that prints a Markdown table |
| `test_unit.py` | `unittest` suite |

## Graph representation
`Graph(num_nodes, edges)` takes a list of `(u, v, w)` tuples and builds a compressed-sparse-row
(CSR) layout:
- Edges are grouped by source node and sorted by destination within each group.
- They are stored in three flat parallel lists: `edges_src`, `edges_dst`, `weights`.
- `node_ptrs` has `num_nodes + 1` entries; the out-edges of node `u` are the index range
  `node_ptrs[u] .. node_ptrs[u + 1] - 1`.
The graph is never modified after construction, so threads can read it without locking.
`neighbors(u)` returns `(dst, weight)` pairs for convenience.

## Sequential solver
`bellman_ford_sequential(graph, source)` initialises `dist` to `inf` (0 at the source) and runs up
to `V - 1` rounds. Each round walks every node with a finite distance and relaxes its out-edges.
If a round makes no update the loop exits early. A final pass over all edges raises
`ValueError("Graph contains a negative weight cycle")` if any edge can still be relaxed.

## Concurrent solver
`ConcurrentBellmanFord(graph, source, num_threads).run()`:
- Creates one `ThreadPoolExecutor(max_workers=num_threads)` for the whole run.
- Each round splits the node list into `num_threads` contiguous partitions of equal size and
  submits one task per partition (`_relax_partition`). Each task relaxes the out-edges of its
  nodes, reading `dist[u]` once per source node.
- **Synchronization:** there is one `threading.Lock` per node. Before comparing and writing
  `dist[v]`, a task takes `locks[v]`, so the check-and-update on a destination is atomic. There
  are no per-thread buffers; updates go straight into the shared `dist` list. Because tasks read
  values other tasks may have just lowered, a round can make more progress than a strict
  round-synchronous Bellman-Ford, which is still correct (distances only ever decrease toward
  the true shortest paths).
- **Convergence:** the main thread waits for all tasks of a round (`as_completed`) and ORs their
  "updated" return values. If none updated, it stops early; otherwise it runs at most `V - 1` rounds.
- **Negative-cycle check** is done sequentially after the rounds, the same way as the sequential
  solver, for a deterministic result.

## Error handling
- Negative-weight cycles reachable from the source raise `ValueError`.
- `load_graph` validates the header, the `u v w` line format, node indices, and the edge count,
  and raises `ValueError` with the line number on bad input. The CLI prints the cycle error and
  exits with status 1.
- Unreachable nodes keep distance `inf` (printed as `INF` by the CLI).

## Design decisions and trade-offs
- **Bellman-Ford** was chosen over Dijkstra because it handles negative weights.
- **Threads, not processes,** keep the shared distance array simple, but under CPython's GIL the
  CPU-bound relaxation does not run in parallel, and the per-edge lock adds overhead. The
  measured result is that the concurrent solver is slower than the sequential one (see
  `performance_report`). The design is kept as a correct, thread-safe reference.
- **CSR storage** keeps each node's out-edges contiguous, which makes partitioning by node simple.

## Possible improvements
- `multiprocessing` with shared memory, a free-threaded Python build, or a NumPy/C/Rust kernel
  for real parallel speedup.
- Per-thread update buffers merged once per round instead of one lock per relaxation.
- Partitioning by edge count rather than node count to balance skewed degree distributions.
