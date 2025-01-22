import pandas as pd
import csv
import io
from log_utils import get_module_logger
from io import StringIO

logging = get_module_logger("response_parser")


def parse_text_to_dataframes(text):
    try:
        lines = text.splitlines()
        if not lines:
            logging.warning("Input text is empty. Returning empty DataFrames.")
            return pd.DataFrame(), pd.DataFrame()

        nodes_lines = []
        edges_lines = []
        in_nodes = False
        in_edges = False

        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.startswith('id,entity,category'):
                in_nodes = True
                in_edges = False
                nodes_lines.append(line)
            elif line.startswith('source,target,relationship'):
                in_nodes = False
                in_edges = True
                edges_lines.append(line)
            elif line.startswith('#') or line.startswith('```'):
                continue
            elif in_nodes:
                nodes_lines.append(line)
            elif in_edges:
                edges_lines.append(line)

        nodes_df = pd.DataFrame(columns=['id', 'entity', 'category'])
        edges_df = pd.DataFrame(columns=['source', 'target', 'relationship'])

        if nodes_lines:
            nodes_csv = '\n'.join(nodes_lines)
            valid_nodes_lines = validate_csv_rows(nodes_csv, ['id', 'entity', 'category'])
            if valid_nodes_lines is None or len(valid_nodes_lines) <= 1:
                logging.error("No valid node rows found after validation.")
                return None, None

            try:
                nodes_df = pd.read_csv(StringIO('\n'.join(valid_nodes_lines)))
            except Exception as e:
                logging.exception("Failed to read nodes CSV into DataFrame.")
                return None, None

            if nodes_df.empty:
                logging.warning("Nodes DataFrame is empty after parsing.")
            if nodes_df['id'].duplicated().any():
                logging.error("Duplicate IDs found in nodes.")
                return None, None

            if not nodes_df['id'].apply(lambda x: isinstance(x, (int, str))).all():
                logging.error("Inconsistent ID types found in nodes.")
                return None, None

            try:
                nodes_df = nodes_df.set_index("id")
            except Exception as e:
                logging.exception("Failed to set 'id' as index for nodes DataFrame.")
                return None, None
        else:
            logging.warning("No node section found. Returning empty node DataFrame.")

        if edges_lines:
            edges_csv = '\n'.join(edges_lines)
            valid_edges_lines = validate_csv_rows(edges_csv, ['source', 'target', 'relationship'])
            if valid_edges_lines is None or len(valid_edges_lines) <= 1:
                logging.error("No valid edge rows found after validation.")
                return nodes_df, None

            try:
                edges_df = pd.read_csv(StringIO('\n'.join(valid_edges_lines)))
            except Exception as e:
                logging.error(f"Failed to read edges CSV into DataFrame. {e}")
                return nodes_df, None
        else:
            logging.warning("No edge section found. Returning empty edge DataFrame.")

        try:
            nodes_df = nodes_df.rename(columns={
                'entity': 'label',
                'category': 'type'
            })
            edges_df = edges_df.rename(columns={
                'relationship': 'label'
            })
        except Exception as e:
            logging.exception("Failed to rename columns.")
            return None, None

        edges_df.drop_duplicates(subset=['source', 'target', 'label'], inplace=True)

        logging.info("---------------------------------------------------------------------")
        logging.info(f"\n{nodes_df}")
        logging.info(f"\n{edges_df}")
        nodes_clean_df, edges_clean_df = remove_orphan_nodes_and_reindex(nodes_df, edges_df)
        # nodes_clean_df, edges_clean_df = nodes_df, edges_df
        logging.info(f"\n{nodes_clean_df}")
        logging.info(f"\n{edges_clean_df}")

        return nodes_clean_df, edges_clean_df

    except Exception as e:
        logging.exception("An error occurred while parsing text to DataFrames.")
        return None, None


