from openai import OpenAI, OpenAIError
from log_utils import get_module_logger
import tiktoken

logging = get_module_logger("gpt")


def _uses_completion_tokens(model: str) -> bool:
    return isinstance(model, str) and model.startswith("gpt-5")


def test_openai_reachability(config):
    try:
        response = execute_prompt("Respond with the word: hello", config)
        if len(response) > 0:
            logging.info(f"OpenAI {config['model']} API is reachable. Response {response}")
        else:
            error_msg = f"OpenAI {config['model']} API responded with no data."
            logging.error(error_msg)
            return error_msg
    except Exception as e:
        error_msg = f"OpenAI {config['model']}\n{e}"
        logging.error(error_msg)
        return error_msg


def count_tokens(text, model):
    try:
        encoding = tiktoken.encoding_for_model(model)
        tokens = encoding.encode(text)
        return len(tokens)
    except ImportError:
        logging.warning("tiktoken module not installed. Token count will be approximate.")
        return len(text.split())


def execute_prompt(prompt, config):
    input_length = count_tokens(prompt, config['model'])
    logging.info(f"GPT Input tokens: {input_length}")
    logging.info(prompt)

    system_message = {"role": "system", "content": "You are a structured data extraction assistant."}
    messages = [system_message, {"role": "user", "content": prompt}]

    client = OpenAI(api_key=config['api_key'])

    request_kwargs = {
        "messages": messages,
        "model": config['model'],
        "temperature": config['temperature'],
        "top_p": config['top_p'],
        "timeout": config['llm_timeout'],
    }

    token_budget = config.get('max_completion_tokens') or config.get('max_tokens')
    if token_budget is not None:
        if _uses_completion_tokens(config['model']):
            request_kwargs['max_completion_tokens'] = token_budget
        else:
            request_kwargs['max_tokens'] = token_budget

    response = client.chat.completions.create(**request_kwargs)

    response_content = response.choices[0].message.content.strip()
    output_length = count_tokens(response_content, config['model'])
    logging.info(f"Output tokens: {output_length}")

    logging.info(response_content)

    return response_content


