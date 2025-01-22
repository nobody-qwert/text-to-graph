import unittest
from graph_extractor.src.graph_utils import merge_graphs_unique


class TestMergeGraphsUnique(unittest.TestCase):
    def setUp(self):
        self.graph1 = {
            "nodes": [
                {"id": "0", "label": "AAAA", "type": "xxxx"},
                {"id": "1", "label": "BBBB", "type": "xxxx"},
                {"id": "2", "label": "CCCC", "type": "cccc"}
            ],
            "edges": [
                {"source": "0", "target": "1", "label": "AAAABBBB", "is_dir": True},
                {"source": "0", "target": "2", "label": "AAAACCCC", "is_dir": True}
            ]
        }

        self.graph3 = {
            "nodes": [
                {"id": "0", "label": "AAAA", "type": "1111"},
                {"id": "1", "label": "BBBB", "type": "2222"},
                {"id": "2", "label": "CCCC", "type": "3333"}
            ],
            "edges": [
                {"source": "0", "target": "1", "label": "AAAA1111", "is_dir": True},
                {"source": "1", "target": "2", "label": "BBBB3333", "is_dir": True},
                {"source": "0", "target": "2", "label": "AAAA3333", "is_dir": True},
                {"source": "0", "target": "1", "label": "AA__22__", "is_dir": True}
            ]
        }

        self.graph2 = {
            "nodes": [
                {"id": "0", "label": "DDDD", "type": "dddd"},
                {"id": "1", "label": "EEEE", "type": "eeee"},
                {"id": "2", "label": "AAAA", "type": "xxxx"}
            ],
            "edges": [
                {"source": "0", "target": "1", "label": "DDDDEEEE", "is_dir": True},
                {"source": "2", "target": "1", "label": "AAAAEEEE", "is_dir": True}
            ]
        }

        self.graph_duplicate = self.graph1

    def test_merge_two_valid_graphs(self):
        all_graphs = [self.graph1, self.graph2]
        merged_data = merge_graphs_unique(all_graphs)

        expected_nodes = {
            ("aaaa", "xxxx"),
            ("bbbb", "xxxx"),
            ("cccc", "cccc"),
            ("dddd", "dddd"),
            ("eeee", "eeee")
        }

        actual_nodes = {(node["label"].lower(), node["type"].lower()) for node in merged_data["nodes"]}
        sorted_expected_nodes = sorted(expected_nodes, key=lambda x: x[0])
        sorted_actual_nodes = sorted(actual_nodes, key=lambda x: x[0])

        print("\n", flush=True)
        print("Expected:", sorted_expected_nodes)
        print("Actual:  ", sorted_actual_nodes)

        self.assertEqual(sorted_expected_nodes, sorted_actual_nodes, "Nodes are not merged uniquely")

        expected_edges = {
            ("0", "1", "aaaabbbb", True),
            ("0", "2", "aaaacccc", True),
            ("3", "4", "ddddeeee", True),
            ("0", "4", "aaaaeeee", True)
        }


        actual_edges = {(edge["source"], edge["target"], edge["label"], edge["is_dir"]) for edge in merged_data["edges"]}
        sorted_expected_edges = sorted(expected_edges, key=lambda x: x[2])  # Sort by label (third element)
        sorted_actual_edges = sorted(actual_edges, key=lambda x: x[2])

        # print("Expected:", sorted_expected_edges)
        # print("Actual:  ", sorted_actual_edges)
        # print()

        self.assertEqual(sorted_expected_edges, sorted_actual_edges, "Edges are not merged uniquely")
        self.assertEqual(len(merged_data["nodes"]), 5, "Not 5 nodes created!")
        self.assertEqual(len(merged_data["edges"]), 4, "Not 4 edges created!")

    def test_merge_two_valid_graphs_similar_names_different_types(self):
        all_graphs = [self.graph1, self.graph3]
        merged_data = merge_graphs_unique(all_graphs)

        expected_nodes = {
            ("aaaa", "xxxx"),
            ("bbbb", "xxxx"),
            ("cccc", "cccc"),
            ("aaaa", "1111"),
            ("bbbb", "2222"),
            ("cccc", "3333"),
        }

        actual_nodes = {(node["label"].lower(), node["type"].lower()) for node in merged_data["nodes"]}
        sorted_expected_nodes = sorted(expected_nodes, key=lambda x: (x[0], x[1]))
        sorted_actual_nodes = sorted(actual_nodes, key=lambda x: (x[0], x[1]))

        # print("\n", flush=True)
        # print("Expected:", sorted_expected_nodes)
        # print("Actual:  ", sorted_actual_nodes)

        self.assertEqual(sorted_expected_nodes, sorted_actual_nodes, "Nodes are not merged uniquely")

        expected_edges = {
            ("0", "1", "aaaabbbb", True),
            ("3", "4", "aa__22__", True),
            ("0", "2", "aaaacccc", True),
            ("3", "4", "aaaa1111", True),
            ("4", "5", "bbbb3333", True),
            ("3", "5", "aaaa3333", True)
        }

        actual_edges = {(edge["source"], edge["target"], edge["label"], edge["is_dir"]) for edge in merged_data["edges"]}
        sorted_expected_edges = sorted(expected_edges, key=lambda x: (x[0], x[1], x[2]))
        sorted_actual_edges = sorted(actual_edges, key=lambda x: (x[0], x[1], x[2]))

        # print("Expected:", sorted_expected_edges)
        # print("Actual:  ", sorted_actual_edges)
        # print("\n", flush=True)

        self.assertEqual(sorted_expected_edges, sorted_actual_edges, "Edges are not merged uniquely")
        self.assertEqual(len(merged_data["nodes"]), 6, "Not 6 nodes created!")
        self.assertEqual(len(merged_data["edges"]), 6, "Not 6 edges created!")

    def test_merge_identical_graphs(self):
        all_graphs = [self.graph1, self.graph_duplicate]
        merged_data = merge_graphs_unique(all_graphs)

        expected_nodes = {
            ("aaaa", "xxxx"),
            ("bbbb", "xxxx"),
            ("cccc", "cccc")
        }

        actual_nodes = {(node["label"].lower(), node["type"].lower()) for node in merged_data["nodes"]}
        self.assertEqual(expected_nodes, actual_nodes, "Identical nodes are not merged correctly")

        expected_edges = {
            ("0", "1", "aaaabbbb", True),
            ("0", "2", "aaaacccc", True)
        }

        actual_edges = {(edge["source"], edge["target"], edge["label"], edge["is_dir"]) for edge in merged_data["edges"]}

        # print()
        # print(merged_data["nodes"])
        # print()
        # print(actual_edges)
        # print(expected_edges)
        # print()
        # print(merged_data["edges"])

        self.assertEqual(expected_edges, actual_edges, "Identical edges are not merged correctly")
        self.assertEqual(len(merged_data["nodes"]), 3, "Not 3 nodes created!")
        self.assertEqual(len(merged_data["edges"]), 2, "Not 2 edges created!")

    def test_empty_graph(self):
        empty_graph = {"nodes": [], "edges": []}
        merged_data = merge_graphs_unique([empty_graph])

        self.assertEqual(merged_data["nodes"], [], "Merged nodes should be empty for empty input graph")
        self.assertEqual(merged_data["edges"], [], "Merged edges should be empty for empty input graph")

    def test_single_node_edge_graph(self):
        single_graph = {
            "nodes": [{"id": "0", "label": "Single Node", "type": "single"}],
            "edges": [{"source": "0", "target": "0", "label": "self_loop", "is_dir": True}]
        }
        merged_data = merge_graphs_unique([single_graph])

        expected_nodes = {("single node", "single")}
        expected_edges = {("0", "0", "self_loop", True)}

        actual_nodes = {(node["label"].lower(), node["type"].lower()) for node in merged_data["nodes"]}
        actual_edges = {(edge["source"], edge["target"], edge["label"], edge["is_dir"]) for edge in merged_data["edges"]}

        self.assertEqual(expected_nodes, actual_nodes, "Single node not merged correctly")
        self.assertEqual(expected_edges, actual_edges, "Single edge not merged correctly")

    def test_conflicting_node_ids(self):
        graph1 = {
            "nodes": [{"id": "0", "label": "aaaa", "type": "xxxx"}],
            "edges": []
        }
        graph2 = {
            "nodes": [{"id": "1", "label": "aaaa", "type": "xxxx"}],
            "edges": []
        }
        merged_data = merge_graphs_unique([graph1, graph2])

        expected_nodes = {("aaaa", "xxxx")}
        actual_nodes = {(node["label"].lower(), node["type"].lower()) for node in merged_data["nodes"]}

        self.assertEqual(expected_nodes, actual_nodes, "Nodes with conflicting IDs were not merged correctly")
        self.assertEqual(len(merged_data["nodes"]), 1, "More than one node created for identical labels")

    def test_conflicting_node_ids_different_type(self):
        graph1 = {
            "nodes": [{"id": "0", "label": "aaaa", "type": "xxxx"}],
            "edges": []
        }
        graph2 = {
            "nodes": [{"id": "1", "label": "aaaa", "type": "yyyy"}],
            "edges": []
        }
        merged_data = merge_graphs_unique([graph1, graph2])

        expected_nodes = {
            ("aaaa", "xxxx"),
            ("aaaa", "yyyy")
        }
        actual_nodes = {(node["label"].lower(), node["type"].lower()) for node in merged_data["nodes"]}

        self.assertEqual(expected_nodes, actual_nodes, "Nodes with conflicting IDs were not merged correctly")
        self.assertEqual(len(merged_data["nodes"]), 2, "Not 2 nodes created!")

    def test_edges_with_duplicate_labels(self):
        graph1 = {
            "nodes": [
                {"id": "0", "label": "Node1", "type": "type1"},
                {"id": "1", "label": "Node2", "type": "type2"},
                {"id": "2", "label": "Node3", "type": "type3"}
            ],
            "edges": [
                {"source": "0", "target": "1", "label": "related", "is_dir": True},
                {"source": "0", "target": "2", "label": "related", "is_dir": True}
            ]
        }
        merged_data = merge_graphs_unique([graph1])

        expected_edges = {
            ("0", "1", "related", True),
            ("0", "2", "related", True)
        }
        actual_edges = {(edge["source"], edge["target"], edge["label"], edge["is_dir"]) for edge in
                        merged_data["edges"]}

        self.assertEqual(expected_edges, actual_edges,
                         "Edges with duplicate labels and different source-target pairs are not handled correctly")

    def test_self_loops_and_cycles(self):
        graph_with_loops = {
            "nodes": [
                {"id": "0", "label": "CycleNode", "type": "loop_type"},
                {"id": "1", "label": "AnotherNode", "type": "loop_type"}
            ],
            "edges": [
                {"source": "0", "target": "0", "label": "self_loop", "is_dir": True},
                {"source": "0", "target": "1", "label": "cycle_edge", "is_dir": True},
                {"source": "1", "target": "0", "label": "cycle_edge_back", "is_dir": True}
            ]
        }
        merged_data = merge_graphs_unique([graph_with_loops])

        expected_edges = {
            ("0", "0", "self_loop", True),
            ("0", "1", "cycle_edge", True),
            ("1", "0", "cycle_edge_back", True)
        }
        actual_edges = {(edge["source"], edge["target"], edge["label"], edge["is_dir"]) for edge in
                        merged_data["edges"]}

        self.assertEqual(expected_edges, actual_edges, "Self-loops and cycles are not handled correctly")


if __name__ == "__main__":
    unittest.main()
