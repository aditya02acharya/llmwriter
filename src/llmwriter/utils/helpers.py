# src/utils/helpers.py
import base64
import json
import logging
import os
import sys
from datetime import datetime
from typing import Any, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger: logging.Logger = logging.getLogger("pdf_generator")


def setup_logging(level: int = logging.INFO, log_file: Optional[str] = None) -> None:
    """
    Set up logging configuration

    Args:
        level (int): Logging level
        log_file (optional, str): Optional path to a log file
    """
    handlers = [logging.StreamHandler(sys.stdout)]

    if log_file:
        handlers.append(logging.FileHandler(log_file))  # type: ignore[arg-type]

    logging.basicConfig(level=level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", handlers=handlers)


def ensure_directory_exists(directory_path: str) -> None:
    """
    Ensure that a directory exists, creating it if necessary

    Args:
        directory_path (str): Path to the directory
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        logger.info(f"Created directory: {directory_path}")


def save_json(data: Any, filepath: str) -> None:
    """
    Save data to a JSON file

    Args:
        data: Data to save
        filepath (str): Path to the output file
    """
    directory = os.path.dirname(filepath)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

    logger.info(f"Saved JSON data to: {filepath}")


def load_json(filepath: str) -> Any:
    """
    Load data from a JSON file

    Args:
        filepath: Path to the JSON file

    Returns:
        Loaded data
    """
    with open(filepath) as f:
        data = json.load(f)

    return data


def generate_timestamp() -> str:
    """
    Generate a timestamp string

    Returns:
        Timestamp string in the format YYYYMMDD_HHMMSS
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def generate_unique_filename(base_name: str, extension: str) -> str:
    """
    Generate a unique filename with timestamp

    Args:
        base_name (str): Base name for the file
        extension (str): File extension

    Returns:
        str: Unique filename
    """
    timestamp = generate_timestamp()
    return f"{base_name}_{timestamp}.{extension}"


def extract_document_metadata(requirements: str) -> dict[str, Union[str, int]]:
    """
    Extract metadata from document requirements

    Args:
        requirements (str): Document requirements text

    Returns:
        Dict[str, Union[str, int]]: Dictionary of metadata
    """
    # This is a simple implementation that could be enhanced with LLM-based extraction
    lines = requirements.strip().split("\n")

    metadata: dict[str, Union[str, int]] = {
        "creation_date": datetime.now().strftime("%Y-%m-%d"),
        "generator": "Synthetic PDF Generator",
    }

    # Try to extract title from the first non-empty line
    for line in lines:
        if line.strip():
            if "titled" in line.lower():
                parts = line.split("titled", 1)
                if len(parts) > 1:
                    title_part = parts[1].strip()
                    # Extract text between quotes if present
                    if title_part.startswith('"') and '"' in title_part[1:]:
                        metadata["title"] = title_part.split('"')[1]
                    elif title_part.startswith("'") and "'" in title_part[1:]:
                        metadata["title"] = title_part.split("'")[1]
                    else:
                        words = title_part.split()
                        metadata["title"] = " ".join(words[:5]) + "..."
            break

    # Count sections
    section_count = sum(1 for line in lines if line.strip() and line.strip()[0].isdigit() and "." in line)
    metadata["section_count"] = section_count

    return metadata


def create_backup(filepath: str) -> Optional[str]:
    """
    Create a backup of a file

    Args:
        filepath (str): Path to the file to backup

    Returns:
        Optional[str]: Path to the backup file, or None if the file does not exist or an error occurs
    """
    if not os.path.exists(filepath):
        return None

    backup_path = f"{filepath}.bak"
    try:
        with open(filepath, "rb") as src, open(backup_path, "wb") as dst:
            dst.write(src.read())
        logger.info(f"Created backup: {backup_path}")
        return backup_path
    except Exception as e:
        logger.exception(f"Failed to create backup of {filepath}: {e!s}")
        return None


def format_bytes(size_bytes: int) -> str:
    """
    Format a byte size as a human-readable string

    Args:
        size_bytes (int): Size in bytes

    Returns:
        str: Formatted string
    """
    if size_bytes == 0:
        return "0B"

    size_names = ("B", "KB", "MB", "GB", "TB")
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes //= 1024
        i += 1

    return f"{size_bytes:.2f}{size_names[i]}"


def encode_image_to_base64(image_path: str) -> str:
    """
    Encode an image file to base64

    Args:
        image_path (str): Path to the image file

    Returns:
        str: Base64-encoded string
    """
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")

    return encoded_string


def decode_base64_to_image(base64_string: str, output_path: str) -> str:
    """
    Decode a base64 string to an image file

    Args:
        base64_string (str): Base64-encoded string
        output_path (str): Path to save the image

    Returns:
        str: Path to the saved image
    """
    with open(output_path, "wb") as image_file:
        image_file.write(base64.b64decode(base64_string))

    return output_path


def get_file_size(filepath: str) -> int:
    """
    Get the size of a file

    Args:
        filepath (str): Path to the file

    Returns:
        int: Size in bytes
    """
    return os.path.getsize(filepath)


def get_project_root() -> str:
    """
    Get the project root directory

    Returns:
        str: Path to the project root
    """
    # This assumes the helpers.py file is in utils/ in the project root
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(current_dir, "../.."))


