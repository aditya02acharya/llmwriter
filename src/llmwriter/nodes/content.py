from concurrent.futures import ThreadPoolExecutor
from typing import Any

import anthropic
import backoff
import openai
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from ..models.structures import (
    ChartContent,
    ComplexContent,
    ComplexElement,
    ImageContent,
    SectionContent,
    SectionStructure,
    SubsectionStructure,
    TableContent,
)
from ..utils.constants import DEFAULT_CONTENT_MODEL_ID


def get_content_llm(model_name: str | None = None) -> ChatAnthropic | ChatOpenAI:
    """Get an LLM for content generation"""
    if model_name:
        if "claude" in model_name.lower():
            return ChatAnthropic(model=model_name, temperature=0.7, max_tokens=4000)  # type: ignore[call-arg]
        else:
            return ChatOpenAI(model=model_name, temperature=0.7)  # type: ignore[call-arg]

    # Default to GPT-4 for content generation
    return ChatAnthropic(model=DEFAULT_CONTENT_MODEL_ID, temperature=0.7, max_tokens=4000)  # type: ignore[call-arg]


def get_review_llm(model_name: str | None = None) -> ChatAnthropic | ChatOpenAI:
    """Get an LLM for content review"""
    if model_name:
        if "claude" in model_name.lower():
            return ChatAnthropic(model=model_name, temperature=0.3, max_tokens=4000)  # type: ignore[call-arg]
        else:
            return ChatOpenAI(model=model_name, temperature=0.3)  # type: ignore[call-arg]

    # Default to GPT-o4 with low temperature for reviews
    return ChatOpenAI(model="o4-mini", temperature=0.3, max_tokens=4000)  # type: ignore[call-arg]


@backoff.on_exception(
    backoff.expo,
    (openai.RateLimitError, anthropic.RateLimitError),
    max_tries=3,
    max_value=10,
)
def generate_text_content(section: SectionStructure | SubsectionStructure, model: ChatAnthropic | ChatOpenAI) -> str:
    """Generate text content for a section"""
    # Check if section has layout properties
    highlight_key_points = False
    if hasattr(section, "layout_properties") and hasattr(section.layout_properties, "highlight_key_points"):
        highlight_key_points = section.layout_properties.highlight_key_points

    styling_instructions = ""
    if highlight_key_points:
        styling_instructions = """
        For important information, use the format:
        **KEY POINT** Your important point here
        This will automatically create highlighted boxes in the final document.
        """
    messages = [
        (
            "system",
            f"""You are a professional content writer specialized in creating high-quality document text.
        Create detailed, well-structured content for the document section described below.
        Guidelines:
        - Write in a professional, clear style
        - Include appropriate headings and subheadings
        - Use paragraph breaks for readability
        - Include topic sentences and supporting details
        - Maintain a logical flow of ideas
        - Be concise but comprehensive
        - Do not use placeholders - generate actual substantive content
        {styling_instructions}
        Output plain text with minimal markdown formatting (only headings and emphasis where needed).
        """,
        ),
        (
            "human",
            f"""
        Section title: {section.title}
        Requirements: {section.content_requirements}
        Generate appropriate content for this section.
        """,
        ),
    ]
    # Format the prompt with section title and requirements
    response = model.invoke(messages)
    return response.content


@backoff.on_exception(
    backoff.expo,
    (openai.RateLimitError, anthropic.RateLimitError),
    max_tries=3,
    max_value=10,
)
def generate_table_content(
    section: SectionStructure | SubsectionStructure, model: ChatAnthropic | ChatOpenAI
) -> TableContent:
    """Generate table content for a section"""

    data_requirements = (
        section.data_requirements
        if section.data_requirements
        else "No specific data requirements provided, use your judgment to create appropriate data."
    )
    struct_model = model.with_structured_output(TableContent)

    messages = [
        (
            "system",
            """You are a data specialist who creates tables with realistic data.
        Create a detailed table based on the requirements provided. Use realistic data that would be appropriate for a professional document.
        Your response must be a valid JSON object with this structure:
        {
            "headers": ["Column1", "Column2", ...],
            "rows": [
                ["Value1", "Value2", ...],
                ["Value1", "Value2", ...],
                ...
            ]
        }
        Guidelines:
        - Include at least 4-8 rows of data unless otherwise specified
        - Make sure all rows have the same number of columns
        - Use appropriate column headers
        - Include a mix of text and numeric data as appropriate
        - Ensure data is realistic and internally consistent
        """,
        ),
        (
            "human",
            f"""
        Section title: {section.title}
        Content requirements: {section.content_requirements}
        Data requirements: {data_requirements}
        Generate a complete table with appropriate headers and data rows.
        """,
        ),
    ]

    # Parse the JSON response
    try:
        table_data = struct_model.invoke(messages)
    except Exception:
        # If the response is not valid JSON, use default data
        table_data = TableContent(**{
            "headers": ["Column 1", "Column 2", "Column 3"],
            "rows": [
                ["Data 1", "Data 2", "Data 3"],
                ["Data 4", "Data 5", "Data 6"],
            ],
        })

    return table_data


