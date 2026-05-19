import os, asyncio
from pathlib import Path
from pydantic import field_validator,Field,BaseModel,model_validator
from typing import Annotated
from langchain.tools import tool



class PathInput(BaseModel):
    path: str

    @field_validator("path")
    @classmethod
    def validate_path(cls, value):

        path = Path(value)

        if not path.exists():
            raise ValueError("Path does not exist")

        return value


# ----------------- list directories---------------------------------
@tool
async def list_folders(path_input:PathInput)->list[Path]:
    """
    Retrieve all subdirectories located inside the specified directory path.

    This tool is useful for filesystem exploration, repository
    navigation, project structure analysis, and agent-based
    directory traversal workflows.

    The provided path is validated using the PathInput schema
    before accessing the filesystem.

    Args:
        path_input: Validated path input containing the target
        directory location.

    Returns:
        A list of Path objects representing all immediate
        subdirectories inside the target directory.

    Raises:
        FileNotFoundError: If the directory does not exist.
        NotADirectoryError: If the provided path is not a directory.
        PermissionError: If access to the directory is denied.
        ValueError: If the path fails validation checks.
    """
    path = Path(path_input.path)
    folders = [dir for dir in path.iterdir() if dir.is_dir()]
    return folders

@tool
async def list_files(path_input:PathInput)->list[Path]:
    """
    Retrieve all files located inside the specified directory path.

    This tool is useful for browsing project files, inspecting
    repository contents, locating readable resources, and
    supporting agent-based filesystem navigation workflows.

    The provided path is validated using the PathInput schema
    before accessing the filesystem.

    Args:
        path_input: Validated path input containing the target
        directory location.

    Returns:
        A list of Path objects representing all immediate
        files inside the target directory.

    Raises:
        FileNotFoundError: If the provided path does not exist.
        NotADirectoryError: If the provided path is not a directory.
        PermissionError: If access to the directory is denied.
        ValueError: If the path fails validation checks.
    """

    path = Path(path_input.path)
    files = [file for file in path.iterdir() if dir.is_file()]
    return files




@tool
def tree_directory(path, indent=""):
    """
    Recursively generate a tree-style representation of a directory.

    This tool traverses all files and subdirectories starting
    from the provided root path and returns a formatted string
    representing the hierarchical filesystem structure.

    Useful for:
    - Repository mapping
    - Project structure visualization
    - Agent-based filesystem navigation
    - Codebase exploration
    - Documentation and RAG preprocessing

    The generated output follows a tree-like format similar to:
    
    ├── src
    │   ├── main.py
    │   ├── utils.py
    ├── README.md

    Args:
        path: Root directory path to traverse.
        indent: Internal indentation used for recursive formatting.

    Returns:
        A formatted string representing the complete directory tree.

    Raises:
        FileNotFoundError: If the provided path does not exist.
        NotADirectoryError: If the provided path is not a directory.
        PermissionError: If access to the directory is denied.
    """

    path = Path(path)
    tree = ""

    for item in path.iterdir():
        tree += f"\n{indent}├── {item.name}"

        if item.is_dir():
            tree += tree_directory(
                item,
                indent + "│   "
            )

    return tree




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

@tool
async def read_files(path_input:PathInput)->str:
    """
    Securely read and return the content of a text-based file.

    This tool validates file safety before reading and blocks
    dangerous, binary, executable, hidden, oversized, or
    sensitive files to prevent unsafe filesystem access.

    Supported use cases include:
    - Source code inspection
    - Reading documentation files
    - Parsing structured text formats
    - Agent-based repository analysis

    Common supported formats:
    .py, .txt, .md, .json, .yaml, .toml, .js, .ts

    Restricted file categories include:
    - Executables and binaries
    - Secret/environment files
    - SSH keys and credentials
    - Archives and compressed files
    - Extremely large files
    - Unsupported or non-text files

    Args:
        path_input: Validated path input containing the
        target file location.

    Returns:
        The decoded text content of the file.

    Raises:
        FileNotFoundError: If the file does not exist.
        PermissionError: If access is denied.
        UnicodeDecodeError: If the file is not readable as text.
        IsADirectoryError: If the provided path is a directory.
        ValueError: If the file is unsafe or unsupported.
    """
    try:
        path = Path(path_input.path)
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




class FileChunk(PathInput):
    start_line:int = Field(ge=1)
    end_line:int = Field(gt=1)
    @classmethod
    @model_validator(mode="after")
    def validate_range(self):
        if self.end_line <= self.start_line:
            raise ValueError(
            "end_line must be greater "
            "than start_line"
            )
        if self.end_line - self.start_line > 500:
            raise ValueError("chunk too large")
        return self


def read_file_chunk(filechunk: FileChunk)->str:
    path = Path(filechunk.path)
    start_line = filechunk.start_line
    end_line = filechunk.end_line
    lines = []
    with open(path,"r",encoding="utf-8") as f:
        for current,line in enumerate(f,start=1):
            if current < start_line:
                continue
            if current > end_line:
                break
            lines.append(line.rstrip())
    return "\n".join(lines)

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
    print_this = tree_directory(r"D:\\MCPs")
    print(print_this)
if __name__=="__main__":
    asyncio.run(main())