def validate_csv_rows(csv_text, expected_columns):
    lines = csv_text.splitlines()
    if not lines:
        logging.error("CSV text is empty. Cannot validate.")
        return None

    header_fields = lines[0].strip().split(',')
    if len(header_fields) != len(expected_columns):
        logging.error(f"Header does not match expected columns. Expected: {expected_columns}, Got: {header_fields}")
        return None

    valid_lines = [lines[0]]
    for i, line in enumerate(lines[1:], start=2):
        line_stripped = line.strip()
        if not line_stripped:
            logging.warning(f"Empty or whitespace-only line at {i}. Skipping.")
            continue
        fields = next(csv.reader([line_stripped], skipinitialspace=True))
        if len(fields) != len(expected_columns):
            logging.warning(f"Invalid row at line {i}: {line}. Expected {len(expected_columns)} columns.")
            continue
        valid_lines.append(line_stripped)

    if len(valid_lines) == 1:
        logging.warning("No valid data rows found in the CSV after validation.")
    return valid_lines


def parse_nodes(response):
    try:
        if not isinstance(response, str):
            logging.warning("parse_nodes received a non-string response.")
            return None

        response = response.strip()
        if not response:
            logging.warning("parse_nodes received an empty response after stripping.")
            return None

        reader = csv.reader(io.StringIO(response), skipinitialspace=True)
        entities = next(reader, None)

        if entities is None:
            logging.warning("No entities could be read from the response.")
            return None

        entities = [entity.strip() for entity in entities if entity.strip()]

        if not entities:
            logging.warning("All extracted entities are empty after trimming.")
            return None

        return entities

    except Exception as e:
        logging.exception("An error occurred in parse_nodes.")
        return None


def remove_orphan_nodes_and_reindex(nodes_df, edges_df):
    if nodes_df is None or edges_df is None:
        return nodes_df, edges_df
    if "source" not in edges_df.columns or "target" not in edges_df.columns:
        return nodes_df, edges_df

    referenced_node_ids = set(edges_df["source"].unique()) | set(edges_df["target"].unique())

    all_node_ids = set(nodes_df.index)
    orphan_node_ids = all_node_ids - referenced_node_ids

    cleaned_nodes_df = nodes_df.drop(index=orphan_node_ids, errors="ignore").copy()

    old_ids = list(cleaned_nodes_df.index)
    new_ids = list(range(len(cleaned_nodes_df)))  # 0..N-1
    old_to_new = dict(zip(old_ids, new_ids))

    cleaned_nodes_df["id"] = cleaned_nodes_df.index.map(old_to_new)
    cleaned_nodes_df.set_index("id", inplace=True)

    cleaned_edges_df = edges_df.copy()
    cleaned_edges_df["source"] = cleaned_edges_df["source"].map(old_to_new)
    cleaned_edges_df["target"] = cleaned_edges_df["target"].map(old_to_new)

    # cleaned_edges_df.dropna(subset=["source", "target"], inplace=True)

    cleaned_edges_df["source"] = cleaned_edges_df["source"].astype(int)
    cleaned_edges_df["target"] = cleaned_edges_df["target"].astype(int)

    return cleaned_nodes_df, cleaned_edges_df


