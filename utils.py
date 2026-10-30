"""Helpers for reading graphs from text files."""
import math
from graph import Graph


def load_graph(path):
    """Read a graph in the sample/input.txt format.

    First line: "<num_nodes> <num_edges>"; then one "u v w" line per directed edge.
    Blank lines and lines starting with '#' are ignored.
    """
    with open(path, encoding="utf-8") as fh:
        lines = [ln.strip() for ln in fh if ln.strip() and not ln.lstrip().startswith("#")]
    if not lines:
        raise ValueError(f"{path}: empty graph file")
    num_nodes, num_edges = (int(x) for x in lines[0].split()[:2])
    edges = []
    for lineno, ln in enumerate(lines[1:], start=2):
        parts = ln.split()
        if len(parts) != 3:
            raise ValueError(f"{path}: expected 'u v w' on line {lineno}, got {ln!r}")
        u, v, w = int(parts[0]), int(parts[1]), float(parts[2])
        if not (0 <= u < num_nodes and 0 <= v < num_nodes):
            raise ValueError(f"{path}: node index out of range on line {lineno}")
        edges.append((u, v, w))
    if len(edges) != num_edges:
        raise ValueError(f"{path}: header says {num_edges} edges, found {len(edges)}")
    return Graph(num_nodes, edges)


def format_distance(d):
    """Format a distance for output: integers without a trailing .0, 'INF' if unreachable."""
    if d == math.inf:
        return "INF"
    return str(int(d)) if float(d).is_integer() else f"{d:.6g}"
