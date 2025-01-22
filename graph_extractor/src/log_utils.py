import logging
import os
import shutil
import traceback


LOGGING_ON = True
LOG_LEVEL = logging.DEBUG if LOGGING_ON else logging.ERROR

LOG_DIR = 'logs'
if LOGGING_ON:
    try:
        if os.path.exists(LOG_DIR):
            shutil.rmtree(LOG_DIR)
    except Exception as e:
        print(f"Warning: Could not delete {LOG_DIR}. Error: {e}")
    finally:
        os.makedirs(LOG_DIR, exist_ok=True)


def get_module_logger(module_name):
    logger = logging.getLogger(module_name)
    logger.propagate = False

    if not logger.handlers and LOGGING_ON:
        file_handler = logging.FileHandler(f"{LOG_DIR}/{module_name}.log", encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logger.setLevel(LOG_LEVEL)
    return logger


def log_location():
    """Get the location of the log call."""
    stack = traceback.extract_stack()
    if len(stack) > 1:
        caller = stack[-2]
        module_name = caller.name
        return f"{module_name}()"
    else:
        return ""
