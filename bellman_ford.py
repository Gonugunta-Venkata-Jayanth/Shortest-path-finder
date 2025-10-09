from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import math
from graph import Graph

class ConcurrentBellmanFord:
    def __init__(self, graph: Graph, source: int, num_threads: int = 8):
        self.graph = graph
        self.source = source
        self.num_threads = num_threads
        self.dist = [math.inf] * graph.num_nodes
        self.dist[source] = 0.0
        # One lock per node distance for fine-grained concurrency
        self.locks = [threading.Lock() for _ in range(graph.num_nodes)]

    def _relax_partition(self, nodes):
        updated = False
        for u in nodes:
            dist_u = self.dist[u]
            if dist_u == math.inf:
                continue
            start = self.graph.node_ptrs[u]
            end = self.graph.node_ptrs[u + 1]
            for i in range(start, end):
                v = self.graph.edges_dst[i]
                w = self.graph.weights[i]
                new_dist = dist_u + w
                # Lock only target dist[v]
                lock = self.locks[v]
                with lock:
                    if new_dist < self.dist[v]:
                        self.dist[v] = new_dist
                        updated = True
        return updated

    def run(self):
        nodes = list(range(self.graph.num_nodes))
        with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            for _ in range(self.graph.num_nodes - 1):
                chunk_size = (len(nodes) + self.num_threads - 1) // self.num_threads
                futures = []
                updated_any = False
                for i in range(self.num_threads):
                    partition = nodes[i * chunk_size:(i + 1) * chunk_size]
                    futures.append(executor.submit(self._relax_partition, partition))
                for future in as_completed(futures):
                    if future.result():
                        updated_any = True
                if not updated_any:
                    break

        # Negative cycle detection (sequential for correctness)
        for u in range(self.graph.num_nodes):
            start = self.graph.node_ptrs[u]
            end = self.graph.node_ptrs[u + 1]
            dist_u = self.dist[u]
            if dist_u == math.inf:
                continue
            for i in range(start, end):
                v = self.graph.edges_dst[i]
                w = self.graph.weights[i]
                if dist_u + w < self.dist[v]:
                    raise ValueError("Graph contains a negative weight cycle")
        return self.dist


def bellman_ford_sequential(graph: Graph, source: int) -> list:
    dist = [math.inf] * graph.num_nodes
    dist[source] = 0.0
    for _ in range(graph.num_nodes - 1):
        updated = False
        for u in range(graph.num_nodes):
            dist_u = dist[u]
            if dist_u == math.inf:
                continue
            start = graph.node_ptrs[u]
            end = graph.node_ptrs[u + 1]
            for i in range(start, end):
                v = graph.edges_dst[i]
                w = graph.weights[i]
                if dist_u + w < dist[v]:
                    dist[v] = dist_u + w
                    updated = True
        if not updated:
            break

    # Negative cycle detection
    for u in range(graph.num_nodes):
        dist_u = dist[u]
        if dist_u == math.inf:
            continue
        start = graph.node_ptrs[u]
        end = graph.node_ptrs[u + 1]
        for i in range(start, end):
            v = graph.edges_dst[i]
            w = graph.weights[i]
            if dist_u + w < dist[v]:
                raise ValueError("Graph contains a negative weight cycle")
    return dist
