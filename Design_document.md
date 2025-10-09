# Design Document: Concurrent Shortest Path Finder

## Overview
This project implements a high-performance concurrent shortest path finder using the Bellman-Ford algorithm, optimized for multi-threading on large, sparse graphs with support for negative weights.

## Architecture
- Graph Representation: Immutable adjacency list storing edges as (destination, weight) tuples.
- Algorithms Implemented: Sequential Bellman-Ford and Concurrent Bellman-Ford.
- Concurrency Model: Thread-based parallelism using Python's `concurrent.futures.ThreadPoolExecutor`.
- Synchronization: Atomic updates avoided by per-thread relaxation; convergence coordinated using a shared flag with thread-safe access.

## Data Structures
- Graph stored as a list of adjacency lists.
- Distance array shared but updated with thread-safe checks to minimize contention.
- Worklist implemented with per-thread local buffers to reduce synchronization overhead.

## Concurrency and Synchronization
- Each thread relaxes a subset of edges concurrently.
- Synchronization uses threading primitives to coordinate iterations and detect convergence.
- Race conditions minimized by atomic compare-and-set updates and local buffers.

## Design Decisions
- Chose Bellman-Ford to support negative weights.
- Immutable graph simplifies thread safety.
- Avoided locks during relaxation by careful data partitioning.
- Used Python's standard threading libraries for portability.

## Error Handling
- Negative weight cycles detected via an extra iteration check.
- Input validation for graph correctness.
- Graceful termination on error conditions.

## Performance Considerations
- Partitioned work to maximize cache locality.
- Minimized false sharing by aligning data access.
- Benchmarked against sequential baseline to validate speedup.