@backoff.on_exception(
    backoff.expo,
    (openai.RateLimitError, anthropic.RateLimitError),
    max_tries=3,
    max_value=10,
)
def generate_chart_content(
    section: SectionStructure | SubsectionStructure, model: ChatAnthropic | ChatOpenAI
) -> ChartContent:
    """Generate chart content for a section"""
    struct_model = model.with_structured_output(ChartContent)

    data_requirements = (
        section.data_requirements
        if section.data_requirements
        else "No specific data requirements provided, use your judgment to create appropriate data."
    )

    messages = [
        (
            "system",
            """You are a data visualization expert.
        Create realistic data for a chart based on the requirements provided. The data will be used to generate a visualization.
        Your response must be a valid JSON object with this structure:
        {
            "chart_type": "bar|line|pie|scatter",
            "title": "Chart Title",
            "x_label": "X Axis Label",
            "y_label": "Y Axis Label",
            "categories": ["Category1", "Category2", ...],
            "values": [value1, value2, ...],
            "series": [                  // Optional, for multi-series charts
                {
                    "name": "Series1",
                    "values": [value1, value2, ...]
                },
                ...
            ]
        }
        Guidelines:
        - Choose an appropriate chart type for the data (bar, line, pie, scatter)
        - Create realistic, plausible data values
        - For time series, use realistic time periods
        - For categorical data, use descriptive category names
        - Include between 5-10 data points unless otherwise specified
        - For multi-series data, include 2-4 series with clear names
        """,
        ),
        (
            "human",
            f"""
        Section title: {section.title}
        Content requirements: {section.content_requirements}
        Data requirements: {data_requirements}
        Generate appropriate chart data.
        """,
        ),
    ]

    # Parse the JSON response
    try:
        chart_data = struct_model.invoke(messages)
    except Exception:
        # Create a default chart if parsing fails
        chart_data = ChartContent(**{
            "chart_type": "bar",
            "title": section.title,
            "x_label": "Categories",
            "y_label": "Values",
            "categories": ["Category A", "Category B", "Category C", "Category D"],
            "values": [23, 45, 56, 78],
        })

    # Handle the case where 'values' is missing but 'series' is present
    if not chart_data.values and chart_data.series:
        # Use the first series values as the main values
        chart_data.values = chart_data.series[0].values

    return chart_data


@backoff.on_exception(
    backoff.expo,
    (openai.RateLimitError, anthropic.RateLimitError),
    max_tries=3,
    max_value=10,
)
def generate_image_content(
    section: SectionStructure | SubsectionStructure, model: ChatAnthropic | ChatOpenAI
) -> ImageContent:
    """Generate image content description for a section"""
    struct_model = model.with_structured_output(ImageContent)
    messages = [
        (
            "system",
            """You are an image description specialist.
        Create a detailed description for an image based on the requirements provided.
        This description will be used to generate a placeholder image in the document.
        Guidelines:
        - Be specific and detailed about what the image should contain
        - Describe the composition, elements, and layout
        - Include any text that should appear in the image
        - Specify the style (e.g., photograph, illustration, diagram)
        - Keep your description clear and concise (100-200 words)
        """,
        ),
        (
            "human",
            f"""
        Section title: {section.title}
        Content requirements: {section.content_requirements}
        Generate a detailed image description.
        """,
        ),
    ]

    response = struct_model.invoke(messages)

    return response


