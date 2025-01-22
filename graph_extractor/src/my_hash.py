import hashlib


def calculate_file_sha256(filepath):
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest(), None
    except FileNotFoundError:
        return None, f"File {filepath} not found."
    except PermissionError:
        return None, f"Can not read {filepath}! Permission denied."
    except Exception as e:
        return None, f"{str(e)}"


def main():
    # 1d5db44864a398c6a6c4b615b6c6b6ff458115606ae6806319f4f472a0c9787d
    code, error_message = calculate_file_sha256("documents/snow2.pdf")
    print(code)
    print(error_message)


if __name__ == '__main__':
    main()