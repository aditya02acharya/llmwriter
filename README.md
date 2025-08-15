# llmwriter

# LLMWriter: Synthetic PDF Document Generator

A GenAI tool for generating synthetic PDF documents based on user-defined requirements using langraph with a supervisory hierarchy of LLM calls.

- **Github repository**: <https://github.com/aditya02acharya/llmwriter/>

## Overview

This project creates complex PDF documents with a hierarchical approach:

1. **Supervisor LLM**: Analyzes requirements and designs document structure
2. **Content Generator LLMs**: Generate specific content for each section
3. **PDF Compiler**: Aggregates content and renders a professional PDF

The tool supports various content types:
- Text content
- Tables with structured data
- Charts and graphs
- Image descriptions
- Complex layouts combining multiple elements

## Features

- **Hierarchical LLM Orchestration**: Uses langraph to create a workflow of specialized LLMs
- **Parallel Content Generation**: Efficiently processes document sections in parallel
- **Content Review**: Reviews and improves content quality
- **Rich Document Features**: Supports tables, charts, images, and complex layouts
- **Extensible Architecture**: Easy to add new content types and generation methods

## Getting started with your project

### 1. Set Up Your Development Environment

Then, install the environment and the pre-commit hooks with

```bash
make install
```

This will also generate your `uv.lock` file

### 2. Set up API keys
#### Create a .env file with your API keys
```bash
echo "OPENAI_API_KEY=your_openai_api_key" > .env
echo "ANTHROPIC_API_KEY=your_anthropic_api_key" >> .env
```

## Usage

### Command Line Interface

The generator can be used via the command line interface:

```bash
# Generate a PDF using text requirements
python cli.py --requirements "Create a detailed report on renewable energy technologies including solar, wind, and hydroelectric power. Include comparison tables and trend charts."

# Generate a PDF using requirements from a file
python cli.py --requirements-file input.txt --output my_document.pdf

# Generate a PDF using a config file
python cli.py --config config.json
```

### Python API

You can also use the generator directly in your Python code:

```python
from pdf_generator import generate_pdf_document

# Define your document requirements
requirements = """
Create a comprehensive technical white paper titled "Next-Generation Neural Networks for Computer Vision"
that includes:

1. A detailed executive summary of the current state of neural networks in computer vision
2. Background on traditional computer vision approaches vs. deep learning
3. An in-depth analysis of at least 5 state-of-the-art neural network architectures for vision tasks
4. Performance comparison tables for these architectures across standard benchmarks
5. Visual representations of how each architecture processes image data
6. Case studies from at least 3 industries (healthcare, automotive, security)
7. Future research directions and challenges
8. A glossary of technical terms

The document should be highly technical but accessible to ML practitioners. Include appropriate
charts, tables, diagrams, and citations throughout.
"""

# Generate the PDF
pdf_path = generate_pdf_document(requirements, "neural_networks_whitepaper.pdf")
print(f"PDF document generated at: {pdf_path}")
```

## Project Structure

```
.
├── src/llmwriter/
│   ├── __init__.py
│   ├── generator.py      # Main implementation
│   ├── nodes/            # Langraph node implementations
│   │   ├── __init__.py
│   │   ├── supervisor.py
│   │   ├── content.py
│   │   └── renderer.py
│   ├── models/           # Data models
│   │   ├── __init__.py
│   │   └── structures.py
│   └── utils/            # Utility functions
│       ├── __init__.py
│       └── helpers.py
├── cli.py                # Command-line interface
├── config.json           # Example configuration
├── example_requirements/ # Example document requirements
│   └── technical_whitepaper.txt
└── README.md
```

## Configuration

You can configure the generator using a JSON configuration file:

```json
{
  "requirements": "Create a detailed report on renewable energy...",
  "output_path": "renewable_energy_report.pdf",
  "models": {
    "supervisor": "claude-3-opus-20240229",
    "content": "gpt-4-turbo",
    "review": "gpt-4-turbo"
  },
  "parallel_workers": 5,
  "review_enabled": true
}
```

## Example Document Requirements

Here are some example document requirements:

### Technical Whitepaper
```
Create a comprehensive technical white paper titled "Blockchain Technology in Supply Chain Management"
that includes:

1. Executive summary
2. Introduction to blockchain technology
3. Current challenges in supply chain management
4. How blockchain addresses these challenges
5. Implementation case studies
6. Cost-benefit analysis
7. Future outlook and recommendations

Include diagrams of blockchain architecture, comparison tables of different solutions,
and graphs showing adoption trends and performance metrics.
```

### Marketing Brochure
```
Create a marketing brochure for a luxury resort called "Azure Paradise"
that includes:

1. Cover page with resort name and tagline
2. Introduction to the resort and its location
3. Accommodation options with photos and pricing
4. Amenities and activities
5. Dining options
6. Special packages and promotions
7. Testimonials from past guests
8. Contact information and booking instructions

The brochure should have a luxurious feel with elegant typography,
high-quality images, and a sophisticated color scheme.
```

## Customization

The generator is designed to be easily customizable:

1. **Add New Content Types**: Extend the content generation functions in `content.py`
2. **Custom PDF Styling**: Modify the PDF rendering in `renderer.py`
3. **New LLM Providers**: Add new LLM providers in the `get_*_llm()` functions

## Evaluation

This tool is particularly well-suited for generating synthetic documents to evaluate PDF-to-markdown conversion processes, as it can create documents with:

- Complex nested structures
- Various content types (text, tables, charts)
- Different formatting styles
- Realistic content that mimics actual documents

## License

MIT License

---
