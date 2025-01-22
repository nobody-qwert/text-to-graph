import os
import platform
import time
import subprocess
from pathlib import Path
from pdf_extractor import extract_text_from_pdf
from log_utils import get_module_logger


logger = get_module_logger("doc_utils")


def extract_text_with_external_tool(pdf_path, config, progress_callback=None):
    logger.info(f"Extracting text from {pdf_path}")
    doc_parser_tool_path = config.get('doc_parser_tool')
    os.makedirs(config['internal_data_dir'], exist_ok=True)

    output_txt_filepath = os.path.join(config['internal_data_dir'], config['temp_txt_file'])

    filename = os.path.basename(pdf_path)
    if progress_callback:
        progress_callback(f"Extracting {filename}...")

    try:

        popen_kwargs = {}
        if platform.system() == 'Windows':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            popen_kwargs["startupinfo"] = startupinfo

        process = subprocess.Popen(
            [doc_parser_tool_path, pdf_path, output_txt_filepath],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, **popen_kwargs
        )

        for line in iter(process.stdout.readline, ''):
            print(line.strip())

        process.wait()

        if process.returncode != 0:
            stderr_output = process.stderr.read().strip()
            logger.error(f"Extracting with tool \"{doc_parser_tool_path}\" failed with error:\n{stderr_output}")
        else:
            if Path(output_txt_filepath).exists():
                try:
                    with open(output_txt_filepath, 'r', encoding='utf-8') as file:
                        return file.read()
                except UnicodeDecodeError:
                    logger.error("Extracted txt file is not UTF-8 encoded!")
                except Exception as e:
                    logger.error(f"{str(e)}")
            else:
                logger.error(f"{output_txt_filepath} was not generated!")

    except Exception as e:
        logger.error(f"Unexpected error: {e}")

    return None


def extract_text_from_document(pdf_path, config, progress_callback=None):
    if config['doc_parser_tool'] is None:
        return extract_text_from_pdf(pdf_path, progress_callback)
    else:
        return extract_text_with_external_tool(pdf_path, config, progress_callback)


def test1():
    directory = "documents"
    extracted_txt_dir = os.path.join(directory, "extracted_txt")
    os.makedirs(extracted_txt_dir, exist_ok=True)

    pdf_files = [f for f in os.listdir(directory) if f.lower().endswith('.pdf')]

    if not pdf_files:
        print("No PDF files found in the directory.")
        return

    total_start_time = time.perf_counter()

    for pdf_file in pdf_files:
        pdf_path = os.path.join(directory, pdf_file)
        start_time = time.perf_counter()
        try:
            txt = extract_text_from_document(pdf_path)
            txt_filename = os.path.splitext(pdf_file)[0] + ".txt"
            txt_path = os.path.join(extracted_txt_dir, txt_filename)

            with open(txt_path, "w", encoding="utf-8") as txt_file:
                txt_file.write(txt)

            elapsed_time = time.perf_counter() - start_time
            print(f"Processed '{pdf_file}': Extracted text length: {len(txt)}, Time taken: {elapsed_time:.2f} seconds")
        except Exception as e:
            elapsed_time = time.perf_counter() - start_time
            print(f"Failed to process '{pdf_file}' after {elapsed_time:.2f} seconds: {e}")

    total_elapsed_time = time.perf_counter() - total_start_time
    print(f"Total processing time: {total_elapsed_time:.2f} seconds")


def test2():
    print()


def main():
    test2()


if __name__ == "__main__":
    main()
