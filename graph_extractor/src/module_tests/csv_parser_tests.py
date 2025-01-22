from csv_parser import parse_text_to_dataframes

import unittest
from io import StringIO
import pandas as pd
import re


class TestParseTextToDataFrames(unittest.TestCase):

    def test_valid_input(self):
        """Test with valid input containing both nodes and edges."""
        text = """
        ```csv
        id,label,type
        0,"Node A","Type 1"
        1,"Node B","Type 2"

        source,target,label
        0,1,"connects to"
        ```"""
        result = parse_text_to_dataframes(text)
        self.assertIsNotNone(result)
        nodes_df, edges_df = result
        self.assertEqual(len(nodes_df), 2)
        self.assertEqual(len(edges_df), 1)

    def test_empty_input(self):
        """Test with empty input."""
        text = ""
        result = parse_text_to_dataframes(text)
        self.assertIsNone(result)

    def test_no_csv_blocks(self):
        """Test input without any ```csv blocks."""
        text = """
        This is some text without any CSV code blocks.
        """
        result = parse_text_to_dataframes(text)
        self.assertIsNone(result)

    def test_missing_edges_section(self):
        """Test input with only nodes section."""
        text = """
        ```csv
        id,label,type
        0,"Node A","Type 1"
        1,"Node B","Type 2"
        ```"""
        result = parse_text_to_dataframes(text)
        self.assertIsNone(result)

    def test_missing_nodes_section(self):
        """Test input with only edges section."""
        text = """
        ```csv
        source,target,label
        0,1,"connects to"
        ```"""
        result = parse_text_to_dataframes(text)
        self.assertIsNone(result)

    def test_invalid_csv_format(self):
        """Test input with invalid CSV formatting."""
        text = """
        ```csv
        id,label,type
        0,"Node A" "Type 1"
        1,"Node B","Type 2"

        source,target,label
        0,1,"connects to"
        ```"""
        result = parse_text_to_dataframes(text)
        self.assertIsNone(result)

    def test_extra_columns_in_nodes(self):
        """Test nodes CSV with extra columns."""
        text = """
        ```csv
        id,label,type,extra
        0,"Node A","Type 1","Extra Data"
        1,"Node B","Type 2","Extra Data"

        source,target,label
        0,1,"connects to"
        ```"""
        result = parse_text_to_dataframes(text)
        self.assertIsNotNone(result)
        nodes_df, _ = result
        self.assertIn('extra', nodes_df.columns)

    def test_missing_columns_in_edges(self):
        """Test edges CSV missing a required column."""
        text = """
        ```csv
        id,label,type
        0,"Node A","Type 1"
        1,"Node B","Type 2"

        source,target
        0,1
        ```"""
        result = parse_text_to_dataframes(text)
        self.assertIsNone(result)

    def test_inconsistent_data_types(self):
        """Test with inconsistent data types in IDs."""
        text = """
        ```csv
        id,label,type
        "zero","Node A","Type 1"
        1,"Node B","Type 2"

        source,target,label
        "zero",1,"connects to"
        ```"""
        result = parse_text_to_dataframes(text)
        self.assertIsNone(result)

    def test_nodes_without_id_column(self):
        """Test nodes CSV without 'id' column."""
        text = """
        ```csv
        label,type
        "Node A","Type 1"
        "Node B","Type 2"

        source,target,label
        0,1,"connects to"
        ```"""
        result = parse_text_to_dataframes(text)
        self.assertIsNone(result)

    def test_edges_without_label_column(self):
        """Test edges CSV without 'label' column."""
        text = """
        ```csv
        id,label,type
        0,"Node A","Type 1"
        1,"Node B","Type 2"

        source,target
        0,1
        ```"""
        result = parse_text_to_dataframes(text)
        self.assertIsNone(result)

    def test_unexpected_additional_data(self):
        """Test input with unexpected additional data in CSV."""
        text = """
        ```csv
        id,label,type
        0,"Node A","Type 1"
        1,"Node B","Type 2"
        Unexpected text
        2,"Node C","Type 3"

        source,target,label
        0,1,"connects to"
        1,2,"leads to"
        ```"""
        result = parse_text_to_dataframes(text)
        self.assertIsNone(result)

    def test_large_dataset(self):
        """Test with a large number of nodes and edges."""
        nodes_csv = "id,label,type\n" + "\n".join([f"{i},\"Node {i}\",\"Type {i%3}\"" for i in range(1000)])
        edges_csv = "source,target,label\n" + "\n".join([f"{i},{(i+1)%1000},\"connects to\"" for i in range(1000)])
        text = f"""
        ```csv
        {nodes_csv}

        {edges_csv}
        ```"""
        result = parse_text_to_dataframes(text)
        self.assertIsNotNone(result)
        nodes_df, edges_df = result
        self.assertEqual(len(nodes_df), 1000)
        self.assertEqual(len(edges_df), 1000)

    def test_edges_with_missing_values(self):
        """Test edges CSV with missing values."""
        text = """
        ```csv
        id,label,type
        0,"Node A","Type 1"
        1,"Node B","Type 2"

        source,target,label
        0,, "connects to"
        ```"""
        result = parse_text_to_dataframes(text)
        self.assertIsNone(result)

    def test_nodes_with_missing_values(self):
        """Test nodes CSV with missing values."""
        text = """
        ```csv
        id,label,type
        0,,"Type 1"
        1,"Node B","Type 2"

        source,target,label
        0,1,"connects to"
        ```"""
        result = parse_text_to_dataframes(text)
        self.assertIsNone(result)

    def test_incorrect_delimiters(self):
        """Test CSVs using incorrect delimiters."""
        text = """
        ```csv
        id;label;type
        0;"Node A";"Type 1"
        1;"Node B";"Type 2"

        source;target;label
        0;1;"connects to"
        ```"""
        result = parse_text_to_dataframes(text)
        self.assertIsNone(result)

    def test_nodes_with_additional_whitespace(self):
        """Test nodes CSV with additional whitespace."""
        text = """
        ```csv
        id , label , type
        0 , "Node A" , "Type 1"
        1 , "Node B" , "Type 2"

        source,target,label
        0,1,"connects to"
        ```"""
        result = parse_text_to_dataframes(text)
        self.assertIsNotNone(result)

    def test_edges_with_additional_whitespace(self):
        """Test edges CSV with additional whitespace."""
        text = """
        ```csv
        id,label,type
        0,"Node A","Type 1"
        1,"Node B","Type 2"

        source , target , label
        0 , 1 , "connects to"
        ```"""
        result = parse_text_to_dataframes(text)
        self.assertIsNotNone(result)

    def test_non_string_labels(self):
        """Test nodes and edges with non-string labels."""
        text = """
        ```csv
        id,label,type
        0,123,"Type 1"
        1,456,"Type 2"

        source,target,label
        0,1,789
        ```"""
        result = parse_text_to_dataframes(text)
        self.assertIsNotNone(result)

    def test_nodes_with_special_characters(self):
        """Test nodes with special characters in labels."""
        text = """
        ```csv
        id,label,type
        0,"Node A ©","Type 1"
        1,"Node B ®","Type 2"

        source,target,label
        0,1,"connects to ™"
        ```"""
        result = parse_text_to_dataframes(text)
        self.assertIsNotNone(result)

if __name__ == '__main__':
    unittest.main()
