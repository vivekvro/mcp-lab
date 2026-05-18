import os, asyncio
from pathlib import Path
from pydantic import Field,BaseModel
from typing import Annotated
from langchain.tools import tool



# ----------------- list directories---------------------------------
@tool
async def list_folders(folder_path:str)->list[Path]:
    """Retrieve all subdirectories from the specified filesystem path.

    Use this tool when you need to explore folder structures,
    navigate project directories, or inspect available subfolders.

    Args:
        folder_path: Target directory path.
    Returns:
        List of subfolder paths located inside the target directory.
    """
    path = Path(folder_path)
    folders = [dir for dir in path.iterdir() if dir.is_dir()]
    return folders

@tool
async def list_files(folder_path:str)->list[Path]:
    """
    Retrieve all files from the specified directory path.

    Use this tool when you need to inspect available files,
    browse project contents, or access files inside a folder.

    Args:
        folder_path: Target directory path.

    Returns:
        A list of Path objects representing all files
        inside the provided directory.

    Raises:
        FileNotFoundError: If the given path does not exist.
        NotADirectoryError: If the provided path is not a directory.
        PermissionError: If access to the directory is denied.
    """

    path = Path(folder_path)
    files = [dir for dir in path.iterdir() if dir.is_file()]
    return files
#------------------------------read files------------------------------------------------



NOT_ALLOWED_EXTENSIONS = {
    ".exe", ".dll", ".so", ".bin",
    ".db", ".sqlite", ".sqlite3",
    ".pem", ".key", ".crt",
    ".zip", ".rar", ".7z",
    ".iso", ".img",
    ".bat", ".cmd", ".sh",
}

NOT_ALLOWED_FILES = {
    ".env",
    ".env.local",
    "id_rsa",
    "id_ed25519",
    "credentials.json",
}


def is_safe_file(path: Path) -> bool:

    # Block hidden files
    if path.name.startswith("."):
        return False

    # Block sensitive filenames
    if path.name in NOT_ALLOWED_FILES:
        return False

    # Block dangerous extensions
    if path.suffix.lower() in NOT_ALLOWED_EXTENSIONS:
        return False

    # Block large files (>10MB)
    if path.stat().st_size > 10 * 1024 * 1024:
        return False

    # Allow only readable text files
    return True


async def read_files(file_path:str)->str:
    """
    Securely read and return the content of a text-based file.

    This tool validates file safety before reading and blocks
    dangerous, binary, executable, hidden, oversized, or
    sensitive files to prevent unsafe filesystem access.

    The tool is intended for:
    - Source code inspection
    - Reading configuration files
    - Viewing documentation or text files
    - Parsing structured text formats

    Supported readable formats commonly include:
    .py, .txt, .md, .json, .yaml, .toml, .js, .ts

    Blocked file categories include:
    - Executables and binaries
    - Environment/secret files
    - SSH keys and credentials
    - Compressed archives
    - Extremely large files
    - Non-text or unsupported encoded files

    Args:
        file_path: Absolute or relative path to the target file.

    Returns:
        The decoded text content of the file.

    Raises:
        FileNotFoundError: If the file does not exist.
        PermissionError: If access is denied.
        UnicodeDecodeError: If the file is not readable as text.
        ValueError: If the file is unsafe or unsupported.
        IsADirectoryError: If the provided path is a directory.
    """
    try:
        path = Path(file_path)
        if is_safe_file(path):
            with open(path,"r",encoding="utf-8") as f:
                file_content = f.read()
            return file_content
        else:
            raise ValueError("Blocked unsafe or unsupported file.")
    except FileNotFoundError:
        return "File not found."

    except PermissionError:
        return "Permission denied."

    except UnicodeDecodeError:
        return "File is not readable as text."

    except IsADirectoryError:
        return "Provided path is a directory."

    except ValueError as e:
        return str(e)

    except Exception as e:
        return f"Unexpected error: {e}"





def tree_directory(path):
    # TODO: Generate recursive folder tree structure
    pass


def read_file(path):
    # TODO: Safely read text file content
    pass


def read_file_chunk(path, start, size):
    # TODO: Read partial content from large files
    pass


def append_file(path, content):
    # TODO: Append content to existing file
    pass


def write_file(path, content):
    # TODO: Write content into file safely
    pass


def create_file(path):
    # TODO: Create empty file if not exists
    pass


def create_folder(path):
    # TODO: Create directory recursively
    pass


def copy_file(src, dst):
    # TODO: Copy file from source to destination
    pass


def move_file(src, dst):
    # TODO: Move file safely
    pass


def rename_file(src, new_name):
    # TODO: Rename file or folder
    pass


def delete_file(path):
    # TODO: Delete file safely with validation
    pass


def delete_folder(path):
    # TODO: Delete directory recursively
    pass


def search_files(path, pattern):
    # TODO: Search files matching pattern
    pass


def grep_text(path, query):
    # TODO: Search text inside files
    pass


def find_by_extension(path, ext):
    # TODO: Find files by extension
    pass


def validate_path(path):
    # TODO: Validate filesystem path security
    pass


def is_safe_file(path):
    # TODO: Check if file is safe to access
    pass


def allowed_workspace():
    # TODO: Return allowed root workspace path
    pass


def file_exists(path):
    # TODO: Check whether file exists
    pass


def get_file_info(path):
    # TODO: Return metadata about file
    pass


def get_last_modified(path):
    # TODO: Return last modified timestamp
    pass


def get_directory_size(path):
    # TODO: Calculate total directory size
    pass


def hash_file(path):
    # TODO: Generate file hash
    pass


def extract_python_metadata(path):
    # TODO: Extract classes, functions, imports, globals
    pass


def extract_imports(path):
    # TODO: Extract Python imports using AST
    pass


def extract_classes(path):
    # TODO: Extract Python classes
    pass


def extract_functions(path):
    # TODO: Extract Python functions
    pass


def extract_docstrings(path):
    # TODO: Extract docstrings from source code
    pass


def chunk_file(path):
    # TODO: Split large file into chunks
    pass


def summarize_code(path):
    # TODO: Generate code summary using LLM
    pass


def build_repo_map(path):
    # TODO: Build repository structure map
    pass


def generate_file_embedding(path):
    # TODO: Generate vector embedding for file
    pass


def watch_directory(path):
    # TODO: Monitor directory changes
    pass


def detect_file_changes(path):
    # TODO: Detect modified files
    pass


def zip_folder(path):
    # TODO: Compress folder into archive
    pass


def extract_archive(path):
    # TODO: Extract compressed archive safely
    pass


def read_json(path):
    # TODO: Read JSON file
    pass


def write_json(path, data):
    # TODO: Write JSON safely
    pass


def read_yaml(path):
    # TODO: Read YAML file
    pass


def write_yaml(path, data):
    # TODO: Write YAML safely
    pass


def tail_file(path, lines=100):
    # TODO: Return last N lines from file
    pass


def create_temp_file():
    # TODO: Create temporary file
    pass


def create_temp_folder():
    # TODO: Create temporary folder
    pass


def check_permissions(path):
    # TODO: Check filesystem permissions
    pass


def make_readonly(path):
    # TODO: Convert file to readonly mode
    pass



async def main():
    print_this = await read_files(r"D:\\MCPs\\mcp_servers\\expense_tracker.py")
    print(print_this)
if __name__=="__main__":
    asyncio.run(main())
