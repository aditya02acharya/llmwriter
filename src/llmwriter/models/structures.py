# src/models/structures.py
from typing import Any, Literal, Optional

from pydantic import BaseModel


class LayoutProperties(BaseModel):
    """Layout properties for a section"""

    arrangement: Optional[Literal["vertical", "horizontal"]] = "vertical"  # 'horizontal' or 'vertical'
    highlight_key_points: Optional[bool] = False
    use_boxed_content: Optional[bool] = False


class StylePreferences(BaseModel):
    """Style preferences for the entire document"""

    color_theme: Optional[Literal["professional", "creative", "modern", "warm", "minimal"]] = (
        "professional"  # 'professional', 'creative', 'modern', 'warm', 'minimal'
    )
    layout_style: Optional[Literal["standard", "modern", "wide", "two_column", "compact"]] = (
        "standard"  # 'standard', 'modern', 'wide', 'two_column', 'compact'
    )
    visual_notes: Optional[str] = None


class SubsectionStructure(BaseModel):
    id: str
    title: str
    type: str
    content_requirements: str
    data_requirements: Optional[str] = None
    layout_properties: Optional[LayoutProperties] = None
    subsections: list["SubsectionStructure"] = []


class SectionStructure(BaseModel):
    id: str
    title: str
    type: str
    content_requirements: str
    data_requirements: Optional[str] = None
    layout_properties: Optional[LayoutProperties] = None
    subsections: list[SubsectionStructure] = []


class DocumentStructure(BaseModel):
    title: str
    style_preferences: Optional[StylePreferences] = None
    sections: list[SectionStructure]


class TableContent(BaseModel):
    headers: list[str]
    rows: list[list[Any]]


class ChartSeries(BaseModel):
    name: str
    values: list[float]


class ChartContent(BaseModel):
    chart_type: str
    title: str
    x_label: str
    y_label: str
    categories: list[str]
    values: Optional[list[float]] = None
    series: Optional[list[ChartSeries]] = None


class ImageContent(BaseModel):
    description: str
    placeholder: str


class ComplexElement(BaseModel):
    type: str
    content: Any


class ComplexContent(BaseModel):
    layout_description: str
    elements: list[ComplexElement]


class SectionContent(BaseModel):
    id: str
    title: str
    type: str
    content: Any
    layout_properties: Optional[LayoutProperties] = None
    subsections: list["SectionContent"] = []


# Initialize circular references
SubsectionStructure.model_rebuild()
SectionContent.model_rebuild()