@backoff.on_exception(
    backoff.expo,
    (openai.RateLimitError, anthropic.RateLimitError),
    max_tries=3,
    max_value=10,
)
def generate_complex_content(
    section: SectionStructure | SubsectionStructure, model: ChatAnthropic | ChatOpenAI
) -> ComplexContent:
    """Generate complex content with mixed text, tables, and charts"""
    arrangement = "vertical"  # Default arrangement
    if hasattr(section, "layout_properties") and hasattr(section.layout_properties, "arrangement"):
        arrangement = section.layout_properties.arrangement

    arrangement_instructions = f"The elements should be arranged {arrangement}ly in the layout."

    messages = [
        (
            "system",
            f"""You are a document design specialist who creates complex layouts.
        Create a detailed description of a complex section layout that combines multiple elements (text, tables, charts, images).
        {arrangement_instructions}
         Guidelines:
        - Describe how different elements should be arranged on the page
        - Specify the relationships between elements
        - Explain the flow of information across the layout
        - Include any specific formatting requirements
        - Be precise about positioning (e.g., "Table on the left, chart on the right")
        Then, provide a list of elements that should be included in this complex layout.
        Your response should be in this format:
        LAYOUT DESCRIPTION:
        [Your detailed layout description here]
        ELEMENTS:
        1. [Element type: text/table/chart/image] - [Brief description]
        2. [Element type: text/table/chart/image] - [Brief description]
        ...
        """,
        ),
        (
            "human",
            f"""
        Section title: {section.title}
        Content requirements: {section.content_requirements}
        Generate a detailed layout description and list of elements.
        """,
        ),
    ]

    response = model.invoke(messages)

    # Parse the response to extract layout description and elements
    layout_description = ""
    elements = []

    # Split by sections
    parts = response.content.split("ELEMENTS:")
    if len(parts) == 2:
        layout_description = parts[0].replace("LAYOUT DESCRIPTION:", "").strip()

        # Parse elements
        elements_text = parts[1].strip().split("\n")
        for element_text in elements_text:
            if not element_text.strip():
                continue

            # Try to extract element type
            element_type = "text"  # Default type
            if "text" in element_text.lower():
                element_type = "text"
            elif "table" in element_text.lower():
                element_type = "table"
            elif "chart" in element_text.lower() or "graph" in element_text.lower():
                element_type = "chart"
            elif "image" in element_text.lower() or "picture" in element_text.lower():
                element_type = "image"

            elements.append(ComplexElement(type=element_type, content=element_text.strip()))
    else:
        # If parsing fails, use the entire response as the layout description
        layout_description = response.content
        elements = [ComplexElement(type="text", content="This is placeholder text for a complex layout.")]

    # Include arrangement information in the layout description if not already mentioned
    if arrangement == "horizontal" and "horizontal" not in layout_description.lower():
        layout_description += "\n\nElements should be arranged horizontally."
    elif arrangement == "vertical" and "vertical" not in layout_description.lower():
        layout_description += "\n\nElements should be arranged vertically."

    return ComplexContent(layout_description=layout_description, elements=elements)


def content_generator_node(state: dict[str, Any]) -> dict[str, Any]:
    """
    Content generator node that creates content for a single section

    Args:
        state: The current state dictionary containing section info

    Returns:
        Updated state with generated content
    """
    section_info = state["section_info"]
    section = section_info["section"]
    model_name = state.get("content_model")

    # Create a content generator LLM
    model = get_content_llm(model_name)

    # Generate content based on section type
    if section.type == "text":
        content = generate_text_content(section, model)
    elif section.type == "table":
        content = generate_table_content(section, model)
    elif section.type == "chart":
        content = generate_chart_content(section, model)
    elif section.type == "image":
        content = generate_image_content(section, model)
    elif section.type == "complex":
        content = generate_complex_content(section, model)
    else:
        # Default to text content if type is unknown
        content = generate_text_content(section, model)

    # Create a section content object
    section_content = SectionContent(
        id=section.id,
        title=section.title,
        type=section.type,
        content=content,
        subsections=[],  # Subsections will be populated separately
    )

    return {"section_content": section_content, "section_path": section_info["path"]}


def content_reviewer_node(state: dict[str, Any]) -> dict[str, Any]:
    """
    Content reviewer node that reviews and improves generated content

    Args:
        state: The current state dictionary containing section content

    Returns:
        Updated state with reviewed content
    """
    section_content = state["section_content"]
    model_name = state.get("review_model")
    review_enabled = state.get("review_enabled", True)

    # Skip review if disabled
    if not review_enabled:
        return {"reviewed_section_content": section_content}

    # Create a review LLM
    model = get_review_llm(model_name)

    # Only review text content for now
    if section_content.type == "text":
        review_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """You are a content quality reviewer. Your task is to review the provided content and suggest improvements.
            Focus on:
            - Clarity and readability
            - Accuracy and relevance
            - Structure and organization
            - Grammar and style
            If the content is already high quality, simply confirm it's good.
            If it needs improvement, make specific suggestions.
            """,
            ),
            (
                "human",
                """
            Section title: {title}
            Content to review:
            {content}
            Please review this content and provide feedback.
            """,
            ),
        ])

        response = model.invoke(
            review_prompt.format_messages(content=section_content.content, title=section_content.title)
        )

        # Check if significant improvements are suggested
        if len(response.content) > 100 and any(
            keyword in response.content.lower() for keyword in ["improve", "change", "revise", "update", "issue"]
        ):
            # If improvements needed, generate new content
            improvement_prompt = ChatPromptTemplate.from_messages([
                (
                    "system",
                    """You are a professional content writer. Please rewrite the provided content based on the review feedback.
                Maintain the same general topic and purpose, but implement the suggested improvements.
                """,
                ),
                (
                    "human",
                    """
                Section title: {title}
                Original content:
                {content}
                Review feedback:
                {response_content}
                Please rewrite the content with these improvements.
                """,
                ),
            ])

            improved_response = model.invoke(
                improvement_prompt.format_messages(
                    content=section_content.content, title=section_content.title, response_content=response.content
                )
            )

            section_content.content = improved_response.content

    return {"reviewed_section_content": section_content}


