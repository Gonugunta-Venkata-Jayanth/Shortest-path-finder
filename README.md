# Concurrent Shortest Path Finder - Bellman-Ford (Industry Level)

## Overview

This project implements a high-performance, concurrent shortest path finder using the Bellman-Ford algorithm in Python. It is designed to:

- Handle large, sparse graphs with millions of edges
- Support negative edge weights and detect negative cycles
- Use fine-grained locking with ThreadPoolExecutor for concurrency
- Optimize graph storage with CSR-like adjacency lists for cache locality
- Provide comprehensive correctness tests and benchmarks

## Requirements

- Python 3.7 or higher
- No external dependencies (uses built-in modules)

## How to Use

### Run correctness tests:

```bash
python main.py --test
