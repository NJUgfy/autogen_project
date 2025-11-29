import os

def read_file(file_path: str) -> str:
    try:
        with open(file_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File not found at '{file_path}'."
    except Exception as e:
        return f"Error reading file '{file_path}': {e}"

def write_to_file(file_path: str, content: str) -> str:
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            f.write(content)
        return f"Successfully wrote to {file_path}"
    except Exception as e:
        return f"Error writing to file '{file_path}': {e}"
