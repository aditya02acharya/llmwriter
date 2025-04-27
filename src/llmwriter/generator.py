import json
import os
from typing import Any, Optional

from langgraph.graph import END, START, Graph, StateGraph

from .nodes.content import content_aggregator_node, parallel_executor_node
from .nodes.renderer import pdf_renderer_node
from .nodes.supervisor import section_router_node, supervisor_node
from .utils.constants import DEFAULT_CONTENT_MODEL_ID, DEFAULT_SUPERVISOR_MODEL_ID


def load_config(config_path: Optional[str] = None) -> dict[str, Any]:
    """
    Load configuration from a JSON file or return default config

    Args:
        config_path: Path to a JSON configuration file

    Returns:
        Configuration dictionary
    """
    default_config = {
        "supervisor_model": DEFAULT_SUPERVISOR_MODEL_ID,
        "content_model": DEFAULT_CONTENT_MODEL_ID,
        "review_model": "o4-mini",
        "parallel_workers": 5,
        "review_enabled": False,
        "page_size": "A4",
        "color_theme": "professional",  # Default color theme
        "layout_style": "standard",  # Default layout style
        "advanced_layout": True,  # Enable advanced layout features
    }

    if not config_path:
        return default_config

    try:
        with open(config_path) as f:
            config = json.load(f)

        # Merge with default config to ensure all settings exist
        merged_config = default_config.copy()
        merged_config.update(config)
        return merged_config
    except Exception as e:
        print(f"Error loading config from {config_path}: {e!s}")
        return default_config


def build_document_generation_graph() -> Graph:
    """
    Build the document generation graph using langraph

    Returns:
        Compiled langraph graph
    """
    # Create a new graph
    graph = StateGraph(state_schema=dict)

    # Add nodes
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("section_router", section_router_node)
    graph.add_node("parallel_executor", parallel_executor_node)
    graph.add_node("content_aggregator", content_aggregator_node)
    graph.add_node("pdf_renderer", pdf_renderer_node)

    # Connect nodes
    graph.add_edge(START, "supervisor")
    graph.add_edge("supervisor", "section_router")
    graph.add_edge("section_router", "parallel_executor")
    graph.add_edge("parallel_executor", "content_aggregator")
    graph.add_edge("content_aggregator", "pdf_renderer")
    graph.add_edge("pdf_renderer", END)

    # Compile the graph
    compiled_graph = graph.compile()

    return compiled_graph


def generate_pdf_document(
    requirements: str,
    output_path: str = "generated_document.pdf",
    config_path: Optional[str] = None,
    color_theme: Optional[str] = None,
    layout_style: Optional[str] = None,
) -> str:
    """
    Generate a PDF document based on the given requirements

    Args:
        requirements: String containing document requirements
        output_path: Path where the PDF will be saved
        config_path: Path to a configuration file

    Returns:
        The path to the generated PDF
    """
    # Load configuration
    config = load_config(config_path)

    # Override config with explicit parameters if provided
    if color_theme:
        config["color_theme"] = color_theme
    if layout_style:
        config["layout_style"] = layout_style

    # Build the document generation graph
    graph = build_document_generation_graph()

    # Initialize the state with requirements and config
    initial_state = {"requirements": requirements, **config}

    # Execute the graph
    print("Generating document based on requirements...")
    result = graph.invoke(initial_state)

    # Save the PDF to a file
    with open(output_path, "wb") as f:
        f.write(result["pdf_data"])

    # Print styling information
    if "selected_theme" in result and "selected_layout" in result:
        print(f"Document styling: {result['selected_theme']} theme with {result['selected_layout']} layout")

    print(f"PDF document generated successfully at: {output_path}")
    return output_path


