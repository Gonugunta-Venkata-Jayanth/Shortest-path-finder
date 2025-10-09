python : test_disconnected_graph (test_unit.TestShortestPath.test_disconnected_graph) ... ok
At C:\Users\Guest Login\Desktop\concurrent_shortest_path\run_all.ps1:1 char:1
+ python -m unittest test_unit.py -v
+ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : NotSpecified: (test_disconnect...d_graph) ... ok:String) [], RemoteException
    + FullyQualifiedErrorId : NativeCommandError
 
test_negative_cycle_detection_concurrent (test_unit.TestShortestPath.test_negative_cycle_detection_concurrent) ... ok
test_negative_cycle_detection_sequential (test_unit.TestShortestPath.test_negative_cycle_detection_sequential) ... ok
test_single_node_graph (test_unit.TestShortestPath.test_single_node_graph) ... ok
test_standard_sequential_and_concurrent (test_unit.TestShortestPath.test_standard_sequential_and_concurrent) ... ok

----------------------------------------------------------------------
Ran 5 tests in 0.097s

OK
[*] Benchmarking: nodes=2000, edge_prob=0.01, threads=8, allow_negative=True
Sequential detected error: Graph contains a negative weight cycle
Sequential time: 5.177s
Concurrent detected error: Graph contains a negative weight cycle
Concurrent time: 16.488s
[*] Running correctness tests...
Sequential distances: [0.0, 5.0, 3.0, 10.0, 7.0]
Concurrent distances: [0.0, 5.0, 3.0, 10.0, 7.0]
Correctly detected negative cycle in sequential: Graph contains a negative weight cycle
Correctly detected negative cycle in concurrent: Graph contains a negative weight cycle