def parallel_executor_node(state: dict[str, Any]) -> dict[str, Any]:
    """
    Node that executes content generation for multiple sections in parallel

    Args:
        state: The current state dictionary containing sections to process

    Returns:
        Updated state with all generated content
    """
    print(state)
    sections_to_process = state["sections_to_process"]
    model_name = state.get("content_model")
    max_workers = state.get("parallel_workers", 5)

    # Prepare the list to store results
    section_contents = []

    # Define a function to process a single section
    def process_section(section_info):
        try:
            model = get_content_llm(model_name)
            section = section_info["section"]

            # Generate content based on section type
            if section.type == "text":
                content = generate_text_content(section, model)
            elif section.type == "table":
                content = generate_table_content(section, model)
            elif section.type == "chart":
                content = generate_chart_content(section, model)
            elif section.type == "image":
                content = generate_image_content(section, model)
            elif section.type == "complex":
                content = generate_complex_content(section, model)
            else:
                # Default to text content if type is unknown
                content = generate_text_content(section, model)

            # Create a section content object
            section_content = SectionContent(
                id=section.id,
                title=section.title,
                type=section.type,
                content=content,
                subsections=[],  # Subsections will be populated separately
            )

            return {"section_content": section_content, "section_path": section_info["path"]}
        except Exception as e:
            # Handle errors and return fallback content
            return {
                "section_content": SectionContent(
                    id=section_info["section"].id,
                    title=section_info["section"].title,
                    type="text",
                    content=f"Error generating content: {e!s}",
                    subsections=[],
                ),
                "section_path": section_info["path"],
            }

    # Use ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all sections for processing
        future_to_section = {
            executor.submit(process_section, section_info): section_info for section_info in sections_to_process
        }

        # Collect results as they complete
        for future in future_to_section:
            try:
                result = future.result()
                section_contents.append(result)
            except Exception as e:
                # Handle errors in section processing (this should rarely happen due to error handling in process_section)
                section_info = future_to_section[future]
                print(f"Error processing section {section_info['section'].title}: {e!s}")

                # Create a fallback content for failed sections
                fallback_content = SectionContent(
                    id=section_info["section"].id,
                    title=section_info["section"].title,
                    type="text",
                    content=f"Error generating content: {e!s}",
                    subsections=[],
                )
                section_contents.append({"section_content": fallback_content, "section_path": section_info["path"]})

    return {"all_section_content": section_contents, **state}


def content_aggregator_node(state: dict[str, Any]) -> dict[str, Any]:
    """
    Aggregates all the generated content into a document structure

    Args:
        state: The current state dictionary containing all section content

    Returns:
        Updated state with aggregated document
    """
    print("Aggregating content...")
    doc_title = state.get("doc_title", "Generated Document Title")
    all_content = state["all_section_content"]

    # Create a document structure to hold all content
    document = {"title": doc_title, "sections": []}

    # Create a mapping from paths to content objects
    path_to_content = {}
    for content_item in all_content:
        path_to_content[content_item["section_path"]] = content_item["section_content"]

    # Function to recursively build the document structure
    def build_section_hierarchy(path_prefix, depth=0):
        # Find all sections at the current depth that match the prefix
        current_level_sections = []
        for path, content in path_to_content.items():
            parts = path.split("/")
            if len(parts) > depth and path.startswith(path_prefix) and len(parts) == depth + 1:
                # Check if this is a direct child of the current prefix
                current_level_sections.append((path, content))

        # Sort sections by their index in the path
        current_level_sections.sort(key=lambda x: int(x[0].split("/")[-1]))

        # Build the section list
        sections = []
        for path, content in current_level_sections:
            # Create a copy of the content with empty subsections
            section = SectionContent(
                id=content.id, title=content.title, type=content.type, content=content.content, subsections=[]
            )

            # Recursively add subsections
            section.subsections = build_section_hierarchy(path, depth + 1)

            sections.append(section)

        return sections

    # Build the entire document hierarchy
    document["sections"] = build_section_hierarchy("", 1)

    return {"document": document}
