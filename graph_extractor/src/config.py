import json
import os
import subprocess
import platform
from log_utils import get_module_logger
from dummy_pdf import MINIMAL_PDF_CONTENT

logger = get_module_logger("config")

default_config = {
    'api_key': '',
    'api': 'openai',
    'doc_parser_tool': '',
    'model': 'gpt-5-mini',
    'llm_timeout': 60,
    'max_concurrent_requests': 50,
    'config_file': 'config.json'
}

CONFIG_TEMPLATE = {
    "api_key": {
        "required": True,
        "type": str,
        "allowed_values": None,
        "range": None,
        "allow_empty": False,
    },
    "api": {
        "required": True,
        "type": str,
        "allowed_values": ["openai"],
        "range": None,
        "allow_empty": False,
    },
    "doc_parser_tool": {
        "required": True,
        "type": str,
        "allowed_values": None,
        "range": None,
        "allow_empty": True,
    },
    "model": {
        "required": True,
        "type": str,
        "allowed_values": ["gpt-5-mini", "gpt-4o", "gpt-4o-2024-11-20"],
        "range": None,
        "allow_empty": False,
    },
    "llm_timeout": {
        "required": True,
        "type": int,
        "allowed_values": None,
        "range": (20, 120),
        "allow_empty": False,
    },
    "max_concurrent_requests": {
        "required": True,
        "type": int,
        "allowed_values": None,
        "range": (1, 100),
        "allow_empty": False,
    },
}


def validate_config(config, ignore_config_filename_field=False):
    errors = []

    missing_fields = [
        field_name for (field_name, spec) in CONFIG_TEMPLATE.items()
        if spec["required"] and field_name not in config
    ]
    if missing_fields:
        errors.append("Missing required fields in config: " + ", ".join(missing_fields))
        return errors

    config_keys = set(config.keys())
    if ignore_config_filename_field and "config_file" in config_keys:
        config_keys.remove("config_file")

    extra_fields = config_keys - set(CONFIG_TEMPLATE.keys())
    if extra_fields:
        errors.append("Unrecognized fields in config: " + ", ".join(sorted(extra_fields)))
        return errors

    for field_name, field_spec in CONFIG_TEMPLATE.items():
        value = config[field_name]
        if not isinstance(value, field_spec["type"]):
            errors.append(
                f"Invalid type for '{field_name}'. "
                f"Expected {field_spec['type'].__name__}, got {type(value).__name__}."
            )
            continue

        if not field_spec["allow_empty"] and isinstance(value, str) and len(value) == 0:
            errors.append(f"Empty '{field_name}' value in config.")
            continue

        if field_spec["allowed_values"] is not None:
            if value not in field_spec["allowed_values"]:
                allowed_list = ", ".join(map(str, field_spec["allowed_values"]))
                errors.append(f"Invalid '{field_name}' value: '{value}'\nMust be one of: {allowed_list}")
                continue

        if field_spec["range"] is not None and isinstance(value, (int, float)):
            min_val, max_val = field_spec["range"]
            if not (min_val <= value <= max_val):
                errors.append(f"Invalid '{field_name}' value: {value}\nMust be between {min_val} and {max_val}.")

    if len(errors) > 0:
        return errors
    else:
        return None


