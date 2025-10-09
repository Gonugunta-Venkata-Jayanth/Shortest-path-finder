import random
from typing import List, Tuple

class Graph:
    def __init__(self, num_nodes: int, edges: List[Tuple[int, int, float]]):
        self.num_nodes = num_nodes
        # Build CSR-like structure
        self.edges_src = []
        self.edges_dst = []
        self.weights = []

        # Temporary adjacency dict for sorting edges per node
        adj = [[] for _ in range(num_nodes)]
        for u, v, w in edges:
            adj[u].append((v, w))
        # Sort adjacency lists for locality
        for u in range(num_nodes):
            adj[u].sort(key=lambda x: x[0])
            for (v, w) in adj[u]:
                self.edges_src.append(u)
                self.edges_dst.append(v)
                self.weights.append(w)

        # Build index pointer for adjacency (start of neighbors for each node)
        self.node_ptrs = [0] * (num_nodes + 1)
        edge_index = 0
        for u in range(num_nodes):
            self.node_ptrs[u] = edge_index
            edge_index += len(adj[u])
        self.node_ptrs[num_nodes] = edge_index

    def neighbors(self, node: int) -> List[Tuple[int, float]]:
        start = self.node_ptrs[node]
        end = self.node_ptrs[node + 1]
        return [(self.edges_dst[i], self.weights[i]) for i in range(start, end)]

def generate_random_graph(num_nodes: int, edge_prob: float, weight_range: Tuple[float, float], allow_negative=False) -> Graph:
    edges = []
    for u in range(num_nodes):
        for v in range(num_nodes):
            if u != v and random.random() < edge_prob:
                w = random.uniform(*weight_range)
                if allow_negative and random.random() < 0.1:
                    w = -abs(w)
                edges.append((u, v, w))
    return Graph(num_nodes, edges)
