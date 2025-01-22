import os
import asyncio
import requests
import gpt as gpt
from log_utils import get_module_logger


logger = get_module_logger("llm_api")

llm_config = None


def set_llm_config(config):
    global llm_config
    llm_config = config


def get_llm_config():
    if llm_config is None:
        raise ValueError("LLM configuration not set.")
    return llm_config


async def obtain_api_key(config):
    api_key = None

    if config['api'] == 'openai':
        api_key = os.getenv("OPENAI_API_KEY")
    else:
        logger.error(f"Unknown API name: {config['api']}")

    if api_key is None:
        logger.error(f"API Key not set for API: {config['api']}")
        return False

    config['api_key'] = api_key
    return True


async def execute(prompt, config):
    response = None
    if config['api'] == 'openai':
        response = await asyncio.to_thread(gpt.execute_prompt, prompt, config)
    else:
        logger.error(f"Unknown API name: {config['api']}")

    return response


def count_tokens(text):
    if llm_config:
        if llm_config['api'] == 'openai':
            return gpt.count_tokens(text, llm_config['model'])
        else:
            logger.error(f"Unknown API name: {llm_config['api']}")
    else:
        raise ValueError("LLM configuration not set.")


def test_api(config):
    api_key = config['api_key']

    if api_key and len(api_key) == 0:
        error_message = f"API key not specified! See \"{config['config_file']}\" file's \"api_key\" field."
        logger.error(error_message)
        return error_message

    try:
        requests.get("https://www.google.com", timeout=5)
        logger.info("Internet connection is available.")
    except requests.exceptions.RequestException:
        error_message = "Internet connection is not available."
        logger.error(error_message)
        return error_message

    if config['api'] == 'openai':
        error_message = gpt.test_openai_reachability(config)
    else:
        error_message = f"Unknown API name: {config['api']}"

    if error_message is not None:
        logger.error(error_message)

    return error_message
