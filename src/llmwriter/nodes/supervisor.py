import json
import re
from typing import Any

import anthropic
import backoff
import openai
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI

from ..models.structures import DocumentStructure, SectionStructure, SubsectionStructure
from ..utils.constants import DEFAULT_SUPERVISOR_MODEL_ID


def get_supervisor_llm(model_name: str | None = None) -> ChatAnthropic | ChatOpenAI:
    """Get a high-capability LLM for supervision tasks"""
    if model_name:
        if "claude" in model_name.lower():
            return ChatAnthropic(model=model_name, temperature=0.2, max_tokens=8192)  # type: ignore[call-arg]
        else:
            return ChatOpenAI(model=model_name, temperature=0.2)

    # Default to Claude 3.7 for complex reasoning tasks
    return ChatAnthropic(model=DEFAULT_SUPERVISOR_MODEL_ID, temperature=0.2, max_tokens=8192)  # type: ignore[call-arg]


def parse_supervisor_response(response_content: str) -> DocumentStructure:
    """Parse the supervisor's response into a DocumentStructure"""
    try:
        # Try direct JSON parsing
        doc_structure = json.loads(response_content)
    except json.JSONDecodeError as error:
        # Try to extract JSON using regex
        json_match = re.search(r"```json\n(.*?)```", response_content, re.DOTALL)
        if json_match:
            doc_structure = json.loads(json_match.group(1))
            json_match = re.search(r"```(.*?)```", response_content, re.DOTALL)
            if json_match:
                doc_structure = json.loads(json_match.group(1))
            else:
                raise ValueError("Could not parse supervisor response as JSON") from error

    return DocumentStructure(**doc_structure)


@backoff.on_exception(
    backoff.expo,
    (openai.RateLimitError, anthropic.RateLimitError),
    max_tries=3,
    max_value=10,
)
def supervisor_node(state: dict[str, Any]) -> dict[str, Any]:
    """
    Supervisor node that analyzes requirements and creates document structure

    Args:
        state: The current state dictionary containing requirements

    Returns:
        Updated state with document structure added
    """
    requirements = state["requirements"]
    model_name = state.get("supervisor_model")

    # Create a supervisor LLM
    model = get_supervisor_llm(model_name).with_structured_output(DocumentStructure)

    # Define the prompt for the supervisor
    messages = [
        (
            "system",
            """You are an expert content editor responsible for planning complex PDF documents.
        Your task is to analyze the given document requirements and create a detailed document structure.
        For each document section, specify:
        1. What type of content is needed (text, table, chart, image, complex)
        2. For tables: what columns and rows should be included
        3. For charts: what type of chart and what data should be visualized
        4. For images: what the image should depict
        5. For complex layouts: how text, tables, and visuals should be arranged
        Visual Styling:
        - Specify when text content should include highlighted key points (use **KEY POINT** at the start)
        - For complex layouts, indicate if elements should be arranged horizontally or vertically
        - Suggest appropriate color theme ("professional", "creative", "modern", "warm", "minimal")
        - Recommend layout style ("standard", "modern", "wide", "two_column", "compact")
        Your response must be in this JSON format:
        {
            "title": "Document Title",
            "style_preferences": {
                "color_theme": "professional|creative|modern|warm|minimal",
                "layout_style": "standard|modern|wide|two_column|compact",
                "visual_notes": "Any specific notes about visual styling"
            },
            "sections": [
                {
                    "id": "section-1",
                    "title": "Section Title",
                    "type": "text|table|chart|image|complex",
                    "content_requirements": "Detailed requirements for this section",
                    "data_requirements": "For tables/charts, specify data requirements",
                    "layout_properties": {
                        "arrangement": "horizontal|vertical",
                        "highlight_key_points": true|false,
                        "use_boxed_content": true|false
                    },
                    "subsections": [ ... ] (optional, same structure as sections)
                },
                ...
            ]
        }
        For better output quality:
        - Include a mix of content types based on what would be most appropriate
        - Make sure each section has a unique ID
        - Be very specific in content requirements to guide content generation
        - Think about visual appeal - use boxed content for important information
        - For text sections, mark important points with **KEY POINT** prefix
        - For tables, specify what columns are needed and what kind of data
        - For charts, indicate what relationships should be visualized
        - For complex layouts, detail how elements should be arranged
        """,
        ),
        ("human", f"{requirements}"),
    ]

    # Call the supervisor LLM
    doc_structure = model.invoke(messages)

    # Extract style preferences if available
    if hasattr(doc_structure, "style_preferences"):
        state["style_preferences"] = doc_structure.style_preferences

        # Apply style preferences directly if specified
        if hasattr(doc_structure.style_preferences, "color_theme"):
            state["selected_theme"] = doc_structure.style_preferences.color_theme

        if hasattr(doc_structure.style_preferences, "layout_style"):
            state["selected_layout"] = doc_structure.style_preferences.layout_style

    return {"doc_structure": doc_structure, **state}


def section_router_node(state: dict[str, Any]) -> dict[str, Any]:
    """
    Router node that distributes sections to appropriate content generators

    Args:
        state: The current state dictionary containing document structure

    Returns:
        Updated state with sections to process
    """
    doc_structure: DocumentStructure = state["doc_structure"]

    # Flatten the document structure to get all sections and subsections
    all_sections = []

    def collect_sections(sections: list[SectionStructure] | list[SubsectionStructure], parent_path: str = "") -> None:
        for i, section in enumerate(sections):
            current_path = f"{parent_path}/{i}" if parent_path else f"{i}"
            section_info = {"section": section, "path": current_path}
            all_sections.append(section_info)

            if section.subsections:  # type: ignore[attr-defined]
                collect_sections(section.subsections, current_path)  # type: ignore[attr-defined]

    collect_sections(doc_structure.sections)

    return {"sections_to_process": all_sections, "doc_title": doc_structure.title}
