from io import StringIO
import sqlite_support
from log_utils import get_module_logger
import pandas as pd

logging = get_module_logger("graph_utils")


def sanitize(text: str) -> str:
    return text.replace('|', '_').strip()


def merge_graphs_unique(all_graphs):
    if not all_graphs:
        logging.warning("Nothing to merge -> merge_graphs_unique() called with empty graphs list!")
        return pd.DataFrame(), pd.DataFrame()

    unique_entities = {}
    next_entity_id = 0
    unique_edges = set()

    for graph in all_graphs:
        df_nodes = graph['nodes']
        df_edges = graph['edges']

        entity_id_map = {}

        for _, node_data in df_nodes.iterrows():
            node_label = sanitize(node_data['label'])
            entity_key = node_label.lower()

            node_type = sanitize(node_data['type'])

            if entity_key in unique_entities:
                new_id = unique_entities[entity_key]['id']
                unique_entities[entity_key]['types'].add(node_type)
            else:
                new_id = next_entity_id
                next_entity_id += 1

                unique_entities[entity_key] = {
                    'id': int(new_id),
                    'base_label': node_label,
                    'types': set([node_type]),
                }

            original_id = node_data['id']
            entity_id_map[original_id] = new_id

        for _, edge_data in df_edges.iterrows():
            source_orig = edge_data["source"]
            target_orig = edge_data["target"]
            raw_edge_label = edge_data.get("label", "")
            edge_label = sanitize(raw_edge_label)

            if source_orig not in entity_id_map or target_orig not in entity_id_map:
                continue

            source = entity_id_map[source_orig]
            target = entity_id_map[target_orig]
            edge_key = (source, target, edge_label.lower())

            if edge_key not in unique_edges:
                unique_edges.add(edge_key)

    merged_nodes_list = []
    for entity_key, info in unique_entities.items():
        all_types_str = '|'.join(sorted(t for t in info['types'] if t))

        merged_nodes_list.append({
            'id': info['id'],
            'label': info['base_label'],
            'type': all_types_str
        })

    df_merged_nodes = pd.DataFrame(merged_nodes_list)

    merged_edges_list = []
    for (src_id, tgt_id, label_lower) in unique_edges:
        merged_edges_list.append({
            "source": src_id,
            "target": tgt_id,
            "label": label_lower
        })

    df_merged_edges = pd.DataFrame(merged_edges_list)

    return df_merged_nodes, df_merged_edges


def merge_graphs(document_id, config_id, metadata):
    graphs = []
    responses = sqlite_support.get_all_responses_for(
        document_id,
        config_id
    )

    for r in responses:
        df_nodes = pd.read_csv(StringIO(r["nodes"]))
        df_edges = pd.read_csv(StringIO(r["edges"]))

        logging.info(f"Merge responses {df_nodes}")
        logging.info(f"Merge responses {df_edges}")

        df_nodes['id'] = pd.to_numeric(df_nodes['id'], errors='coerce')
        df_nodes.dropna(subset=['id'], inplace=True)
        df_nodes['id'] = df_nodes['id'].astype(int)
        df_nodes = df_nodes[df_nodes['id'] >= 0]

        df_edges['source'] = pd.to_numeric(df_edges['source'], errors='coerce')
        df_edges['target'] = pd.to_numeric(df_edges['target'], errors='coerce')
        df_edges.dropna(subset=['source', 'target'], inplace=True)
        df_edges['source'] = df_edges['source'].astype(int)
        df_edges['target'] = df_edges['target'].astype(int)

        df_edges = df_edges[(df_edges['source'] >= 0) & (df_edges['target'] >= 0)]

        df_nodes['label'] = df_nodes['label'].astype(str)
        df_edges['label'] = df_edges['label'].astype(str)

        graphs.append({'nodes': df_nodes, 'edges': df_edges})

    nodes, edges = merge_graphs_unique(graphs)

    nodes_string = nodes.to_csv(index=False)
    edges_string = edges.to_csv(index=False)

    graph_id = sqlite_support.insert_graph(
        document_id,
        config_id,
        nodes_string,
        edges_string,
        metadata
    )

    logging.info(f"Merged Graph ID {graph_id}, {len(nodes)} Nodes, {len(edges)} Edges")

    logging.info(f"Finished graph\n{nodes}")
    logging.info(f"Finished graph\n{edges}")

    return nodes, edges


