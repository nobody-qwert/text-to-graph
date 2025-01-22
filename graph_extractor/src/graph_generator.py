import json
import os
import asyncio
import abort_manager
import my_hash
import doc_utils
import chunk_utils
import graph_utils
import prompts
import response_parser
import sqlite_support
import llm_api

from create_graph_viewer import build_viewer
from log_utils import get_module_logger


logger = get_module_logger("graph_generator")


def _ensure_directories_exist(config):
    directories = [config['output_folder'], config['internal_data_dir']]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"Created directory: {directory}")


def _build_chunk_node_map(responses):
    chunk_node_map = {}
    for response in responses:
        chunk_index = response.get("chunk_index")
        nodes_str = response.get("nodes")

        if not nodes_str:
            logger.warning(f"No nodes CSV found for chunk index {chunk_index}.")
            continue

        nodes = response_parser.parse_nodes(nodes_str)

        if chunk_index in chunk_node_map:
            chunk_node_map[chunk_index].extend(nodes)
        else:
            chunk_node_map[chunk_index] = nodes

    logger.info(f"Created [chunk index , node list] map with {len(chunk_node_map)} chunks.")
    return chunk_node_map


async def _process_chunk(document_id, config_id, chunk_index, prompt, config):
    try:
        response = await asyncio.wait_for(llm_api.execute(prompt, config), config['llm_timeout']+2)
    except asyncio.TimeoutError:
        abort_manager.ABORT_FLAG = True
        raise Exception("API call timed out!")

    result = response_parser.parse_text_to_dataframes(response)
    if result is None:
        logger.warning(f"Could not parse response for chunk {chunk_index}!\n{response}")
        return

    nodes, edges = result
    if nodes is None or edges is None:
        logger.warning(f"Parsing returned None objects for chunk {chunk_index}!\n{response}")
        return
    elif nodes.empty:
        logger.warning(f"Parsing returned empty nodes for chunk {chunk_index}!\n{response}")
    elif edges.empty:
        logger.warning(f"Parsing returned empty edges for chunk {chunk_index}!\n{response}")

    logger.info(f"Response for chunk {chunk_index}!\n{response}")
    nodes_string = nodes.to_csv(index=True)
    edges_string = edges.to_csv(index=False)
    response_id = sqlite_support.insert_response(document_id, chunk_index, config_id, nodes_string, edges_string)
    logger.info(f"Response for chunk {chunk_index} saved to {response_id}")


async def _process_L1_chunk(document_id, config_id, chunk, prompt, config):
    try:
        response = await asyncio.wait_for(llm_api.execute(prompt, config), config['llm_timeout']+2)
    except asyncio.TimeoutError:
        abort_manager.ABORT_FLAG = True
        raise Exception("API call timed out!")

    nodes = response_parser.parse_nodes(response)
    if nodes is None:
        logger.warning(f"Could not parse response for chunk index {chunk.chunk_index}!\n{response}")
        return

    nodes_string = ', '.join(f'"{node}"' for node in nodes)

    if not nodes_string.strip():
        logger.warning(f"nodes_string is empty for chunk index {chunk.chunk_index}. Skipping database insertion.")
        return

    response_id = sqlite_support.insert_response_L1(document_id, chunk.chunk_index, config_id, nodes_string)
    logger.info(f"Response ({len(nodes)} nodes) for chunk ID {chunk.chunk_index}: {response}")
    logger.info(f"Saved to Response ID: {response_id}")


async def _run_async_tasks_in_batches(
    to_process,
    processor_fn,
    max_concurrent_requests,
    progress_label,
    progress_callback=None
):
    if not to_process:
        logger.info(f"No tasks to process for {progress_label}.")
        if progress_callback:
            progress_callback(f"{progress_label}  {1:.0%}")
        return

    total_jobs = len(to_process)
    completed_tasks = 0

    async def track_progress(task):
        nonlocal completed_tasks
        try:
            result = await task
        except Exception as e:
            logger.error(f"Error while processing task: {e}")
            if progress_callback:
                progress_callback(f"{e}", 'error')
                abort_manager.ABORT_FLAG = True
            result = None
        completed_tasks += 1
        if progress_callback and not abort_manager.ABORT_FLAG:
            progress = completed_tasks / total_jobs
            progress_callback(f"{progress_label}  {progress:.0%}")
        return result

    if progress_callback:
        progress_callback(f"{progress_label}  {0:.0%}")

    for start_idx in range(0, total_jobs, max_concurrent_requests):
        if abort_manager.ABORT_FLAG:
            logger.info(f"Abort triggered, not scheduling next batch for {progress_label}.")
            break

        batch_data = to_process[start_idx : start_idx + max_concurrent_requests]

        batch_tasks = [
            asyncio.create_task(processor_fn(*args))
            for args in batch_data
        ]

        try:
            await asyncio.gather(*(track_progress(t) for t in batch_tasks))
        except Exception as e:
            logger.error(f"Exception in {progress_label} batch gather: {e}")
            if abort_manager.ABORT_FLAG:
                logger.info(f"Canceling running tasks in current batch for {progress_label}...")
                for t in batch_tasks:
                    t.cancel()
                await asyncio.gather(*batch_tasks, return_exceptions=True)
            break


