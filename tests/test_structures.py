import pytest
from pydantic import ValidationError

from src.models.structures import (
    ChartContent,
    ChartSeries,
    ComplexContent,
    ComplexElement,
    DocumentStructure,
    ImageContent,
    SectionContent,
    SectionStructure,
    SubsectionStructure,
    TableContent,
)


def test_subsection_structure():
    subsection = SubsectionStructure(
        id="sub1",
        title="Subsection 1",
        type="text",
        content_requirements="Some requirements",
    )
    assert subsection.id == "sub1"
    assert subsection.title == "Subsection 1"
    assert subsection.type == "text"
    assert subsection.content_requirements == "Some requirements"
    assert subsection.data_requirements is None
    assert subsection.subsections == []


def test_section_structure():
    section = SectionStructure(
        id="sec1",
        title="Section 1",
        type="text",
        content_requirements="Some requirements",
        subsections=[
            SubsectionStructure(
                id="sub1",
                title="Subsection 1",
                type="text",
                content_requirements="Some requirements",
            )
        ],
    )
    assert section.id == "sec1"
    assert section.title == "Section 1"
    assert section.type == "text"
    assert len(section.subsections) == 1
    assert section.subsections[0].id == "sub1"


def test_document_structure():
    document = DocumentStructure(
        title="Document Title",
        sections=[
            SectionStructure(
                id="sec1",
                title="Section 1",
                type="text",
                content_requirements="Some requirements",
            )
        ],
    )
    assert document.title == "Document Title"
    assert len(document.sections) == 1
    assert document.sections[0].id == "sec1"


def test_table_content():
    table = TableContent(
        headers=["Column 1", "Column 2"],
        rows=[[1, 2], [3, 4]],
    )
    assert table.headers == ["Column 1", "Column 2"]
    assert table.rows == [[1, 2], [3, 4]]


def test_chart_content():
    chart = ChartContent(
        chart_type="bar",
        title="Chart Title",
        x_label="X Axis",
        y_label="Y Axis",
        categories=["A", "B", "C"],
        series=[
            ChartSeries(name="Series 1", values=[1.0, 2.0, 3.0]),
        ],
    )
    assert chart.chart_type == "bar"
    assert chart.title == "Chart Title"
    assert chart.x_label == "X Axis"
    assert chart.y_label == "Y Axis"
    assert chart.categories == ["A", "B", "C"]
    assert len(chart.series) == 1
    assert chart.series[0].name == "Series 1"


def test_image_content():
    image = ImageContent(
        description="An image",
        placeholder="image_placeholder",
    )
    assert image.description == "An image"
    assert image.placeholder == "image_placeholder"


def test_complex_content():
    complex_content = ComplexContent(
        layout_description="A layout",
        elements=[
            ComplexElement(type="text", content="Some text"),
            ComplexElement(type="image", content={"url": "image_url"}),
        ],
    )
    assert complex_content.layout_description == "A layout"
    assert len(complex_content.elements) == 2
    assert complex_content.elements[0].type == "text"
    assert complex_content.elements[1].type == "image"


def test_section_content():
    section_content = SectionContent(
        id="sec1",
        title="Section Content 1",
        type="text",
        content="Some content",
        subsections=[
            SectionContent(
                id="sub1",
                title="Subsection Content 1",
                type="text",
                content="Subcontent",
            )
        ],
    )
    assert section_content.id == "sec1"
    assert section_content.title == "Section Content 1"
    assert len(section_content.subsections) == 1
    assert section_content.subsections[0].id == "sub1"


def test_invalid_subsection_structure():
    with pytest.raises(ValidationError):
        SubsectionStructure(
            id="sub1",
            title="Subsection 1",
            type="text",
            content_requirements=None,  # Invalid: content_requirements is required
        )
