# ⚡ Concurrent Shortest Path Finder (Bellman-Ford)

> A pure-Python single-source shortest path engine that runs Bellman-Ford sequentially and in parallel with a thread pool, handles negative edge weights, and detects negative-weight cycles.

![Python](https://img.shields.io/badge/Python-3.7%2B-3776AB?logo=python&logoColor=white)
![Algorithm](https://img.shields.io/badge/Algorithm-Bellman--Ford-6A5ACD)
![Concurrency](https://img.shields.io/badge/Concurrency-ThreadPoolExecutor-2E8B57)
![Tests](https://img.shields.io/badge/Tests-unittest-informational)
![Dependencies](https://img.shields.io/badge/Runtime%20deps-none-brightgreen)

---

## ✨ Features

- **Two solvers with the same output**
  - `bellman_ford_sequential(graph, source)`: classic Bellman-Ford with early exit once an iteration makes no update.
  - `ConcurrentBellmanFord(graph, source, num_threads).run()`: splits nodes into equal partitions and relaxes their outgoing edges in parallel with `concurrent.futures.ThreadPoolExecutor`.
- **Fine-grained locking**: one `threading.Lock` per node, so a thread only locks the destination distance it is updating.
- **Negative weights supported**, with **negative-cycle detection** through an extra relaxation pass that raises `ValueError("Graph contains a negative weight cycle")`.
- **CSR-style graph storage**: edges are kept in flat `edges_dst` / `weights` arrays, sorted per source node and indexed by `node_ptrs`, for cache-friendly traversal.
- **Random graph generator** (`generate_random_graph`) with configurable size, edge probability, weight range, and an optional ~10% share of negative edges.
- **Built-in benchmark CLI** that times the sequential and concurrent solvers on the same graph and counts distance mismatches.
- **Unit tests** for a standard mixed-weight graph, negative-cycle detection (both solvers), disconnected graphs (unreachable nodes stay `inf`), and the single-node case.

## 🛠 Tech Stack

| Area | Tools |
|---|---|
| Language | Python 3 (standard library only at runtime) |
| Concurrency | `concurrent.futures.ThreadPoolExecutor`, `threading.Lock` |
| CLI | `argparse` |
| Testing | `unittest` |
| Scripting | PowerShell (`run_all.ps1`) |

## 🏗 How it works

```mermaid
flowchart TD
    A["main.py (argparse)"] -->|--test| B["test_framework.test_correctness"]
    A -->|default| C["test_framework.benchmark"]
    C --> D["graph.generate_random_graph"]
    D --> E["Graph: CSR arrays<br/>node_ptrs · edges_dst · weights"]
    B --> E
    E --> F["bellman_ford_sequential"]
    E --> G["ConcurrentBellmanFord"]
    G --> H["Split nodes into num_threads partitions"]
    H --> I["Threads relax edges<br/>per-node lock on dist[v]"]
    I --> J{"Any distance updated?"}
    J -->|yes, up to V-1 rounds| H
    J -->|no| K["Negative-cycle check"]
    F --> K
    K -->|cycle found| L["raise ValueError"]
    K -->|ok| M["Distance list"]
```

## 📂 Project Structure

```
Shortest-path-finder/
├── graph.py                  # Graph class (CSR-like storage) + random graph generator
├── bellman_ford.py           # Sequential and concurrent Bellman-Ford
├── main.py                   # CLI: correctness check or benchmark
├── test_framework.py         # test_correctness() and benchmark()
├── test_unit.py              # unittest suite
├── utils.py                  # Placeholder for future helpers
├── run_all.ps1               # Runs unit tests, a 2,000-node benchmark, and the correctness check
├── sample/
│   ├── input.txt             # Example graph: "<nodes> <edges>" then "u v w" per line
│   └── output.txt            # Expected distances from node 0 for that graph
├── Design_document.md        # Design notes
├── performance_report        # Performance write-up
├── reflection_future _works  # Reflection and future-work notes
├── output_utf8.md            # Captured console output of run_all.ps1
└── requirements.txt
```

## 🚀 Getting Started

```bash
git clone https://github.com/Gonugunta-Venkata-Jayanth/Shortest-path-finder.git
cd Shortest-path-finder
```

No third-party packages are needed to run the solver or the tests (`requirements.txt` lists `numpy` and `pytest`, but the code does not import them).

### Correctness check

```bash
python main.py --test
```

### Benchmark sequential vs concurrent

```bash
python main.py --nodes 2000 --edge_prob 0.01 --threads 8 --allow_negative
```

| Flag | Default | Meaning |
|---|---|---|
| `--nodes` | `1000` | Number of nodes in the random graph |
| `--edge_prob` | `0.01` | Probability of an edge between any ordered pair of nodes |
| `--threads` | `8` | Worker threads for the concurrent solver |
| `--allow_negative` | off | Makes ~10% of edges negative |
| `--test` | off | Runs the correctness check instead of the benchmark |

### Unit tests

```bash
python -m unittest test_unit.py -v
```

### Everything at once (Windows PowerShell)

```powershell
./run_all.ps1
```

### Use it as a library

```python
from graph import Graph
from bellman_ford import bellman_ford_sequential, ConcurrentBellmanFord

edges = [(0, 1, 5), (0, 2, 3), (1, 2, 2), (1, 3, 6), (2, 3, 7), (2, 4, 4), (3, 4, -1)]
g = Graph(5, edges)

print(bellman_ford_sequential(g, 0))                 # [0.0, 5.0, 3.0, 10.0, 7.0]
print(ConcurrentBellmanFord(g, 0, num_threads=4).run())
```

## 📊 Results (from the captured run in `output_utf8.md`)

- All 5 unit tests pass.
- Both solvers return `[0.0, 5.0, 3.0, 10.0, 7.0]` on the reference graph, and both detect the negative cycle.
- Benchmark with `nodes=2000, edge_prob=0.01, threads=8, allow_negative=True`: both solvers correctly reported a negative-weight cycle; sequential took **5.177 s** and concurrent **16.488 s** on that machine.

Because of CPython's Global Interpreter Lock (GIL), CPU-bound relaxation in threads plus per-edge locking can be slower than the sequential loop. The future-work items below target this.

## 🔮 Future Work

- Use `multiprocessing` / shared memory, or a C/C++/Rust extension, to get around the GIL.
- Replace per-edge locking with lock-free per-thread buffers that are merged once per round.
- Read graphs from files in the `sample/input.txt` format through the CLI.
- Add work-stealing for uneven degree distributions, plus other algorithms (e.g. parallel Dijkstra / Δ-stepping for non-negative weights).
- Add CI (GitHub Actions) to run the test suite on every push.

## 👤 Author

**Jayanth Gonugunta Venkata**: [github.com/Gonugunta-Venkata-Jayanth](https://github.com/Gonugunta-Venkata-Jayanth)