def main():
    print("\n\n==================Node Label Parse tests========================\n\n")

    sample_response = '''"cot1.pl-SnEt4r", "SAC.TE", "coto'l".Et'IE'HT", "e.u..s", "el.6OC> VES:!.E:LS", "Mtclf'tGr", "IN.-L.AI"'4I'\ATo'tY CI"WS", "f'StoTE'1", "Figure 8-2", "CHAFT'ER 8", "THE IMMUNE SYSTEM", "Opsonization", "C3b", "bacteria", "neutrophils", "macrophages", "phagocytose", "Mnemonic", "C,3", "b", "antibodies", "antigen", "phagocytic cells", "red cells", "liver", "tipleen", "bacteria", "viruses", "bacterial agglutination", "virulence", "viruses"'''
    entities_list = parse_nodes(sample_response)
    print(entities_list)
    print("--------")

    sample_response = '"Multi RS Solar", "HTML5", "ENGLISH", "Multi RS Solar Product Manual", "Safety Instructions", "General Description", "Two AC outputs", "PowerControl", "PowerAssist", "Programmable", "Programmable relay", "Programmable analog/digital input/output ports", "Built-in Battery Monitor", "High efficiency", "Frequency shift function", "High power inverter", "Interfacing and Communications", "Battery charger", "Lead-acid batteries", "Li-ion batteries", "batteries", "battery charging", "Setup options", "Limitations"'
    entities_list = parse_nodes(sample_response)
    print(entities_list)

    sample_response = '"123"'
    entities_list = parse_nodes(sample_response)
    print(entities_list)

    sample_response = '\"\"'
    entities_list = parse_nodes(sample_response)
    print(entities_list)

    sample_response = 'asdfdasfg'
    entities_list = parse_nodes(sample_response)
    print(entities_list)

    sample_response = ';;;'
    entities_list = parse_nodes(sample_response)
    print(entities_list)

    sample_response = ',,,'
    entities_list = parse_nodes(sample_response)
    print(entities_list)

    sample_response = '"'
    entities_list = parse_nodes(sample_response)
    print(entities_list)

    sample_response = ',",'
    entities_list = parse_nodes(sample_response)
    print(entities_list)

    print("\n\n==================CSV Parse tests========================\n\n")

    text_1 = """
    ```csv
    id,entity,category
    0,"Jacob Ludwig Grimm","Person"
    1,"Wilhelm Carl Grimm","Person"
    2,"Grimm's Fairy Tales","Literary Work"
    3,"Snow-white","Character"
    4,"Seven Dwarfs","Character"
    5,"Queen","Character"
    6,"King","Character"
    7,"Huntsman","Character"
    8,"Germany","Location"
    9,"Kinder- und Hausmarchen","Literary Work"
    10,"Looking-glass","Object"
    11,"Wild Boar","Animal"
    12,"House","Location"
    13,"Mountains","Location"
    14,"Peddler Woman","Disguise"
    15,"Old Woman","Disguise"

    source,target,relationship
    0,2,"co-authored"
    1,2,"co-authored"
    0,9,"co-authored"
    1,9,"co-authored"
    9,2,"translated_to"
    3,5,"escaped_from"
    3,4,"lives_with"
    5,10,"uses"
    5,3,"envies"
    5,7,"commands"
    7,3,"spares"
    7,11,"kills"
    3,12,"finds"
    4,12,"owns"
    4,3,"shelters"
    5,14,"disguises_as"
    5,15,"disguises_as"
    5,3,"attacks"
    ```"""

    text_2 = """
    ```csv
    id,entity,category
    0,"Multi RS Solar","Product"
    1,"Victron","Organization"
    2,"Inverter/Charger","Component"
    3,"MPPT Solar Charge Controller","Component"
    4,"Multi RS Solar 48/6000/100-450/100 - PMR482602020","Product"
    5,"Firmware","Software"
    6,"Victron Dealer","Organization"
    7,"Victron Sales Manager","Person"
    8,"Battery","Component"
    9,"PV Modules","Component"
    10,"Installation Manual","Document"
    11,"Safety Instructions","Document"
    12,"Tri-rated Cable","Component"
    13,"IEC 61730 Class A","Standard"
    14,"VDE 0295","Standard"
    15,"IEC 60228","Standard"
    16,"BS6360","Standard"
    ```
    
    ```csv
    source,target,relationship
    0,1,"integrates"
    0,2,"includes"
    0,3,"includes"
    0,4,"applies_to"
    0,5,"requires"
    1,6,"employs"
    1,7,"employs"
    8,0,"powers"
    9,0,"powers"
    10,0,"guides"
    11,0,"guides"
    12,8,"connects"
    12,9,"connects"
    9,13,"requires"
    12,14,"complies_with"
    12,15,"complies_with"
    12,16,"complies_with"
    ```
    """

    text_3 = """
    # Nodes CSV table
    id,entity,category
    0,"Multi RS Solar","Product"
    1,"AC cabling","Component"
    2,"ground terminal","Component"
    3,"ground relay H","Component"
    4,"chassis","Component"
    5,"shore current plug","Component"
    6,"isolation transformer","Component"
    7,"printed circuit board","Component"
    8,"AC-out-1","Component"
    9,"AC-out-2","Component"
    10,"AC-in","Component"
    11,"VE.Direct","Interface"
    12,"PC/laptop","Device"
    13,"VE.Direct to USB accessory","Accessory"
    14,"Victron GlobalLink 520","Device"
    15,"GX device","Device"
    16,"VE.Can","Interface"
    17,"Bluetooth","Interface"
    18,"VictronConnect","Software"
    19,"Remote on/off connector","Component"
    20,"Remote L","Terminal"
    21,"Remote H","Terminal"
    22,"BMS","Device"
    23,"Programmable relay","Component"
    24,"Voltage sense","Component"
    25,"Temperature sensor","Component"
    26,"User I/O","Component"
    27,"AUX_IN1+","Terminal"
    28,"AUX_IN2+","Terminal"
    29,"Victron lithium battery BMS","Device"
    30,"MPPT Solar Charge Controller","Device"
    
    # Edges CSV table
    source,target,relationship
    0,1,"connects_to"
    0,2,"includes"
    0,3,"includes"
    0,4,"connects_to"
    0,5,"connects_to"
    0,6,"uses"
    0,7,"contains"
    0,8,"provides"
    0,9,"provides"
    0,10,"connects_to"
    11,12,"connects_to"
    11,13,"uses"
    11,14,"connects_to"
    15,16,"connects_to"
    17,18,"uses"
    19,20,"includes"
    19,21,"includes"
    22,20,"connects_to"
    22,21,"connects_to"
    23,0,"includes"
    24,0,"includes"
    25,0,"includes"
    26,27,"includes"
    26,28,"includes"
    29,22,"controls"
    30,18,"configures"
    """

    text_4 = """
    ```csv
    id,entity,category
    0,"Multi RS Solar","Product"
    1,"Victron","Organization"
    2,"Inverter/Charger","Component"
    3,"MPPT Solar Charge Controller","Component"
    4,"Firmware","Software"
    5,"Victron Dealer","Organization"
    6,"Victron Sales Manager","Person"
    7,"Battery","Component"
    8,"Solar Modules","Component"
    9,"Cable","Component"
    10,"PV Modules","Component"
    11,"Installation Manual","Document"
    12,"Safety Instructions","Document"
    13,"Environment","Location"
    14,"IEC 61730 Class A","Standard"
    15,"VDE 0295","Standard"
    16,"IEC 60228","Standard"
    17,"BS6360","Standard"
    18,"UL","Standard"
    19,"CSA","Standard"
    20,"BS","Standard"
    21,"Tri-rated Cable","Component"
    22,"AC Mains","Component"
    23,"PV Array","Component"
    24,"Installation Location","Location"
    25,"Enclosure","Component"
    26,"Australia & New Zealand","Location"
    ```
    
    ```csv
    source,target,relationship
    0,1,"integrates"
    0,2,"includes"
    0,3,"includes"
    0,4,"requires"
    0,5,"consult"
    0,6,"consult"
    0,7,"connects_to"
    0,8,"connects_to"
    0,9,"connects_to"
    0,10,"requires"
    0,11,"contains"
    0,12,"contains"
    0,13,0,"operates_in"
    0,14,10,"requires"
    0,15,9,"follows"
    0,16,9,"follows"
    0,17,9,"follows"
    0,18,21,"approves"
    0,19,21,"approves"
    0,20,21,"approves"
    0,22,23,"connects_to"
    0,24,0,"houses"
    0,25,0,"contains"
    0,26,0,"complies_with"
    ```
    """

    text_5 = """
    ```
    # CSV containing nodes
    id,entity,category
    0,"Multi RS Solar","Product"
    1,"Victron","Organization"
    2,"Inverter/Charger","Component"
    3,"MPPT Solar Charge Controller","Component"
    4,"Battery","Component"
    5,"PV Modules","Component"
    6,"Firmware","Software"
    7,"Victron Dealer","Organization"
    8,"Victron Sales Manager","Person"
    9,"Installation Manual","Document"
    10,"Safety Instructions","Document"
    11,"Tri-rated Cable","Component"
    12,"IEC 61730 Class A","Standard"
    13,"AC Mains","Component"
    14,"PV Array","Component"
    
    # CSV containing edges which correspond to relationships
    source,target,relationship
    0,1,"manufactured_by"
    0,2,"integrates"
    0,3,"integrates"
    0,4,"requires"
    0,5,"requires"
    0,6,"requires"
    0,7,"contact"
    0,8,"contact"
    0,9,"includes"
    0,10,"includes"
    11,4,"connects_to"
    12,5,"requires"
    13,14,"compares_to"
    ```
    """

    text_6 = """
    # Nodes CSV
    id,entity,category
    0,"EN-IEC 60335-1","Standard"
    1,"EN-IEC 60335-2-29","Standard"
    2,"EN-IEC 62109-1","Standard"
    3,"EN-IEC 62109-2","Standard"
    
    # Edges CSV
    """

    text_7 = """
        ```
        # CSV containing nodes
        id,entity,category
        0,"Multi RS Solar","Product"
        1,"Victron","Organization"
        
        # CSV containing edges which correspond to relationships
        source,target,relationship
        0,1,"manufactured_by"
        0,1,"manufactured_by"
        0,1,"manufactured_by"
        0,1,"manufactured_by"
        0,1,"manufactured_by"
        0,1,"manufactured_by"
        0,1,"manufactured_by"
        0,1,"manufactured_by"
        0,1,"manufactured_by"
        0,1,"manufactured_by"
        0,1,"manufactured_by"
        0,1,"manufactured_by"
        ```
        """
    text_8 = """
        ```
        # CSV containing nodes
        id,entity,category
        0,"Multi RS Solar","Product"
        1,"Victron","Organization"

        # CSV containing edges which correspond to relationships
        source,target,relationship
        0,1,"manufactured_by"
        ```
        """

    text_9 = """
            ```
            # CSV containing nodes
            id,entity,category
            0,"Multi RS Solar","Product"
            1,"Victron","Organization"

            # CSV containing edges which correspond to relationships
            source,target,relationship
            0,1,"manufactured_by"
            0,
            ```
            """

    text_10 = """
                ```
                # CSV containing nodes
                id,entity,category
                0,"Edmonton, Alberta","Location"
                1,"Cleveland Press, June 19, 1938","Document"

                # CSV containing edges which correspond to relationships
                source,target,relationship
                0,1,"manufactured_by"
                ```
                """
    # Test with text_1
    logging.info("Testing with text_1")
    result = parse_text_to_dataframes(text_1)
    if result is not None:
        nodes_df, edges_df = result
        logging.info(nodes_df)
        logging.info(edges_df)
    else:
        logging.error("Parsing was unsuccessful for text_1.")

    # Test with text_2
    logging.info("Testing with text_2")
    result = parse_text_to_dataframes(text_2)
    if result is not None:
        nodes_df, edges_df = result
        logging.info(nodes_df)
        logging.info(edges_df)
    else:
        logging.error("Parsing was unsuccessful for text_2.")

    logging.info("Testing with text_3")
    result = parse_text_to_dataframes(text_3)
    if result is not None:
        nodes_df, edges_df = result
        logging.info(nodes_df)
        logging.info(edges_df)
    else:
        logging.error("Parsing was unsuccessful for text_3.")

    logging.info("Testing with text_4")
    result = parse_text_to_dataframes(text_4)
    if result is not None:
        nodes_df, edges_df = result
        logging.info(nodes_df)
        logging.info(edges_df)
    else:
        logging.info("Parsing was unsuccessful for text_4. As expected")

    logging.info("Testing with text_5 xxx")
    result = parse_text_to_dataframes(text_5)
    if result is not None:
        nodes_df, edges_df = result
        logging.info(nodes_df)
        logging.info(edges_df)
    else:
        logging.error("Parsing was unsuccessful for text_5.")

    logging.info("Testing with text_6")
    result = parse_text_to_dataframes(text_6)
    if result is not None:
        nodes_df, edges_df = result
        logging.info(nodes_df)
        logging.info(edges_df)
    else:
        logging.error("Parsing was unsuccessful for text_6.")

    logging.info("Testing with text_7")
    result = parse_text_to_dataframes(text_7)
    if result is not None:
        nodes_df, edges_df = result
        logging.info(nodes_df)
        logging.info(edges_df)
    else:
        logging.error("Parsing was unsuccessful for text_7.")

    logging.info("Testing with text_8")
    result = parse_text_to_dataframes(text_8)
    if result is not None:
        nodes_df, edges_df = result
        logging.info(nodes_df)
        logging.info(edges_df)
    else:
        logging.error("Parsing was unsuccessful for text_8.")

    logging.info("Testing with text_9")
    result = parse_text_to_dataframes(text_9)
    if result is not None:
        nodes_df, edges_df = result
        logging.info(nodes_df)
        logging.info(edges_df)
    else:
        logging.error("Parsing was unsuccessful for text_9.")

    logging.info("Testing with text_10")
    result = parse_text_to_dataframes(text_10)
    if result is not None:
        nodes_df, edges_df = result
        logging.info(nodes_df)
        logging.info(edges_df)
    else:
        logging.error("Parsing was unsuccessful for text_10.")


