import os
import sys
import subprocess
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


def main():
    src_script = r"../src/gui.py"

    if not os.path.exists(src_script):
        logging.error(f"Source script not found at {src_script}")
        sys.exit(1)

    icon_path = os.path.abspath("graph.ico")
    print(f"Icon path: {icon_path}")

    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name", "GraphGenerator",
        "--paths", r"../graph_extractor/src",
        "--hidden-import", "tiktoken_ext.openai_public",
        f"--icon={icon_path}",
        src_script
    ]

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
