import os
import sys
import shutil
import subprocess
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


def run_command(cmd, check=True, shell=True):
    logging.info("Running command: " + " ".join(cmd))
    result = subprocess.run(cmd, stdout=sys.stdout, stderr=sys.stderr, shell=shell)
    if check and result.returncode != 0:
        logging.error(f"Command failed with return code {result.returncode}")
        sys.exit(result.returncode)
    return result


def main():
    src_dir = os.path.abspath("../src")
    main_script = os.path.join(src_dir, "gui.py")
    obfuscated_dir = os.path.abspath("../src/obfuscated")
    icon_path = os.path.abspath("graph.ico")

    if not os.path.exists(main_script):
        logging.error(f"Source script not found at {main_script}")
        sys.exit(1)

    # Ensure a fresh obfuscation directory
    if os.path.exists(obfuscated_dir):
        logging.info(f"Removing old obfuscated directory: {obfuscated_dir}")
        shutil.rmtree(obfuscated_dir)
    os.makedirs(obfuscated_dir)

    # Obfuscate only files directly in the src directory
    for filename in os.listdir(src_dir):
        file_path = os.path.join(src_dir, filename)
        if os.path.isfile(file_path) and filename.endswith(".py"):
            run_command(["pyarmor", "gen", "-O", obfuscated_dir, file_path])

    obfuscated_main_script = os.path.join(obfuscated_dir, "gui.py")
    if not os.path.exists(obfuscated_main_script):
        logging.error("Obfuscated cli.py not found. Obfuscation may have failed.")
        sys.exit(1)

    hidden_imports = [
        "asyncio",
        "tiktoken_ext.openai_public",
        "ttkbootstrap",
        "tkinter",
        "tkinter.filedialog",
        "tkinter.messagebox",
        "openai",
        "pdfplumber",
        "my_hash",
        # --------------------------------------------------
        "doc_utils",
        "abort_manager",
        "config",
        "chunk_utils",
        "graph_utils",
        "graph_view_template",
        "gui.py",
        "gui_config_window",
        "gui_initial_window",
        "gui_main_window",
        "gui_status_window",
        "gui_style_definitions",
        "gui_tooltip",
        "gui_utils",
        "dummy_pdf",
        "create_graph_viewer",
        "edge_utils",
        "gpt",
        "graph_generator",
        "llm_api",
        "log_utils",
        "pdf_extractor",
        "pdf_extractor_open",
        "prompts",
        "response_parser",
        "sqlite_support"
    ]

    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name", "GraphGenerator",
        "--paths", obfuscated_dir,
        f"--icon={icon_path}",
    ]

    # Add each hidden import
    for hidden_import in hidden_imports:
        cmd += ["--hidden-import", hidden_import]

    # Finally, add the obfuscated entry point script
    cmd.append(obfuscated_main_script)

    logging.info("Running PyInstaller with the following command:")
    logging.info(" ".join(cmd))

    try:
        result = subprocess.run(cmd, stdout=sys.stdout, stderr=sys.stderr, shell=True)
    except FileNotFoundError:
        logging.error("PyInstaller not found. Make sure it's installed and on your PATH.")
        sys.exit(1)

    if result.returncode != 0:
        logging.error("PyInstaller failed. Check the output above for details.")
        sys.exit(result.returncode)
    else:
        logging.info("Executable generated successfully.")


if __name__ == "__main__":
    main()
