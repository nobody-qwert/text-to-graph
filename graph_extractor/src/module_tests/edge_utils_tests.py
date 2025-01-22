import unittest
import logging
from graph_extractor.src.edge_utils import extract_edge_labels
from graph_extractor.src.edge_utils import apply_edge_mappings

TEST_DATA_DIR = "test_data/edge_utils/"


class TestExtractEdgeTypes(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler()])

    def test_valid_file(self):
        edge_types = extract_edge_labels(TEST_DATA_DIR + "test_valid.json")
        self.assertEqual(edge_types, ["acknowledged", "authored", "related_to"])

    def test_missing_label(self):
        edge_types = extract_edge_labels(TEST_DATA_DIR + "test_missing_label.json")
        self.assertIsNone(edge_types)

    def test_no_edges(self):
        edge_types = extract_edge_labels(TEST_DATA_DIR + "test_no_edges.json")
        self.assertEqual(edge_types, [])

    def test_empty_file(self):
        edge_types = extract_edge_labels(TEST_DATA_DIR + "test_empty.json")
        self.assertEqual(edge_types, [])

    def test_invalid_format(self):
        edge_types = extract_edge_labels(TEST_DATA_DIR + "test_invalid_format.json")
        self.assertIsNone(edge_types)

    def test_non_existent_file(self):
        edge_types = extract_edge_labels(TEST_DATA_DIR + "non_existent.json")
        self.assertIsNone(edge_types)


class TestApplyEdgeMappings(unittest.TestCase):
    def setUp(self):
        self.graph1 = {
            "nodes": [
                {"id": "0", "label": "AAAA", "type": "aaaa"},
                {"id": "1", "label": "BBBB", "type": "bbbb"},
                {"id": "2", "label": "CCCC", "type": "cccc"},
                {"id": "3", "label": "DDDD", "type": "dddd"},
                {"id": "4", "label": "EEEE", "type": "eeee"}
            ],
            "edges": [
                {"source": "0", "target": "1", "label": "xxx1", "is_dir": True},
                {"source": "0", "target": "2", "label": "xxx2", "is_dir": True},
                {"source": "2", "target": "3", "label": "yyyy", "is_dir": True},
                {"source": "4", "target": "0", "label": "xxxx", "is_dir": True},
            ]
        }

        self.mapping_partial = {
            "old_to_new_edge_mapping": [
                {
                    "old_type": "xxx1",
                    "new_type": "xxxx",
                    "category_name": "yyyy"
                },
                {
                    "old_type": "xxx2",
                    "new_type": "xxxx",
                    "category_name": "yyyy"
                }
            ]
        }

        self.mapping_invalid_old_name = {
            "old_to_new_edge_mapping": [
                {
                    "old_type": "zzzz",
                    "new_type": "xxxx",
                    "category_name": "yyyy"
                },
                {
                    "old_type": "xxx2",
                    "new_type": "xxxx",
                    "category_name": "yyyy"
                }
            ]
        }

        self.mapping_empty = {
            "old_to_new_edge_mapping": [
            ]
        }

    def test_apply_edge_mappings_empty(self):
        graph = apply_edge_mappings(self.graph1, self.mapping_empty)
        self.assertEqual(len(graph["nodes"]), 5, "Not 5 edges created!")
        self.assertEqual(len(graph["edges"]), 4, "Not 4 edges created!")

        expected_edges = {
            ("0", "1", "xxx1", True, "uncategorized"),
            ("0", "2", "xxx2", True, "uncategorized"),
            ("2", "3", "yyyy", True, "uncategorized"),
            ("4", "0", "xxxx", True, "uncategorized")
        }

        actual_edges = {
            (edge["source"], edge["target"], edge["label"], edge["is_dir"], edge["category"])
            for edge in graph["edges"]
        }

        sorted_expected_edges = sorted(expected_edges, key=lambda x: (x[0], x[1], x[2], x[3], x[4]))
        sorted_actual_edges = sorted(actual_edges, key=lambda x: (x[0], x[1], x[2], x[3], x[4]))

        print()
        print("Expected:", sorted_expected_edges)
        print("Actual:  ", sorted_actual_edges)

    def test_apply_edge_mappings_invalid(self):
        graph = apply_edge_mappings(self.graph1, self.mapping_invalid_old_name)

        self.assertEqual(len(graph["nodes"]), 5, "Not 5 edges created!")
        self.assertEqual(len(graph["edges"]), 4, "Not 4 edges created!")

        expected_edges = {
            ("0", "1", "xxx1", True, "uncategorized"),
            ("0", "2", "xxxx", True, "yyyy"),
            ("2", "3", "yyyy", True, "uncategorized"),
            ("4", "0", "xxxx", True, "yyyy")
        }

        actual_edges = {
            (edge["source"], edge["target"], edge["label"], edge["is_dir"], edge["category"])
            for edge in graph["edges"]
        }

        sorted_expected_edges = sorted(expected_edges, key=lambda x: (x[0], x[1], x[2], x[3], x[4]))
        sorted_actual_edges = sorted(actual_edges, key=lambda x: (x[0], x[1], x[2], x[3], x[4]))

        print()
        print("Expected:", sorted_expected_edges)
        print("Actual:  ", sorted_actual_edges)

    def test_apply_edge_mappings_partial(self):
        graph = apply_edge_mappings(self.graph1, self.mapping_partial)

        self.assertEqual(len(graph["nodes"]), 5, "Not 5 edges created!")
        self.assertEqual(len(graph["edges"]), 4, "Not 4 edges created!")

        expected_edges = {
            ("0", "1", "xxxx", True, "yyyy"),
            ("0", "2", "xxxx", True, "yyyy"),
            ("2", "3", "yyyy", True, "uncategorized"),
            ("4", "0", "xxxx", True, "yyyy")
        }

        actual_edges = {
            (edge["source"], edge["target"], edge["label"], edge["is_dir"], edge["category"])
            for edge in graph["edges"]
        }

        sorted_expected_edges = sorted(expected_edges, key=lambda x: (x[0], x[1], x[2], x[3], x[4]))
        sorted_actual_edges = sorted(actual_edges, key=lambda x: (x[0], x[1], x[2], x[3], x[4]))

        print()
        print("Expected:", sorted_expected_edges)
        print("Actual:  ", sorted_actual_edges)

        self.assertEqual(sorted_expected_edges, sorted_actual_edges, "Edges are not merged uniquely")
        self.assertEqual(len(graph["nodes"]), 5, "Not 5 nodes created!")


if __name__ == "__main__":
    unittest.main()