def generate_pdf_from_file(
    requirements_file: str, output_path: Optional[str] = None, config_path: Optional[str] = None
) -> str:
    """
    Generate a PDF document based on requirements from a file

    Args:
        requirements_file: Path to a file containing document requirements
        output_path: Path where the PDF will be saved
        config_path: Path to a configuration file

    Returns:
        The path to the generated PDF
    """
    # Read requirements from file
    with open(requirements_file) as f:
        requirements = f.read()

    # Generate output path if not provided
    if not output_path:
        base_name = os.path.splitext(os.path.basename(requirements_file))[0]
        output_path = f"{base_name}_generated.pdf"

    # Generate the PDF
    return generate_pdf_document(requirements, output_path, config_path)


def advanced_pdf_generation(
    requirements: str, output_path: str = "generated_document.pdf", config: Optional[dict[str, Any]] = None
) -> dict[str, Any]:
    """
    Advanced PDF generation with custom graph structure and configuration

    Args:
        requirements: String containing document requirements
        output_path: Path where the PDF will be saved
        config: Configuration dictionary

    Returns:
        Dictionary with generation results
    """
    # Use default config if none provided
    if config is None:
        config = load_config()

    # Build a custom graph with any special configurations
    graph = StateGraph(
        nodes=["supervisor", "section_router", "parallel_executor", "content_aggregator", "pdf_renderer"]
    )

    # Add nodes
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("section_router", section_router_node)
    graph.add_node("parallel_executor", parallel_executor_node)
    graph.add_node("content_aggregator", content_aggregator_node)
    graph.add_node("pdf_renderer", pdf_renderer_node)

    # Connect nodes
    graph.add_edge("supervisor", "section_router")
    graph.add_edge("section_router", "parallel_executor")
    graph.add_edge("parallel_executor", "content_aggregator")
    graph.add_edge("content_aggregator", "pdf_renderer")
    graph.add_edge("pdf_renderer", END)

    # Compile the graph
    compiled_graph = graph.compile()

    # Initialize the state with requirements and config
    initial_state = {"requirements": requirements, **config}

    # Execute the graph
    print("Generating document with advanced configuration...")
    result = compiled_graph.invoke(initial_state)

    # Save the PDF to a file
    with open(output_path, "wb") as f:
        f.write(result["pdf_data"])

    print(f"PDF document generated successfully at: {output_path}")

    # Return detailed results
    return {
        "output_path": output_path,
        "doc_title": result.get("doc_title", ""),
        "section_count": len(result.get("all_section_content", [])),
        "success": True,
    }


if __name__ == "__main__":
    # Example usage when running this module directly
    sample_requirements = """
    Create a visually appealing technical white paper titled "Next-Generation Neural Networks for Computer Vision"
    that includes:
    1. A detailed executive summary of the current state of neural networks in computer vision
    2. Background on traditional computer vision approaches vs. deep learning
    3. An in-depth analysis of at least 5 state-of-the-art neural network architectures for vision tasks
    4. Performance comparison tables for these architectures across standard benchmarks
    5. Visual representations of how each architecture processes image data
    6. Case studies from at least 3 industries (healthcare, automotive, security)
    7. Future research directions and challenges
    8. A glossary of technical terms
    The document should be highly technical but visually appealing with colored sections, highlighted key points,
    and a modern look and feel. Use a two-column layout where appropriate, and make sure to include
    colorful charts, boxed content for important information, and visually distinct tables.
    """

    # Generate with default styling
    pdf_path = generate_pdf_document(sample_requirements, "neural_networks_default.pdf")
    print(f"Sample PDF generated at: {pdf_path}")

    # Generate with creative styling
    pdf_path = generate_pdf_document(
        sample_requirements, "neural_networks_creative.pdf", color_theme="creative", layout_style="two_column"
    )
    print(f"Creative styled PDF generated at: {pdf_path}")

    # Generate with warm styling
    pdf_path = generate_pdf_document(
        sample_requirements, "neural_networks_warm.pdf", color_theme="warm", layout_style="modern"
    )
    print(f"Warm styled PDF generated at: {pdf_path}")
