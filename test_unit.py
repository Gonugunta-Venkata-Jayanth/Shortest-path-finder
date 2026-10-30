import unittest
import time
from graph import Graph
from bellman_ford import bellman_ford_sequential, ConcurrentBellmanFord

class TestShortestPath(unittest.TestCase):

    def setUp(self):
        # Standard graph with mixed edges and no negative cycle
        self.standard_edges = [
            (0, 1, 5),
            (0, 2, 3),
            (1, 2, 2),
            (1, 3, 6),
            (2, 3, 7),
            (2, 4, 4),
            (3, 4, -1)
        ]
        self.standard_graph = Graph(5, self.standard_edges)

        # Graph with a negative cycle
        self.neg_cycle_edges = [
            (0, 1, 1),
            (1, 2, -1),
            (2, 0, -1)
        ]
        self.neg_cycle_graph = Graph(3, self.neg_cycle_edges)

        # Disconnected graph (some nodes unreachable)
        self.disconnected_edges = [
            (0, 1, 4),
            (2, 3, 5)
        ]
        self.disconnected_graph = Graph(5, self.disconnected_edges)

        # Single node graph
        self.single_node_graph = Graph(1, [])

        # Large sparse graph generator helper
        self.large_sparse_graph = self._generate_large_sparse_graph(1000, 0.001)

    def _generate_large_sparse_graph(self, n, edge_prob):
        import random
        edges = []
        for u in range(n):
            for v in range(u + 1, n):
                if random.random() < edge_prob:
                    edges.append((u, v, random.uniform(1, 10)))
        return Graph(n, edges)

    def test_standard_sequential_and_concurrent(self):
        # Test standard graph correctness
        expected = [0.0, 5.0, 3.0, 10.0, 7.0]

        seq_dist = bellman_ford_sequential(self.standard_graph, 0)
        conc_dist = ConcurrentBellmanFord(self.standard_graph, 0, num_threads=4).run()

        for i in range(len(expected)):
            self.assertAlmostEqual(seq_dist[i], expected[i], msg=f"Sequential failed at node {i}")
            self.assertAlmostEqual(conc_dist[i], expected[i], msg=f"Concurrent failed at node {i}")

    def test_negative_cycle_detection_sequential(self):
        with self.assertRaises(ValueError) as cm:
            bellman_ford_sequential(self.neg_cycle_graph, 0)
        self.assertIn("negative weight cycle", str(cm.exception).lower())

    def test_negative_cycle_detection_concurrent(self):
        with self.assertRaises(ValueError) as cm:
            ConcurrentBellmanFord(self.neg_cycle_graph, 0, num_threads=2).run()
        self.assertIn("negative weight cycle", str(cm.exception).lower())

    def test_disconnected_graph(self):
        # Distances should be infinity where nodes unreachable
        dist_seq = bellman_ford_sequential(self.disconnected_graph, 0)
        dist_conc = ConcurrentBellmanFord(self.disconnected_graph, 0, num_threads=3).run()

        self.assertEqual(dist_seq[0], 0.0)
        self.assertEqual(dist_conc[0], 0.0)
        self.assertEqual(dist_seq[1], 4.0)
        self.assertEqual(dist_conc[1], 4.0)

        # Unreachable nodes distances should be float('inf')
        for node in [2,3,4]:
            self.assertEqual(dist_seq[node], float('inf'))
            self.assertEqual(dist_conc[node], float('inf'))

    def test_single_node_graph(self):
        dist_seq = bellman_ford_sequential(self.single_node_graph, 0)
        dist_conc = ConcurrentBellmanFord(self.single_node_graph, 0, num_threads=1).run()
        self.assertEqual(dist_seq, [0.0])
        self.assertEqual(dist_conc, [0.0])

    def test_large_sparse_graph_performance(self):
        start = time.time()
        dist_seq = bellman_ford_sequential(self.large_sparse_graph, 0)
        seq_time = time.time() - start

        start = time.time()
        dist_conc = ConcurrentBellmanFord(self.large_sparse_graph, 0, num_threads=8).run()
        conc_time = time.time() - start

        for d_seq, d_conc in zip(dist_seq, dist_conc):
            self.assertAlmostEqual(d_seq, d_conc)

        self.assertLess(seq_time, 30, f"Sequential took too long: {seq_time}s")

        if seq_time > 0.01:
            self.assertLess(conc_time, seq_time * 5, f"Concurrent too slow: {conc_time}s")
        else:
            print(f"Warning: sequential time very low ({seq_time}s), skipping concurrency speed test")

    def test_concurrent_repeatability(self):
        # Run concurrent algorithm multiple times to catch race conditions
        for _ in range(5):
            dist1 = ConcurrentBellmanFord(self.standard_graph, 0, num_threads=4).run()
            dist2 = ConcurrentBellmanFord(self.standard_graph, 0, num_threads=4).run()
            self.assertEqual(dist1, dist2, "Concurrent runs differ — potential race condition")

    def test_zero_edges_graph(self):
        # Graph with nodes but no edges
        g = Graph(4, [])
        dist_seq = bellman_ford_sequential(g, 0)
        dist_conc = ConcurrentBellmanFord(g, 0, num_threads=2).run()
        expected = [0.0, float('inf'), float('inf'), float('inf')]
        self.assertEqual(dist_seq, expected)
        self.assertEqual(dist_conc, expected)

    def test_sample_input_file_matches_expected_output(self):
        # sample/input.txt solved from node 0 must match sample/output.txt
        import os
        from utils import load_graph, format_distance
        here = os.path.dirname(os.path.abspath(__file__))
        g = load_graph(os.path.join(here, 'sample', 'input.txt'))
        with open(os.path.join(here, 'sample', 'output.txt'), encoding='utf-8') as fh:
            expected = [ln.strip() for ln in fh if ln.strip()]
        for solver in (lambda: bellman_ford_sequential(g, 0),
                       lambda: ConcurrentBellmanFord(g, 0, num_threads=2).run()):
            self.assertEqual([format_distance(d) for d in solver()], expected)


if __name__ == '__main__':
    unittest.main()
