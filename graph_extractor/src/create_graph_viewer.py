import json
import base64
import zlib
from graph_view_template import TEMPLATE
import html
from log_utils import get_module_logger


logger = get_module_logger("graph-viewer")


def compress_and_encode_graph_json(data_string):
    try:
        logger.info(f"Encoding...")
        compressed_data = zlib.compress(data_string.encode('utf-8'))
        logger.info(f"Compressed Data...")
        base64_encoded_data = base64.b64encode(compressed_data).decode('utf-8')
        logger.info(f"Base64 Encoded Data {base64_encoded_data}")

        return base64_encoded_data
    except Exception as e:
        print(f"Error: {e}")
        return None


def inject_data(html_content, placeholder, data):
    if placeholder in html_content:
        safe_data = data.replace("\\", "\\\\").replace("`", "\\`")
        safe_data = html.escape(safe_data)
        html_content = html_content.replace(placeholder, safe_data)
    else:
        logger.error(f"Could not find placeholder {placeholder} in HTML!")

    return html_content


def build_viewer(nodes_str, edges_str, metadata_str):
    html_content = TEMPLATE

    html_content = inject_data(html_content, 'idejonaszoveg1', compress_and_encode_graph_json(nodes_str))
    html_content = inject_data(html_content, 'idejonaszoveg2', compress_and_encode_graph_json(edges_str))
    html_content = inject_data(html_content, 'idejonaszoveg3', compress_and_encode_graph_json(metadata_str))

    return html_content
