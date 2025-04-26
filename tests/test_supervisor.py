import json
from unittest.mock import patch

import pytest

from src.llmwriter.models.structures import DocumentStructure
from src.llmwriter.nodes.supervisor import (
    get_supervisor_llm,
    parse_supervisor_response,
    section_router_node,
)


@pytest.fixture
def mock_state():
    return {
        "requirements": "Create a document with sections on AI, ML, and Data Science.",
        "supervisor_model": "claude-2",
    }


@pytest.fixture
def mock_response():
    return {
        "title": "Sample Document",
        "sections": [
            {
                "id": "section-1",
                "title": "AI",
                "type": "text",
                "content_requirements": "Overview of AI",
                "data_requirements": "",
                "subsections": [],
            },
            {
                "id": "section-2",
                "title": "ML",
                "type": "text",
                "content_requirements": "Overview of ML",
                "data_requirements": "",
                "subsections": [],
            },
        ],
    }


@patch("src.llmwriter.nodes.supervisor.ChatAnthropic")
@patch("src.llmwriter.nodes.supervisor.ChatOpenAI")
def test_get_supervisor_llm(mock_chat_openai, mock_chat_anthropic):
    mock_chat_anthropic.return_value = "MockAnthropic"
    mock_chat_openai.return_value = "MockOpenAI"

    llm = get_supervisor_llm("claude-2")
    assert llm == "MockAnthropic"

    llm = get_supervisor_llm("gpt-4")
    assert llm == "MockOpenAI"

    llm = get_supervisor_llm()
    assert llm == "MockAnthropic"


def test_parse_supervisor_response(mock_response):
    data = json.dumps(mock_response)
    doc_structure = parse_supervisor_response(data)
    assert doc_structure.title == mock_response["title"]
    assert len(doc_structure.sections) == len(mock_response["sections"])


def test_section_router_node(mock_response):
    doc_structure = DocumentStructure(**mock_response)
    state = {"doc_structure": doc_structure}

    result = section_router_node(state)
    assert "sections_to_process" in result
    assert len(result["sections_to_process"]) == len(mock_response["sections"])
    assert result["doc_title"] == mock_response["title"]