def validate_config(config: dict[str, Any]) -> tuple[bool, str]:
    """
    Validate configuration values

    Args:
        config (dict[str, Any]): Configuration dictionary

    Returns:
        tuple[bool, str]: Tuple of (is_valid, error_message)
    """
    required_keys = ["supervisor_model", "content_model"]

    for key in required_keys:
        if key not in config:
            return False, f"Missing required configuration key: {key}"

    if "parallel_workers" in config:
        try:
            workers = int(config["parallel_workers"])
            if workers < 1 or workers > 10:
                return False, "parallel_workers must be between 1 and 10"
        except ValueError:
            return False, "parallel_workers must be an integer"

    if "page_size" in config:
        valid_sizes = ["A4", "LETTER"]
        if config["page_size"].upper() not in valid_sizes:
            return False, f"page_size must be one of: {', '.join(valid_sizes)}"

    return True, ""


def check_environment() -> tuple[bool, str]:
    """
    Check if the environment is properly set up

    Returns:
        Tuple of (is_valid, error_message)
    """
    required_env_vars: list[str] = ["OPENAI_API_KEY"]

    for var in required_env_vars:
        if var not in os.environ or not os.environ[var]:
            return False, f"Missing environment variable: {var}"

    return True, ""


def format_error_message(error: Exception) -> str:
    """
    Format an exception into a user-friendly error message

    Args:
        error (Exception): Exception object

    Returns:
        str: Formatted error message
    """
    if isinstance(error, ImportError):
        return f"Missing dependency: {error!s}"
    elif isinstance(error, PermissionError):
        return f"Permission denied: {error!s}"
    elif isinstance(error, FileNotFoundError):
        return f"File not found: {error!s}"
    else:
        return f"Error: {error!s}"


def summarize_document_structure(doc_structure: Any) -> str:
    """
    Create a text summary of a document structure

    Args:
        doc_structure (Any): Document structure object

    Returns:
        str: Text summary
    """
    summary: list[str] = [f"Document Title: {doc_structure.title}", ""]

    def add_section(section: Any, level: int = 0) -> None:
        indent = "  " * level
        section_type = f"[{section.type}]" if hasattr(section, "type") else ""
        summary.append(f"{indent}- {section.title} {section_type}")

        if hasattr(section, "subsections") and section.subsections:
            for subsection in section.subsections:
                add_section(subsection, level + 1)

    for section in doc_structure.sections:
        add_section(section)

    return "\n".join(summary)


def get_temp_directory() -> str:
    """
    Get a temporary directory for the project

    Returns:
        str: Path to temporary directory
    """
    temp_dir = os.path.join(get_project_root(), "temp")
    ensure_directory_exists(temp_dir)
    return temp_dir
