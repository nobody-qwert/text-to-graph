import time

import pandas as pd
import re
from log_utils import get_module_logger
from log_utils import log_location
from llm_api import count_tokens
import abort_manager

logger = get_module_logger("chunk_utils")


class ChunkBuilder:
    def __init__(self, document_id, target_chunk_size, max_token_size):
        self.document_id = document_id
        self.target_chunk_size = target_chunk_size
        self.max_token_size = max_token_size

        self.chunks = []

        self.current_chunk = ""
        self.current_token_count = 0
        self.start_token = 0
        self.chunk_id = 0

    def add_text(self, text, separator=" "):
        if self.current_chunk:
            self.current_chunk += separator + text
        else:
            self.current_chunk = text
        self.current_token_count += count_tokens(text)

    def finalize_chunk(self):
        end_token = self.start_token + self.current_token_count

        row_dict = {
            'chunk_index': self.chunk_id,
            'document_id': self.document_id,
            'chunk_size': self.current_token_count,
            'doc_page': 0,  # if you don’t have page info, you can default to 0
            'token_start': self.start_token,
            'token_end': end_token,
            'text': self.current_chunk.strip()
        }

        self.chunks.append(row_dict)

        logger.info(f"Created chunk {len(self.chunks)} with {self.current_token_count} tokens")

        self.start_token = end_token + 1
        self.chunk_id += 1
        self.current_chunk = ""
        self.current_token_count = 0


def create_chunks_from_document(document_id, text, target_chunk_size, progress_callback=None):
    logger.info(f"{log_location()}")

    if text is None:
        logger.warning(f"No input text! <- {log_location()}")
        return pd.DataFrame(columns=['chunk_index', 'document_id', 'chunk_size', 'doc_page',
                                     'token_start', 'token_end', 'text'])

    logger.info(f"Creating chunks with a target of {target_chunk_size} tokens")
    if progress_callback:
        progress_callback("Preparing text: 0%")

    max_token_size = int(target_chunk_size * 1.1)
    min_token_size = int(target_chunk_size * 0.5)

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    def split_sentences(x):
        return re.split(r'(?<=[.!?])\s+', x.strip())

    def split_lines(x):
        return x.strip().split("\n")

    units = []
    for paragraph in paragraphs:
        if abort_manager.ABORT_FLAG:
            break
        for sentence in split_sentences(paragraph):
            for line in split_lines(sentence):
                if line.strip():
                    units.append(line.strip())

    cb = ChunkBuilder(document_id, target_chunk_size, max_token_size)

    total_units = len(units)

    i = 0
    while i < total_units:
        if abort_manager.ABORT_FLAG:
            return None
        if progress_callback and (i % 1000) == 0:
            time.sleep(0.001)
            progress = i / total_units
            progress_message = f"Preparing text: {progress:.0%}"
            progress_callback(progress_message)

        token_count = count_tokens(units[i])
        if cb.current_token_count + token_count <= max_token_size:
            cb.add_text(units[i])
            i += 1
        else:
            if cb.current_token_count >= min_token_size:
                cb.finalize_chunk()
            else:
                cb.add_text(units[i])
                i += 1
                cb.finalize_chunk()

    if cb.current_chunk:
        cb.finalize_chunk()

    if len(cb.chunks) > 1:
        last_chunk_size = count_tokens(cb.chunks[-1]["text"])
        if last_chunk_size < min_token_size:
            t = cb.chunks[-1]["text"]
            n = last_chunk_size
            cb.chunks[-2]["text"] += " " + t
            cb.chunks[-2]["token_end"] += n
            cb.chunks[-2]["chunk_size"] = count_tokens(cb.chunks[-2]["text"])
            cb.chunks.pop()

    df = pd.DataFrame(
        cb.chunks,
        columns=[
            'chunk_index', 'document_id', 'chunk_size', 'doc_page',
            'token_start', 'token_end', 'text'
        ]
    )

    return df