async def _L2_extract_graph_big_context(document_id, config_id, df_chunks, config, progress_callback=None):
    if abort_manager.ABORT_FLAG:
        return

    logger.info(f"L2 Extracting graph from chunks")

    responses = sqlite_support.get_all_L1_responses_for(document_id, config_id)

    nr = len(responses)
    nc = len(df_chunks)

    if nr == 0:
        logger.warning(
            f"Document Id: {document_id} ChunkSize: {config['chunk_size']} has no response available! Run L1!")
        return

    if nr != nc:
        logger.warning(f"Document Id: {document_id} ChunkSize: {config['chunk_size']} has {nc} chunks but {nr} responses!")

    chunk_node_map = _build_chunk_node_map(responses)

    to_process = []
    for i, chunk in df_chunks.iterrows():
        if config["optimization_on"] and sqlite_support.response_exists(document_id, i, config_id):
            logger.info(f"L2 Response available for chunk Chunk index: {i}")
            continue

        if i not in chunk_node_map:
            logger.warning(f"Chunk {i} not found in L1 responses!")
            continue

        nodes = chunk_node_map[i] or []
        node_labels_str = ", ".join(nodes)

        big_text = ""
        if i > 0:
            big_text += df_chunks.loc[i - 1, 'text']
        big_text += df_chunks.loc[i, 'text']
        if i < nc - 1:
            big_text += df_chunks.loc[i + 1, 'text']

        logger.info(f"L2 Extracting entities and relationships from chunk {i}")
        prompt = prompts.extract_entities_and_relationships_prompt_level2(big_text, node_labels_str)

        to_process.append((document_id, config_id, i, prompt, config))

    await _run_async_tasks_in_batches(
        to_process,
        _process_chunk,
        config['max_concurrent_requests'],
        progress_label="Mapping relationships",
        progress_callback=progress_callback
    )


async def _L1_extract_entities_from_chunks(document_id, config_id, df_chunks, config, progress_callback=None):
    logger.info(f"L1 Extracting entities from chunks")

    if df_chunks.empty:
        logger.warning("Chunks are empty!")
        return

    original_padding_size = config['padding_size']
    config['padding_size'] = 0

    to_process = []
    for i, chunk in df_chunks.iterrows():
        if config["optimization_on"] and sqlite_support.response_exists_L1(document_id, i, config_id):
            logger.info(f"L1 Response available for chunk Chunk index: {i}")
            continue

        logger.info(f"L1 Extracting entities from chunk {i}")
        prompt = prompts.extract_entities_prompt(chunk.text)
        to_process.append((document_id, config_id, chunk, prompt, config))

    await _run_async_tasks_in_batches(
        to_process,
        _process_L1_chunk,
        config['max_concurrent_requests'],
        progress_label="Finding entities",
        progress_callback=progress_callback
    )

    config['padding_size'] = original_padding_size
    print()


async def _L0_extract_graph(document_id, config_id, df_chunks, config, progress_callback=None):
    logger.info(f"L0 Extracting graph from chunks")

    nc = len(df_chunks)
    chunk_size = config['chunk_size']
    overlap_coefficient = config['overlap'] / chunk_size

    if nc == 0:
        logger.error(f"Document Id: {document_id} ChunkSize: {chunk_size} has {nc} chunks!")
        return None

    to_process = []
    for i, chunk in df_chunks.iterrows():
        if config["optimization_on"] and sqlite_support.response_exists(document_id, i, config_id):
            logger.info(f"Response available for chunk Chunk index: {i}")
            continue

        big_text = ""
        if i > 0:
            str_o = df_chunks.loc[i - 1, 'text']
            n = int(len(str_o) * overlap_coefficient)
            big_text += str_o[-n:]

        big_text += df_chunks.loc[i, 'text']

        if i < nc - 1:
            str_o = df_chunks.loc[i + 1, 'text']
            n = int(len(str_o) * overlap_coefficient)
            big_text += str_o[:n]

        logger.info(f"L0 Extracting entities and relationships from chunk {i}")
        prompt = prompts.extract_entities_and_relationships_prompt_level0(big_text)

        to_process.append((document_id, config_id, chunk.chunk_index, prompt, config))

    await _run_async_tasks_in_batches(
        to_process,
        _process_chunk,
        config['max_concurrent_requests'],
        progress_label="Building graph",
        progress_callback=progress_callback
    )


def save_html_file(file_path, html_content):
    if html_content is None:
        logger.warning(f"HTML content is None!")
        return

    try:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(html_content)
    except (OSError, IOError) as e:
        logger.error(f"Error writing to file {file_path}: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred while writing to {file_path}: {e}")


