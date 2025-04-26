import os
from datetime import datetime

import pytest

from src.utils.helpers import (
    check_environment,
    create_backup,
    decode_base64_to_image,
    encode_image_to_base64,
    ensure_directory_exists,
    extract_document_metadata,
    format_bytes,
    format_error_message,
    generate_timestamp,
    generate_unique_filename,
    get_file_size,
    get_project_root,
    get_temp_directory,
    load_json,
    save_json,
    validate_config,
)


@pytest.fixture
def temp_directory(tmp_path):
    return str(tmp_path)


def test_ensure_directory_exists(temp_directory):
    test_dir = os.path.join(temp_directory, "test_dir")
    ensure_directory_exists(test_dir)
    assert os.path.exists(test_dir)


def test_save_and_load_json(temp_directory):
    test_data = {"key": "value"}
    test_file = os.path.join(temp_directory, "test.json")
    save_json(test_data, test_file)
    assert os.path.exists(test_file)
    loaded_data = load_json(test_file)
    assert loaded_data == test_data


def test_generate_timestamp():
    timestamp = generate_timestamp()
    assert datetime.strptime(timestamp, "%Y%m%d_%H%M%S")


def test_generate_unique_filename():
    filename = generate_unique_filename("test", "txt")
    assert filename.startswith("test_")
    assert filename.endswith(".txt")


def test_extract_document_metadata():
    requirements = """
    This document is titled "Test Document".
    1. Section One
    2. Section Two
    """
    metadata = extract_document_metadata(requirements)
    assert metadata["title"] == "Test Document"
    assert metadata["section_count"] == 2


def test_create_backup(temp_directory):
    test_file = os.path.join(temp_directory, "test.txt")
    with open(test_file, "w") as f:
        f.write("test content")
    backup_file = create_backup(test_file)
    assert backup_file is not None
    assert os.path.exists(backup_file)


def test_format_bytes():
    assert format_bytes(0) == "0B"
    assert format_bytes(1024) == "1.00KB"
    assert format_bytes(1048576) == "1.00MB"


def test_encode_and_decode_image_to_base64(temp_directory):
    test_image_path = os.path.join(temp_directory, "test_image.txt")
    with open(test_image_path, "w") as f:
        f.write("test image content")
    encoded = encode_image_to_base64(test_image_path)
    decoded_path = os.path.join(temp_directory, "decoded_image.txt")
    decode_base64_to_image(encoded, decoded_path)
    with open(decoded_path) as f:
        assert f.read() == "test image content"


def test_get_file_size(temp_directory):
    test_file = os.path.join(temp_directory, "test.txt")
    with open(test_file, "w") as f:
        f.write("test content")
    assert get_file_size(test_file) == len("test content")


def test_get_project_root():
    project_root = get_project_root()
    assert os.path.exists(project_root)


def test_validate_config():
    valid_config = {"supervisor_model": "model1", "content_model": "model2", "parallel_workers": 5, "page_size": "A4"}
    invalid_config = {"content_model": "model2"}
    assert validate_config(valid_config) == (True, "")
    assert validate_config(invalid_config) == (False, "Missing required configuration key: supervisor_model")


def test_check_environment(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test_key")
    assert check_environment() == (True, "")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    assert check_environment() == (False, "Missing environment variable: OPENAI_API_KEY")


def test_format_error_message():
    assert format_error_message(FileNotFoundError("file not found")) == "File not found: file not found"
    assert format_error_message(PermissionError("permission denied")) == "Permission denied: permission denied"


def test_get_temp_directory(temp_directory, monkeypatch):
    monkeypatch.setattr("src.utils.helpers.get_project_root", lambda: temp_directory)
    temp_dir = get_temp_directory()
    assert os.path.exists(temp_dir)
