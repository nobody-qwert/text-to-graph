import sqlite3
import os
import threading
from log_utils import get_module_logger

logging = get_module_logger("database")

_thread_local = threading.local()

_db_initialized = {}

_database_path = None


def set_database_path(db_path):
    global _database_path
    _database_path = db_path


def get_connection():
    conn = getattr(_thread_local, 'connection', None)

    if conn is None:
        if _database_path is None:
            logging.error('Database path needs to be set first! Use "set_database_path()" !')
            return None

        try:
            os.makedirs(os.path.dirname(_database_path), exist_ok=True)

            conn = sqlite3.connect(_database_path, check_same_thread=False)
            _thread_local.connection = conn

            if _database_path not in _db_initialized:
                initialize_database(conn)
                _db_initialized[_database_path] = True
                logging.info("Database initialized successfully for this database path.")

            logging.info("Thread-local database connection established.")
        except sqlite3.Error as e:
            logging.error(f"An error occurred while establishing the database connection: {e}")
            return None
    return conn


def initialize_database(conn):
    try:
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Configurations (
                id INTEGER PRIMARY KEY,
                api TEXT NOT NULL,
                model TEXT NOT NULL,
                temperature REAL NOT NULL,
                top_p REAL NOT NULL,
                chunk_size INTEGER NOT NULL,
                padding_size INTEGER NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Documents (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                document_text TEXT NOT NULL,
                sha_256 BLOB UNIQUE NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Responses_L1 (
                id INTEGER PRIMARY KEY,
                chunk_index INTEGER NOT NULL,
                document_id INTEGER NOT NULL,
                config_id INTEGER NOT NULL,
                nodes TEXT NOT NULL,
                FOREIGN KEY (document_id) REFERENCES Documents(id),
                FOREIGN KEY (config_id) REFERENCES Configurations(id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Responses (
                id INTEGER PRIMARY KEY,
                chunk_index INTEGER NOT NULL,
                document_id INTEGER NOT NULL,
                config_id INTEGER NOT NULL,
                nodes TEXT NOT NULL,
                edges TEXT NOT NULL,
                FOREIGN KEY (document_id) REFERENCES Documents(id),
                FOREIGN KEY (config_id) REFERENCES Configurations(id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Graphs (
                id INTEGER PRIMARY KEY,
                document_id INTEGER NOT NULL,
                config_id INTEGER NOT NULL,
                nodes TEXT NOT NULL,
                edges TEXT NOT NULL,
                metadata TEXT NOT NULL,
                FOREIGN KEY (document_id) REFERENCES Documents(id),
                FOREIGN KEY (config_id) REFERENCES Configurations(id)
            )
        ''')

        conn.commit()

    except sqlite3.Error as e:
        logging.error(f"An error occurred while initializing the database: {e}")


def get_or_create_config_id(api, model, temperature, top_p, chunk_size, padding_size):
    conn = get_connection()
    if conn is None:
        logging.error("Database connection is not available.")
        return None

    try:
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id 
            FROM Configurations
            WHERE api = ?
              AND model = ?
              AND temperature = ?
              AND top_p = ?
              AND chunk_size = ?
              AND padding_size = ?
        ''', (api, model, temperature, top_p, chunk_size, padding_size))
        result = cursor.fetchone()

        if result:
            return result[0]

        cursor.execute('''
            INSERT INTO Configurations 
            (api, model, temperature, top_p, chunk_size, padding_size)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (api, model, temperature, top_p, chunk_size, padding_size))
        conn.commit()
        config_id = cursor.lastrowid
        logging.info(f"Inserted new configuration with ID: {config_id}")
        return config_id

    except sqlite3.Error as e:
        logging.error(f"An error occurred while inserting or retrieving configuration: {e}")
        return None


def get_document_id(sha_256_hash):
    conn = get_connection()
    if conn is None:
        logging.error("Database connection is not available.")
        return None

    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name, sha_256 
            FROM Documents 
            WHERE sha_256 = ?
        ''', (sha_256_hash,))
        result = cursor.fetchone()
        if result:
            doc_id, doc_name, doc_hash = result
            logging.info(f"Document found: ID={doc_id}, Name={doc_name}, SHA-256={doc_hash}")
            return doc_id
        else:
            logging.info(f"Document existence check for SHA-256 {sha_256_hash}: Not found")
            return None
    except sqlite3.Error as e:
        logging.error(f"An error occurred while checking document existence: {e}")
        return None


def get_document_text(doc_id):
    conn = get_connection()
    if conn is None:
        logging.error("Database connection is not available.")
        return None

    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name, sha_256, document_text 
            FROM Documents 
            WHERE id = ?
        ''', (doc_id,))
        result = cursor.fetchone()
        if result:
            doc_id, doc_name, doc_hash, doc_text = result
            logging.info(
                f"Document details retrieved: ID={doc_id}, Name={doc_name}, SHA-256={doc_hash}, Text Length={len(doc_text)}")
            return doc_text
        else:
            logging.info(f"Document with ID={doc_id} not found.")
            return None
    except sqlite3.Error as e:
        logging.error(f"An error occurred while retrieving document text: {e}")
        return None


def insert_document(sha_256_hash, text, name):
    conn = get_connection()
    if conn is None:
        logging.error("Database connection is not available.")
        return None

    try:
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id 
            FROM Documents 
            WHERE sha_256 = ?
        ''', (sha_256_hash,))
        result = cursor.fetchone()

        if result:
            logging.info(f"Document with the same SHA-256 hash already exists with ID: {result[0]}")
            return result[0]

        cursor.execute('''
            INSERT INTO Documents (sha_256, document_text, name) 
            VALUES (?, ?, ?)
        ''', (sha_256_hash, text, name))
        conn.commit()
        doc_id = cursor.lastrowid
        logging.info(f"Inserted document {name} with SHA-256 hash. ID: {doc_id}")
        return doc_id

    except sqlite3.Error as e:
        logging.error(f"An error occurred while inserting document {name}: {e}")
        return None


def print_database_summary():
    conn = get_connection()
    if conn is None:
        logging.error("Database connection is not available.")
        return

    try:
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()

        if not tables:
            logging.info("No tables found in the database.")
            return

        logging.info("Database Summary:")
        for (table_name,) in tables:
            logging.info(f"\nTable: {table_name}")
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()

            for col in columns:
                col_id, col_name, col_type, col_notnull, col_default, col_pk = col
                logging.info(
                    f"  Column: {col_name} | Type: {col_type} | "
                    f"NotNull: {'Yes' if col_notnull else 'No'} | "
                    f"Primary Key: {'Yes' if col_pk else 'No'}"
                )

    except sqlite3.Error as e:
        logging.error(f"An error occurred while printing the database summary: {e}")


def response_exists_L1(document_id, chunk_index, config_id):
    conn = get_connection()
    if conn is None:
        logging.error("Database connection is not available.")
        return False

    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 1 
            FROM Responses_L1 
            WHERE document_id = ? 
              AND chunk_index = ?
              AND config_id = ?
        ''', (document_id, chunk_index, config_id))
        result = cursor.fetchone()

        if result:
            logging.info(f"L1 - Response exists for document ID={document_id}, chunk_index={chunk_index}, config_id={config_id}.")
            return True
        else:
            logging.info(f"L1 - No response found for document ID={document_id}, chunk_index={chunk_index}, config_id={config_id}.")
            return False

    except sqlite3.Error as e:
        logging.error(f"An error occurred while checking L1 response existence: {e}")
        return False


def response_exists(document_id, chunk_index, config_id):
    conn = get_connection()
    if conn is None:
        logging.error("Database connection is not available.")
        return False

    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 1 
            FROM Responses
            WHERE document_id = ?
              AND chunk_index = ?
              AND config_id = ?
        ''', (document_id, chunk_index, config_id))
        result = cursor.fetchone()

        if result:
            logging.info(f"L2 - Response exists for document ID={document_id}, chunk_index={chunk_index}, config_id={config_id}.")
            return True
        else:
            logging.info(f"L2 - No response found for document ID={document_id}, chunk_index={chunk_index}, config_id={config_id}.")
            return False

    except sqlite3.Error as e:
        logging.error(f"An error occurred while checking L2 response existence: {e}")
        return False


def insert_response_L1(document_id, chunk_index, config_id, nodes):
    conn = get_connection()
    if conn is None:
        logging.error("Database connection is not available.")
        return None

    try:
        cursor = conn.cursor()

        # Check if there's an existing row
        cursor.execute('''
            SELECT id 
            FROM Responses_L1 
            WHERE document_id = ? 
              AND chunk_index = ?
              AND config_id = ?
        ''', (document_id, chunk_index, config_id))
        existing_response = cursor.fetchone()

        if existing_response:
            response_id = existing_response[0]
            cursor.execute('''
                UPDATE Responses_L1
                SET nodes = ?
                WHERE document_id = ?
                  AND chunk_index = ?
                  AND config_id = ?
            ''', (nodes, document_id, chunk_index, config_id))
            conn.commit()
            logging.info(f"L1 - Updated response with ID {response_id} for doc={document_id}, chunk_index={chunk_index}, config_id={config_id}.")
            logging.info(f"L1 - {nodes}")
            return response_id
        else:
            cursor.execute('''
                INSERT INTO Responses_L1 (document_id, chunk_index, config_id, nodes)
                VALUES (?, ?, ?, ?)
            ''', (document_id, chunk_index, config_id, nodes))
            conn.commit()
            response_id = cursor.lastrowid
            logging.info(f"L1 - Inserted response with ID {response_id} for doc={document_id}, chunk_index={chunk_index}, config_id={config_id}.")
            logging.info(f"L1 - {nodes}")
            return response_id

    except sqlite3.Error as e:
        logging.error(f"L1 - Error while inserting/updating response for doc={document_id}, chunk_index={chunk_index}, config_id={config_id}: {e}")
        return None


def insert_response(document_id, chunk_index, config_id, nodes, edges):
    conn = get_connection()
    if conn is None:
        logging.error("Database connection is not available.")
        return None

    try:
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id 
            FROM Responses
            WHERE document_id = ?
              AND chunk_index = ?
              AND config_id = ?
        ''', (document_id, chunk_index, config_id))
        existing_response = cursor.fetchone()

        if existing_response:
            response_id = existing_response[0]
            cursor.execute('''
                UPDATE Responses
                SET nodes = ?, edges = ?
                WHERE document_id = ?
                  AND chunk_index = ?
                  AND config_id = ?
            ''', (nodes, edges, document_id, chunk_index, config_id))
            conn.commit()
            logging.info(f"L2 - Updated response with ID {response_id} for doc={document_id}, chunk_index={chunk_index}, config_id={config_id}.")
            return response_id
        else:
            cursor.execute('''
                INSERT INTO Responses (document_id, chunk_index, config_id, nodes, edges)
                VALUES (?, ?, ?, ?, ?)
            ''', (document_id, chunk_index, config_id, nodes, edges))
            conn.commit()
            response_id = cursor.lastrowid
            logging.info(f"L2 - Inserted response with ID {response_id} for doc={document_id}, chunk_index={chunk_index}, config_id={config_id}.")
            return response_id

    except sqlite3.Error as e:
        logging.error(f"L2 - Error while inserting/updating response for doc={document_id}, chunk_index={chunk_index}, config_id={config_id}: {e}")
        return None


def get_all_L1_responses_for(document_id, config_id):
    conn = get_connection()
    if conn is None:
        logging.error("Database connection is not available.")
        return []

    try:
        cursor = conn.cursor()

        query = '''
        SELECT R.*
        FROM Responses_L1 R
        WHERE R.document_id = ?
          AND R.config_id = ?
        '''
        cursor.execute(query, (document_id, config_id))
        rows = cursor.fetchall()

        if not rows:
            logging.info(f"L1 - No responses found for document_id={document_id} with config_id={config_id}.")
            return []

        column_names = [description[0] for description in cursor.description]
        responses = [dict(zip(column_names, row)) for row in rows]

        logging.info(f"L1 - Retrieved {len(responses)} responses for document_id={document_id}, config_id={config_id}.")
        return responses

    except sqlite3.Error as e:
        logging.error(f"An error occurred while retrieving L1 responses for document_id={document_id}, config_id={config_id}: {e}")
        return []


def get_all_responses_for(document_id, config_id):
    conn = get_connection()
    if conn is None:
        logging.error("Database connection is not available.")
        return []

    try:
        cursor = conn.cursor()

        query = '''
        SELECT R.*
        FROM Responses R
        WHERE R.document_id = ?
          AND R.config_id = ?
        '''
        cursor.execute(query, (document_id, config_id))
        rows = cursor.fetchall()

        if not rows:
            logging.info(f"No responses found for document_id={document_id} with config_id={config_id}.")
            return []

        column_names = [description[0] for description in cursor.description]
        responses = [dict(zip(column_names, row)) for row in rows]

        logging.info(f"Retrieved {len(responses)} responses for document_id={document_id}, config_id={config_id}.")
        return responses

    except sqlite3.Error as e:
        logging.error(f"An error occurred while retrieving L2 responses for document_id={document_id}: {e}")
        return []


def insert_graph(document_id, config_id, nodes, edges, metadata):
    logging.info(f"Insert graph. Document ID {document_id} config_id {config_id}")
    conn = get_connection()
    if conn is None:
        logging.error("Database connection is not available.")
        return None

    try:
        cursor = conn.cursor()

        cursor.execute('SELECT id FROM Documents WHERE id = ?', (document_id,))
        if not cursor.fetchone():
            logging.error(f"Document ID {document_id} does not exist.")
            return None

        cursor.execute('''
            SELECT id 
            FROM Graphs
            WHERE document_id = ?
              AND config_id = ?
        ''', (document_id, config_id))
        result = cursor.fetchone()

        if result:
            existing_id = result[0]
            cursor.execute('DELETE FROM Graphs WHERE id = ?', (existing_id,))
            logging.info(f"Deleted existing graph with ID {existing_id} for document ID {document_id}.")

        cursor.execute('''
            INSERT INTO Graphs (document_id, config_id, nodes, edges, metadata)
            VALUES (?, ?, ?, ?, ?)
        ''', (document_id, config_id, nodes, edges, metadata))
        conn.commit()
        graph_id = cursor.lastrowid
        logging.info(f"Inserted new graph with ID {graph_id} for document ID {document_id}.")
        return graph_id

    except sqlite3.Error as e:
        logging.error(f"An error occurred while inserting graph for document ID {document_id}: {e}")
        return None


def main():
    print_database_summary()

    config_id = get_or_create_config_id(
        api='openai',
        model='gpt-5-mini',
        temperature=0,
        top_p=0.3,
        chunk_size=1000,
        padding_size=1
    )

    if config_id is not None:
        logging.info(f"Using configuration with ID: {config_id}")

    doc_sha = b"\x12\x34\x56\x78"
    doc_text = "This is some example content."
    doc_name = "example_file.txt"

    document_id = insert_document(doc_sha, doc_text, doc_name)
    if document_id is not None:
        logging.info(f"Document inserted with ID: {document_id}")


if __name__ == "__main__":
    main()
