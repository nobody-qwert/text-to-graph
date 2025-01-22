import json
import os
import logging


def extract_edge_labels(json_file_path):
    if not os.path.exists(json_file_path):
        logging.warning(f"File \"{json_file_path}\" does not exist!")
        return None

    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)

        if data is not None:
            edge_labels = {edge['label'] for edge in data.get("edges", [])}
            return sorted(edge_labels)

    except FileNotFoundError:
        logging.error(f"File not found. Please check the file path: {json_file_path}")
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON. Please ensure the file is correctly formatted: {json_file_path}")
    except KeyError:
        logging.error(f"Error: Missing 'label' field in one or more edges: {json_file_path}")

    return None


def apply_edge_mappings(graph, old_to_new_mappings):

    mapping_dict = {
        entry['old_type']: (entry['new_type'])
        for entry in old_to_new_mappings['old_to_new_edge_mapping']
    }

    for edge in graph['edges']:
        old_type = edge['label']
        if old_type in mapping_dict:
            edge['label'] = mapping_dict[old_type]

    return graph


def main():
    return None


if __name__ == "__main__":
    main()