def detect_external_pdf_extractor_tool(config):
    doc_parser_tool_path = config.get('doc_parser_tool')
    doc_parser_tool_valid = False

    logger.info(f"Specified tool path: \"{doc_parser_tool_path}\"")

    if doc_parser_tool_path is not None and doc_parser_tool_path != "":
        if os.path.exists(doc_parser_tool_path):
            try:
                os.makedirs(config['internal_data_dir'], exist_ok=True)
                dummy_pdf_path = os.path.join(config['internal_data_dir'], 'test.pdf')
                with open(dummy_pdf_path, 'wb') as f:
                    f.write(MINIMAL_PDF_CONTENT)

                output_txt_filepath = os.path.join(config['internal_data_dir'], config['temp_txt_file'])

                popen_kwargs = {}
                if platform.system() == 'Windows':
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    startupinfo.wShowWindow = subprocess.SW_HIDE
                    popen_kwargs["startupinfo"] = startupinfo

                process = subprocess.Popen(
                    [doc_parser_tool_path, dummy_pdf_path, output_txt_filepath],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    **popen_kwargs
                )
                process.wait()

                if process.returncode == 0:
                    if not os.path.exists(output_txt_filepath):
                        logger.warning(f"File {output_txt_filepath} does not exist.")
                    else:
                        with open(output_txt_filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            contents = f.read()

                        os.remove(output_txt_filepath)

                        if 'Hello from dummy PDF!' in contents:
                            doc_parser_tool_valid = True
                        else:
                            logger.warning("Parser failed to extract correct text!")
                else:
                    stderr_output = process.stderr.read().strip()
                    logger.warning(f"Tool \"{doc_parser_tool_path}\" test failed with error:\n{stderr_output}")

            except Exception as e:
                logger.warning(f"Unexpected error: {e}")
        else:
            logger.warning(f"Tool \"{doc_parser_tool_path}\" not found.")

    if doc_parser_tool_valid:
        logger.info(f"\"{config['doc_parser_tool']}\" Parser Tool Detected!")
    else:
        logger.info("Using internal parser.")
        config['doc_parser_tool'] = None


def print_config(config, xxx=""):
    if config is None:
        return

    print(f"\n====={xxx}===================== Loaded Configuration ==========================")
    for key, value in config.items():
        display_value = value
        # Truncate displayed api_key
        if key == 'api_key' and isinstance(value, str):
            display_value = f"{value[:30]}..." if len(value) > 30 else value
        print(f"{key.capitalize().replace('_', ' '):<25}: {display_value}")
    print("=" * 75)


def set_resolution(config, resolution):
    if resolution == "normal":
        config["resolution_state"] = "normal"
        config['chunk_size'] = 1000
        config['padding_size'] = 0
    elif resolution == "high":
        config["resolution_state"] = "high"
        config['chunk_size'] = 300
        config['padding_size'] = 1

    if config['padding_size'] > 0:
        config['max_tokens'] = 2 * int(config['chunk_size'] + 2 * config['padding_size'] * config['chunk_size'])
    else:
        config['overlap'] = 100
        config['max_tokens'] = 3 * int(config['chunk_size'] + 2 * config['overlap'])


def build_extended_config(config):
    """Merges user config with internal defaults."""
    if config is None:
        return None

    config_internal = {
        'temperature': 0,
        'top_p': 0.3,
        'output_folder': "output_graphs",
        'internal_data_dir': 'data_cache',
        'temp_txt_file': 'tmp.dat',
        'db_filename': 'data.dat',
        "optimization_on": True
    }

    config.update(config_internal)
    set_resolution(config, "normal")

    return config


def _sanitize_config(config, key_max_length=128, val_max_length=1024, parent_key='root'):
    if isinstance(config, dict):
        for key, value in config.items():
            # Check key length
            if isinstance(key, str) and len(key) > key_max_length:
                raise ValueError(f"Config key '{parent_key}.{key}' exceeds "
                                 f"maximum allowed length of {key_max_length} characters.")

            if isinstance(value, (dict, list)):
                _sanitize_config(value, key_max_length, val_max_length, f"{parent_key}.{key}")
            elif isinstance(value, str) and len(value) > val_max_length:
                raise ValueError(f"String value for '{parent_key}.{key}' exceeds "
                                 f"maximum allowed length of {val_max_length} characters.")

    elif isinstance(config, list):
        for i, item in enumerate(config):
            if isinstance(item, (dict, list)):
                _sanitize_config(item, key_max_length, val_max_length, f"{parent_key}[{i}]")
            elif isinstance(item, str) and len(item) > val_max_length:
                raise ValueError(f"String value in '{parent_key}[{i}]' exceeds "
                                 f"maximum allowed length of {val_max_length} characters.")


def save_config(config):
    errors = []

    filename = config.get("config_file")
    if not filename:
        errors.append("Cannot save config: 'config_file' not found in config.")
        return errors

    valid_keys = set(CONFIG_TEMPLATE.keys())
    sanitized_config = {}
    for key in valid_keys:
        if key in config:
            sanitized_config[key] = config[key]
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(sanitized_config, f, indent=4)
    except Exception as e:
        errors.append(f"Error saving config to '{filename}': {e}")
        return errors

    return None


def load_config():
    filename = default_config['config_file']

    if not os.path.exists(filename):
        return None, [f"Error: '{filename}' deos not exist!"]

    file_size = os.path.getsize(filename)
    if file_size > 2_048:
        return None, [f"Error: '{filename}' is too large ({file_size} bytes). Possibly malicious."]

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except json.JSONDecodeError:
        return None, ["Error: Invalid JSON syntax in config file."]

    try:
        _sanitize_config(config)
    except ValueError as e:
        return None, [f"Error: {e}"]

    validation_errors = validate_config(config)
    config['config_file'] = 'config.json'

    return config, validation_errors