def merge_all_document_graphs(all_graphs):
    entity_map = {}
    next_entity_id = 0

    edge_map = {}

    for doc_index, (pdf_filename, df_nodes, df_edges) in enumerate(all_graphs):
        node_id_to_label = {}

        logging.info(f"=>>>>>>>>>>>>>>>>>>>>>\n{df_edges}")

        for _, node_row in df_nodes.iterrows():
            original_id = int(node_row['id'])
            raw_label = str(node_row['label'])
            node_type = str(node_row.get('type'))

            node_label = sanitize(raw_label)
            node_label_lower = node_label.lower()

            logging.info(f"Processing Node({original_id}) {raw_label}  ->  {node_type} ")

            node_id_to_label[original_id] = node_label

            if not node_label:
                logging.warning(f"{pdf_filename} - Label is none after sanitized {raw_label}")
                continue

            if node_label_lower not in entity_map:
                entity_map[node_label_lower] = {
                    'id': int(next_entity_id),
                    'base_label': node_label,
                    'types': {node_type},
                    'doc_set': {doc_index}
                }
                next_entity_id += 1
            else:
                entity_map[node_label_lower]['types'].add(node_type)
                entity_map[node_label_lower]['doc_set'].add(doc_index)

        for _, edge_row in df_edges.iterrows():
            src_orig = edge_row['source']
            tgt_orig = edge_row['target']

            logging.info(f"Processing Edge {edge_row['label']} {src_orig} {tgt_orig}")

            raw_edge_label = str(edge_row['label'])
            edge_label = sanitize(raw_edge_label)
            edge_label_lower = edge_label.lower()

            if src_orig not in node_id_to_label or tgt_orig not in node_id_to_label:
                logging.warning(f"Not found {src_orig} or {tgt_orig} in {node_id_to_label}")
                continue

            src_node_label_lower = node_id_to_label[src_orig].lower()
            tgt_node_label_lower = node_id_to_label[tgt_orig].lower()

            final_src_id = entity_map[src_node_label_lower]['id']
            final_tgt_id = entity_map[tgt_node_label_lower]['id']

            edge_key = (final_src_id, final_tgt_id, edge_label_lower)

            if edge_key not in edge_map:
                edge_map[edge_key] = {
                    'source': final_src_id,
                    'target': final_tgt_id,
                    'base_label': edge_label,
                    'doc_set': {doc_index}
                }
            else:
                edge_map[edge_key]['doc_set'].add(doc_index)

    merged_nodes_list = []
    for node_label_lower, info in entity_map.items():
        if len(info['types']) > 1:
            logging.info(f"Label '{info['base_label']}' has multiple types: {info['types']}")

        doc_str = '|'.join(str(d) for d in sorted(info['doc_set']))
        final_label = f"{info['base_label']}|{doc_str}"

        all_types_str = '|'.join(sorted(t for t in info['types'] if t))

        merged_nodes_list.append({
            'id': info['id'],
            'label': final_label,
            'type': all_types_str
        })

    merged_nodes = pd.DataFrame(merged_nodes_list)

    logging.info(f"Merged Nodes\n{merged_nodes}")

    merged_edges_list = []
    for (src_id, tgt_id, edge_label_lower), info in edge_map.items():
        logging.info(f"Merging edge {edge_label_lower}")
        doc_str = '|'.join(str(d) for d in sorted(info['doc_set']))
        final_edge_label = f"{info['base_label']}|{doc_str}"

        merged_edges_list.append({
            'source': src_id,
            'target': tgt_id,
            'label': final_edge_label
        })

    merged_edges = pd.DataFrame(merged_edges_list)

    logging.info(f"Merged Edges\n{merged_edges}")

    return merged_nodes, merged_edges