def test_orphan():

    nodes_data = {
        "id": [0, 1, 2, 3, 4],
        "label": ["Node1", "Node2", "Node3", "OrphanNode", "Node4"],
        "type": ["TypeA", "TypeB", "TypeC", "TypeX", "TypeD"]
    }
    nodes_df = pd.DataFrame(nodes_data)

    edges_data = {
        "source": [0, 1, 4, 1],
        "target": [1, 2, 0, 4],
        "label": ["connects_to", "connects_to", "sees", "has"]
    }
    edges_df = pd.DataFrame(edges_data)

    print("=== Original Nodes ===")
    print(nodes_df)
    print("\n=== Original Edges ===")
    print(edges_df)

    cleaned_nodes_df, cleaned_edges_df = remove_orphan_nodes_and_reindex(nodes_df, edges_df)

    print("\n=== Cleaned/Reindexed Nodes ===")
    print(cleaned_nodes_df)
    print("\n=== Cleaned/Reindexed Edges ===")
    print(cleaned_edges_df)

    print("---------------------------------------------------")
    nodes_string = cleaned_nodes_df.to_csv(index=True)
    edges_string = cleaned_edges_df.to_csv(index=False)
    print(nodes_string)
    print(edges_string)
    print("---------------------------------------------------")


def test_parse_text_and_remove_orphans():
    test_input = """\
    id,entity,category
    0,dwarfs,Group
    1,Snow-white,Person
    2,King's daughter,Title
    3,coffin,Object
    4,mountain,Location
    5,owl,Animal
    6,raven,Animal
    7,dove,Animal
    8,King's son,Person
    9,dwarfs' house,Location
    10,bush,Object
    11,poisoned apple,Object
    12,father's castle,Location
    13,bride,Title
    14,step-mother,Person
    15,looking-glass,Object
    16,Queen,Title
    17,wedding,Event
    source,target,relationship
    0,1,finds
    0,3,creates
    0,4,places_on
    0,8,rides_to
    8,3,sees
    8,1,desires
    8,0,requests_from
    0,8,gives_to
    8,1,revives
    8,12,invites_to
    8,13,marries
    14,15,consults
    15,16,responds_to
    14,17,attends
    14,1,recognizes
    """

    nodes_df, edges_df = parse_text_to_dataframes(test_input)

    print(nodes_df)
    print(edges_df)


if __name__ == "__main__":
    # test_orphan()
    test_parse_text_and_remove_orphans()
