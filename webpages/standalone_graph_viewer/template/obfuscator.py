import os
import shutil
import subprocess
import sys
from csscompressor import compress
from htmlmin import minify


def ensure_dir_exists(path):
    """Ensure that a directory exists; if not, create it."""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Created directory: {path}")


def process_js_file(input_path, output_path):
    """Obfuscate JavaScript files using javascript-obfuscator via absolute path."""
    js_obfuscator_path = r"C:\Users\lazlo\AppData\Roaming\npm\javascript-obfuscator.cmd"
    if not os.path.exists(js_obfuscator_path):
        print(f"Error: '{js_obfuscator_path}' does not exist.")
        sys.exit(1)

    cmd = [js_obfuscator_path, input_path, '--output', output_path]
    try:
        result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(f"Obfuscated JS: {input_path} -> {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error obfuscating JS file {input_path}: {e.stderr.strip()}")


def process_css_file(input_path, output_path):
    """Minify CSS files using csscompressor."""
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
        minified_css = compress(css_content)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(minified_css)
        print(f"Minified CSS: {input_path} -> {output_path}")
    except Exception as e:
        print(f"Error minifying CSS file {input_path}: {e}")


def process_html_file(input_path, output_path):
    """Minify HTML files using htmlmin."""
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Prepare keyword arguments for minify
        minify_kwargs = {
            'remove_comments': True,
            'remove_empty_space': True,
            'reduce_boolean_attributes': True,
            'remove_optional_attribute_quotes': True,
            'keep_pre': True
        }

        # Attempt to add 'remove_empty_attributes' if supported
        try:
            minified_html = minify(html_content, **minify_kwargs, remove_empty_attributes=True)
        except TypeError:
            # If 'remove_empty_attributes' is not supported, omit it
            minified_html = minify(html_content, **minify_kwargs)
            print("Warning: 'remove_empty_attributes' is not supported by htmlmin in the current version.")

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(minified_html)
        print(f"Minified HTML: {input_path} -> {output_path}")
    except Exception as e:
        print(f"Error minifying HTML file {input_path}: {e}")


def copy_other_file(input_path, output_path):
    """Copy files that do not require processing."""
    try:
        shutil.copy2(input_path, output_path)
        print(f"Copied: {input_path} -> {output_path}")
    except Exception as e:
        print(f"Error copying file {input_path}: {e}")


def main():
    dev_dir = 'dev'
    prod_dir = 'prod'

    print("Current PATH:", os.environ['PATH'])

    if not os.path.exists(dev_dir):
        print(f"Error: Source directory '{dev_dir}' does not exist.")
        sys.exit(1)

    ensure_dir_exists(prod_dir)

    for root, dirs, files in os.walk(dev_dir):
        rel_path = os.path.relpath(root, dev_dir)
        prod_root = os.path.join(prod_dir, rel_path) if rel_path != '.' else prod_dir
        ensure_dir_exists(prod_root)

        for file in files:
            dev_file_path = os.path.join(root, file)
            prod_file_path = os.path.join(prod_root, file)
            ext = os.path.splitext(file)[1].lower()

            if ext == '.js':
                process_js_file(dev_file_path, prod_file_path)
            elif ext == '.css':
                process_css_file(dev_file_path, prod_file_path)
            elif ext in ['.html', '.htm']:
                process_html_file(dev_file_path, prod_file_path)
            else:
                copy_other_file(dev_file_path, prod_file_path)

    print("\nBuild process completed. All files are processed and saved in the 'prod' folder.")


if __name__ == '__main__':
    main()