async def generate_graph_async(pdf_files, config, progress_callback=None):
    _ensure_directories_exist(config)

    # -----------------------------------------------------------------------------------

    db_full_path = os.path.join(config['internal_data_dir'], config['db_filename'])
    sqlite_support.set_database_path(db_full_path)

    # -----------------------------------------------------------------------------------

    config_id = sqlite_support.get_or_create_config_id(
        config['api'],
        config['model'],
        config['temperature'],
        config['top_p'],
        config['chunk_size'],
        config['padding_size']
    )

    # -----------------------------------------------------------------------------------
    generate_composite_graph = config["merge_document_graphs"]
    all_graphs = []
    metadata_list = []
    metadata = {}

    for i, document_path in enumerate(pdf_files, start=1):
        if abort_manager.ABORT_FLAG:
            return

        # -----------------------------------------------------------------------------------

        pdf_filename = os.path.basename(document_path)
        progress_callback(f"\n[{i}/{len(pdf_files)}] Processing: {pdf_filename}", "log")

        # -----------------------------DOCUMENT----------------------------------------------

        hash_code, error_message = my_hash.calculate_file_sha256(document_path)
        if error_message:
            logger.info(f"Warning: {error_message}")
            continue
        else:
            logger.info(f"{document_path}  hash: {hash_code}")

        document_file_name = os.path.basename(document_path)
        document_base_name = os.path.splitext(document_file_name)[0]

        document_id = sqlite_support.get_document_id(hash_code)
        if document_id is None:
            logger.info(f"Extracting text from \"{document_path}\"")
            text = doc_utils.extract_text_from_document(document_path, config, progress_callback)
            document_id = sqlite_support.insert_document(hash_code, text, document_base_name)
        else:
            logger.info(f"Document text exists in cache \"{document_path}\"")
            text = sqlite_support.get_document_text(document_id)

        # ------------------------------------BUILD CHUNKS------------------------------------

        logger.info(f"Create Chunks for: \"{document_base_name}\"")
        chunks_df = await asyncio.to_thread(
            chunk_utils.create_chunks_from_document,
            document_id,
            text,
            config['chunk_size'],
            progress_callback
        )

        # ------------------------------------------------------------------------------------
        logger.info("Building graph ...")
        # ------------------------------------------------------------------------------------

        if abort_manager.ABORT_FLAG:
            return

        if config['padding_size'] > 0:
            await _L1_extract_entities_from_chunks(document_id, config_id, chunks_df, config, progress_callback)
            await _L2_extract_graph_big_context(document_id, config_id, chunks_df, config, progress_callback)
        else:
            await _L0_extract_graph(document_id, config_id, chunks_df, config, progress_callback)

        if abort_manager.ABORT_FLAG:
            return

        # ------------------------------------------------------------------------------------
        #                                     MERGE PARTS                                    -
        # ------------------------------------------------------------------------------------

        metadata = {
            "index": 0,
            "filename": pdf_filename,
            "sha256": hash_code
        }

        nodes, edges = graph_utils.merge_graphs(document_id, config_id, metadata)

        # -------------------------------------------------------------------------------------
        #                                   Generate HTML                                     -
        # -------------------------------------------------------------------------------------

        if generate_composite_graph:
            all_graphs.append((pdf_filename, nodes, edges))
            metadata["index"] = i - 1
            metadata_list.append(metadata)
        else:
            nodes_string = nodes.to_csv(index=False)
            edges_string = edges.to_csv(index=False)
            metadata_str = json.dumps([metadata])
            print(metadata_str)

            viewer_html = build_viewer(nodes_string, edges_string, metadata_str)

            file_path = os.path.join(config['output_folder'], document_base_name) + '.html'
            save_html_file(file_path, viewer_html)

            logger.info(f"Graph saved to: {file_path}")

    # -------------------------------------------------------------------------------------
    #                                   Composite HTML                                    -
    # -------------------------------------------------------------------------------------

    if generate_composite_graph:
        metadata_str = json.dumps(metadata_list)
        print(metadata_str)
        nodes, edges = graph_utils.merge_all_document_graphs(all_graphs)

        nodes_string = nodes.to_csv(index=False)
        edges_string = edges.to_csv(index=False)

        logger.info(f"BUILDING HTML!")

        viewer_html = build_viewer(nodes_string, edges_string, metadata_str)

        from datetime import datetime
        timestamp_string = datetime.now().strftime('%Y%m%d_%H%M%S')

        file_path = os.path.join(config['output_folder'], f"combined_graph_{timestamp_string}") + '.html'
        save_html_file(file_path, viewer_html)

        logger.info(f"Graph saved to: {file_path}")

        # -------------------------------------------------------------------------------------
        #      TEMP STUFF   ---------------------- DELETE This in prod
        # -------------------------------------------------------------------------------------

        dummy_hash = timestamp_string
        composite_filename = f"combined_graph_{timestamp_string}.pdf"
        document_id = sqlite_support.insert_document(dummy_hash, timestamp_string, composite_filename)

        graph_id = sqlite_support.insert_graph(
            document_id,
            config_id,
            nodes_string,
            edges_string,
            metadata
        )

        logger.info(f"Merged Graph ID {graph_id}, {len(nodes)} Nodes, {len(edges)} Edges")
