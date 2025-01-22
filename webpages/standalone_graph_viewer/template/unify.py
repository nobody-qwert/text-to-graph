import os
import re
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter('[%(levelname)s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def read_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Failed to read file: {filepath} - {e}")
        return ''


def inline_css(html, folder):
    def replace_css(match):
        css_file = match.group(2).strip('"\'')

        if not css_file:
            logger.warning("Empty CSS file reference found.")
            return match.group(0)

        css_path = os.path.join(folder, css_file)
        logger.debug(f"Checking CSS file: {css_file} at Path: {css_path}")

        if os.path.isfile(css_path):
            logger.info(f"Inlining CSS file: {css_file}")
            return f'<style>{read_file(css_path)}</style>'
        else:
            logger.warning(f"CSS file not found: {css_file}")
            return match.group(0)

    return re.sub(r'<link\s+[^>]*href=(\'|")?([^"\'>\s]+)(\1)?[^>]*>', replace_css, html)


def inline_js(html, folder):
    def replace_js(match):
        js_file = match.group(2).strip('"\'')

        if not js_file:
            logger.warning("Empty JS file reference found.")
            return match.group(0)

        js_path = os.path.join(folder, js_file)
        logger.debug(f"Checking JS file: {js_file} at Path: {js_path}")

        if os.path.isfile(js_path):
            logger.info(f"Inlining JS file: {js_file}")
            return f'<script>{read_file(js_path)}</script>'
        else:
            logger.warning(f"JS file not found: {js_file}")
            return match.group(0)

    return re.sub(r'<script\s+[^>]*src=(\'|")?([^"\'>\s]+)(\1)?[^>]*>.*?</script>', replace_js, html, flags=re.DOTALL)


def unify_html(html_file, output_file):
    folder = os.path.dirname(html_file)
    logger.info(f"Reading HTML file: {html_file}")
    html_content = read_file(html_file)
    logger.info("Inlining CSS files...")
    html_content = inline_css(html_content, folder)
    logger.info("Inlining JS files...")
    html_content = inline_js(html_content, folder)
    logger.info(f"Writing unified HTML to: {output_file}")
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        logger.info(f"Unified HTML written to {output_file}")
    except Exception as e:
        logger.error(f"Failed to write unified HTML: {e}")


def main():
    input_file = 'prod/template.html'
    output_file = 'prod/template_full.html'
    unify_html(input_file, output_file)


if __name__ == '__main__':
    main()

