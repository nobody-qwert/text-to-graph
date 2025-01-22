import pdfplumber
import os
import abort_manager


def extract_text_from_pdf(pdf_path, progress_callback=None):
    extracted_text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            filename = os.path.basename(pdf_path)
            for page_number, page in enumerate(pdf.pages, start=1):
                if abort_manager.ABORT_FLAG:
                    break

                txt = page.extract_text()
                if txt:
                    extracted_text += txt + "\n"

                if progress_callback:
                    progress = page_number / total_pages
                    progress_message = f"Extracting {filename} - Progress: {progress:.0%}"
                    progress_callback(progress_message)
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")

    return extracted_text


def _test():
    def progress_reporter(progress):
        print(f"\rProgress: {progress:.0%}", end='', flush=True)

    pdf_file = "documents/man.pdf"
    text = extract_text_from_pdf(pdf_file, progress_reporter)


if __name__ == "__main__":
    _test()
