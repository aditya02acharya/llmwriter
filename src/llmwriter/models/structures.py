# src/models/structures.py
from typing import Any, Optional

from pydantic import BaseModel


class SubsectionStructure(BaseModel):
    id: str
    title: str
    type: str
    content_requirements: str
    data_requirements: Optional[str] = None
    subsections: list["SubsectionStructure"] = []


class SectionStructure(BaseModel):
    id: str
    title: str
    type: str
    content_requirements: str
    data_requirements: Optional[str] = None
    subsections: list[SubsectionStructure] = []


class DocumentStructure(BaseModel):
    title: str
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
    subsections: list["SectionContent"] = []


# Initialize circular references
SubsectionStructure.model_rebuild()
SectionContent.model_rebuild()
