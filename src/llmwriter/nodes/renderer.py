import io
from typing import Any, Optional

import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("Agg")  # Use non-interactive backend
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Flowable,
    Frame,
    Image,
    PageBreak,
    PageTemplate,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
)

# Define preset color themes
COLOR_THEMES = {
    "professional": {
        "primary": colors.HexColor("#003366"),  # Deep blue
        "secondary": colors.HexColor("#4D88FF"),  # Medium blue
        "accent": colors.HexColor("#FF9900"),  # Orange
        "background": colors.HexColor("#F5F5F5"),  # Light gray
        "text": colors.HexColor("#333333"),  # Dark gray
        "heading": colors.HexColor("#003366"),  # Deep blue
        "table_header": colors.HexColor("#E6F0FF"),  # Light blue
        "table_odd": colors.HexColor("#F9F9F9"),  # Very light gray
        "table_even": colors.white,
    },
    "creative": {
        "primary": colors.HexColor("#6200EA"),  # Deep purple
        "secondary": colors.HexColor("#B388FF"),  # Light purple
        "accent": colors.HexColor("#00E676"),  # Green
        "background": colors.HexColor("#FFFFFF"),  # White
        "text": colors.HexColor("#424242"),  # Dark gray
        "heading": colors.HexColor("#6200EA"),  # Deep purple
        "table_header": colors.HexColor("#EDE7F6"),  # Very light purple
        "table_odd": colors.HexColor("#F3F3F3"),  # Light gray
        "table_even": colors.white,
    },
    "modern": {
        "primary": colors.HexColor("#546E7A"),  # Blue gray
        "secondary": colors.HexColor("#90A4AE"),  # Light blue gray
        "accent": colors.HexColor("#26A69A"),  # Teal
        "background": colors.HexColor("#ECEFF1"),  # Very light blue gray
        "text": colors.HexColor("#37474F"),  # Dark blue gray
        "heading": colors.HexColor("#455A64"),  # Medium blue gray
        "table_header": colors.HexColor("#CFD8DC"),  # Light blue gray
        "table_odd": colors.HexColor("#FAFAFA"),  # Off white
        "table_even": colors.white,
    },
    "warm": {
        "primary": colors.HexColor("#D84315"),  # Deep orange
        "secondary": colors.HexColor("#FFAB91"),  # Light orange
        "accent": colors.HexColor("#FFC107"),  # Amber
        "background": colors.HexColor("#FFF3E0"),  # Very light orange
        "text": colors.HexColor("#5D4037"),  # Brown
        "heading": colors.HexColor("#BF360C"),  # Dark orange
        "table_header": colors.HexColor("#FFCCBC"),  # Very light orange
        "table_odd": colors.HexColor("#FFF8E1"),  # Very light amber
        "table_even": colors.white,
    },
    "minimal": {
        "primary": colors.HexColor("#212121"),  # Very dark gray
        "secondary": colors.HexColor("#757575"),  # Medium gray
        "accent": colors.HexColor("#2196F3"),  # Blue
        "background": colors.HexColor("#FFFFFF"),  # White
        "text": colors.HexColor("#212121"),  # Very dark gray
        "heading": colors.HexColor("#212121"),  # Very dark gray
        "table_header": colors.HexColor("#EEEEEE"),  # Light gray
        "table_odd": colors.HexColor("#FAFAFA"),  # Very light gray
        "table_even": colors.white,
    },
}

# Define layout styles
LAYOUT_STYLES = {
    "standard": {
        "margins": (72, 72, 72, 72),  # (left, right, top, bottom)
        "columns": 1,
        "header_height": 0.5 * inch,
        "footer_height": 0.5 * inch,
        "spacing": 0.2 * inch,
    },
    "modern": {
        "margins": (90, 90, 72, 72),
        "columns": 1,
        "header_height": 0.75 * inch,
        "footer_height": 0.6 * inch,
        "spacing": 0.25 * inch,
    },
    "wide": {
        "margins": (54, 54, 72, 72),
        "columns": 1,
        "header_height": 0.5 * inch,
        "footer_height": 0.5 * inch,
        "spacing": 0.2 * inch,
    },
    "two_column": {
        "margins": (54, 54, 72, 72),
        "columns": 2,
        "header_height": 0.5 * inch,
        "footer_height": 0.5 * inch,
        "spacing": 0.3 * inch,
        "column_gap": 0.4 * inch,
    },
    "compact": {
        "margins": (45, 45, 45, 45),
        "columns": 1,
        "header_height": 0.4 * inch,
        "footer_height": 0.4 * inch,
        "spacing": 0.15 * inch,
    },
}


# Create a boxed content flowable
class BoxedContent(Flowable):
    """
    A flowable that renders its content in a box with a background color,
    optional border, rounded corners, and drop shadow.
    """

    def __init__(
        self,
        content_flowables: list[Flowable],
        padding: int = 10,
        background_color: colors.Color = colors.white,
        border_color: colors.Color = None,
        border_width: int = 1,
        corner_radius: int = 5,
        drop_shadow: bool = False,
        width: Optional[int] = None,
    ):
        super().__init__()
        self.content_flowables = content_flowables
        self.padding = padding
        self.background_color = background_color
        self.border_color = border_color
        self.border_width = border_width
        self.corner_radius = corner_radius
        self.drop_shadow = drop_shadow
        self.width = width
        self._height = 0
        self._width = 0

    def wrap(self, available_width: int, available_height: int) -> tuple[int, int]:
        if self.width:
            content_width = min(self.width, available_width) - 2 * self.padding
        else:
            content_width = available_width - 2 * self.padding

        content_height = 0
        for flowable in self.content_flowables:
            w, h = flowable.wrap(content_width, available_height - content_height)
            content_height += h

        self._width = content_width + 2 * self.padding
        self._height = content_height + 2 * self.padding

        # Handle drop shadow (makes it slightly larger)
        if self.drop_shadow:
            self._height += 3
            self._width += 3

        return self._width, self._height

    def draw(self):
        canvas = self.canv

        # Draw drop shadow if requested
        if self.drop_shadow:
            canvas.setFillColor(colors.HexColor("#CCCCCC"))
            canvas.roundRect(3, 0, self._width - 3, self._height - 3, self.corner_radius, fill=1, stroke=0)

        # Draw background
        canvas.setFillColor(self.background_color)
        canvas.roundRect(
            0,
            3,
            self._width - (3 if self.drop_shadow else 0),
            self._height - (3 if self.drop_shadow else 0),
            self.corner_radius,
            fill=1,
            stroke=0,
        )

        # Draw border if requested
        if self.border_color:
            canvas.setStrokeColor(self.border_color)
            canvas.setLineWidth(self.border_width)
            canvas.roundRect(
                0,
                3,
                self._width - (3 if self.drop_shadow else 0),
                self._height - (3 if self.drop_shadow else 0),
                self.corner_radius,
                fill=0,
                stroke=1,
            )

        # Draw content
        canvas.saveState()
        y = self._height - self.padding
        x = self.padding
        for flowable in self.content_flowables:
            flowable_width, flowable_height = flowable.wrap(
                self._width - 2 * self.padding, self._height - 2 * self.padding
            )
            y -= flowable_height
            flowable.drawOn(canvas, x, y)
            y -= 0  # No extra space between flowables
        canvas.restoreState()


class HorizontalLayout(Flowable):
    """
    A flowable that arranges multiple flowables horizontally,
    with specified spacing and alignment.
    """

    def __init__(
        self,
        flowables: list[Flowable],
        spacing: int = 10,
        alignment: str = "center",
        padding: int = 0,
        background_color: Optional[colors.Color] = None,
        border_color: Optional[colors.Color] = None,
    ):
        super().__init__()
        self.flowables = flowables
        self.spacing = spacing
        self.alignment = alignment  # 'left', 'center', 'right'
        self.padding = padding
        self.background_color = background_color
        self.border_color = border_color
        self._width = 0
        self._height = 0

    def wrap(self, available_width: int, available_height: int) -> tuple[int, int]:
        content_width = 0
        max_height = 0

        # First, wrap each flowable
        wrapped_sizes = []
        for flowable in self.flowables:
            w, h = flowable.wrap(available_width / len(self.flowables) - self.spacing, available_height)
            wrapped_sizes.append((w, h))
            content_width += w
            max_height = max(max_height, h)

        # Add spacing between flowables
        content_width += self.spacing * (len(self.flowables) - 1)

        # Add padding
        self._width = content_width + 2 * self.padding
        self._height = max_height + 2 * self.padding

        # Store wrapped sizes for later
        self._wrapped_sizes = wrapped_sizes

        return self._width, self._height

    def draw(self):
        canvas = self.canv

        # Draw background if needed
        if self.background_color:
            canvas.setFillColor(self.background_color)
            canvas.rect(0, 0, self._width, self._height, fill=1, stroke=0)

        # Draw border if needed
        if self.border_color:
            canvas.setStrokeColor(self.border_color)
            canvas.rect(0, 0, self._width, self._height, fill=0, stroke=1)

        # Determine starting x position based on alignment
        x = self.padding

        # Draw each flowable
        canvas.saveState()
        for i, flowable in enumerate(self.flowables):
            flowable_width, flowable_height = self._wrapped_sizes[i]

            # Center vertically
            y = (self._height - flowable_height) / 2

            flowable.drawOn(canvas, x, y)
            x += flowable_width + self.spacing

        canvas.restoreState()


def select_theme(state: dict[str, Any]) -> dict[str, Any]:
    """
    Select a color theme and layout style based on state preferences or defaults

    Args:
        state: The current state dictionary

    Returns:
        Updated state with selected theme and layout style
    """
    # Check if style preferences are already defined by the supervisor
    if state.get("style_preferences"):
        prefs = state["style_preferences"]

        # Handle both dictionary and object formats
        if isinstance(prefs, dict):
            # Get theme from style preferences dictionary
            if "color_theme" in prefs and prefs["color_theme"] in COLOR_THEMES:
                theme_name = prefs["color_theme"]
            else:
                # Default or fallback theme
                theme_name = state.get("color_theme", "professional")

            # Get layout style from style preferences dictionary
            if "layout_style" in prefs and prefs["layout_style"] in LAYOUT_STYLES:
                layout_style = prefs["layout_style"]
            else:
                # Default or fallback layout
                layout_style = state.get("layout_style", "standard")
        else:
            # Handle object format (for Pydantic models)
            # Get theme from style preferences object
            if hasattr(prefs, "color_theme") and prefs.color_theme in COLOR_THEMES:
                theme_name = prefs.color_theme
            else:
                # Default or fallback theme
                theme_name = state.get("color_theme", "professional")

            # Get layout style from style preferences object
            if hasattr(prefs, "layout_style") and prefs.layout_style in LAYOUT_STYLES:
                layout_style = prefs.layout_style
            else:
                # Default or fallback layout
                layout_style = state.get("layout_style", "standard")
    else:
        # Use configuration defaults if no LLM-provided preferences
        theme_name = state.get("color_theme", "professional")
        layout_style = state.get("layout_style", "standard")

    # Update state
    state["selected_theme"] = theme_name
    state["selected_layout"] = layout_style
    state["color_theme"] = COLOR_THEMES[theme_name]
    state["layout_style"] = LAYOUT_STYLES[layout_style]

    return state


def create_pdf_styles(color_theme: Optional[dict[str, colors.Color]] = None) -> dict[str, ParagraphStyle]:
    """Create and return custom styles for the PDF document with colors from the theme"""
    styles = getSampleStyleSheet()

    if color_theme is None:
        color_theme = COLOR_THEMES["professional"]  # Default theme

    # Add custom styles with theme colors
    styles.add(
        ParagraphStyle(
            name="Heading1",
            parent=styles["Heading1"],
            fontSize=16,
            spaceAfter=12,
            textColor=color_theme["heading"],
            fontName="Helvetica-Bold",
        )
    )
    styles.add(
        ParagraphStyle(
            name="Heading2",
            parent=styles["Heading2"],
            fontSize=14,
            spaceAfter=10,
            textColor=color_theme["heading"],
            fontName="Helvetica-Bold",
        )
    )
    styles.add(
        ParagraphStyle(
            name="Heading3",
            parent=styles["Heading3"],
            fontSize=12,
            spaceAfter=8,
            textColor=color_theme["heading"],
            fontName="Helvetica-Bold",
        )
    )
    styles.add(
        ParagraphStyle(name="Normal", parent=styles["Normal"], fontSize=10, leading=14, textColor=color_theme["text"])
    )
    styles.add(
        ParagraphStyle(name="Italic", parent=styles["Italic"], fontSize=10, leading=14, textColor=color_theme["text"])
    )
    styles.add(
        ParagraphStyle(
            name="Caption",
            parent=styles["Italic"],
            fontSize=9,
            leading=12,
            alignment=1,  # Center alignment
            textColor=color_theme["secondary"],
        )
    )
    styles.add(
        ParagraphStyle(
            name="BoxHeading",
            parent=styles["Heading3"],
            fontSize=12,
            textColor=colors.white,
            backColor=color_theme["primary"],
            borderPadding=(5, 5, 3, 8),  # (top, right, bottom, left)
        )
    )
    styles.add(
        ParagraphStyle(
            name="BoxContent",
            parent=styles["Normal"],
            fontSize=10,
            leading=14,
            textColor=color_theme["text"],
            borderPadding=(5, 5, 5, 5),
        )
    )
    styles.add(
        ParagraphStyle(
            name="Highlight",
            parent=styles["Normal"],
            fontSize=10,
            leading=14,
            textColor=color_theme["primary"],
            backColor=colors.HexColor("#FFFFCC"),  # Light yellow highlight
        )
    )
    styles.add(
        ParagraphStyle(
            name="Quote",
            parent=styles["Normal"],
            fontSize=10,
            leading=14,
            leftIndent=36,
            rightIndent=36,
            italics=True,
            textColor=color_theme["secondary"],
        )
    )

    return styles


def process_text_content(
    content: str,
    styles: dict[str, ParagraphStyle],
    color_theme: Optional[dict[str, colors.Color]] = None,
    add_styling: bool = True,
) -> list[Flowable]:
    """Process text content and return a list of flowable elements"""
    elements: list[Flowable] = []

    if not color_theme:
        color_theme = COLOR_THEMES["professional"]

    # Split content into paragraphs
    paragraphs: list[str] = content.split("\n\n")

    # Track if we should create a highlight box
    highlight_box_content: list[Flowable] = []
    in_highlight_section: bool = False

    for para in paragraphs:
        if not para.strip():
            continue

        # Check if it's a heading
        if para.strip().startswith("# "):
            if in_highlight_section and highlight_box_content:
                # Add the previous highlight box
                elements.append(create_highlight_box(highlight_box_content, styles, color_theme))
                highlight_box_content = []
                in_highlight_section = False

            p = Paragraph(para.strip()[2:], styles["Heading2"])
            elements.append(p)

        elif para.strip().startswith("## "):
            if in_highlight_section and highlight_box_content:
                # Add the previous highlight box
                elements.append(create_highlight_box(highlight_box_content, styles, color_theme))
                highlight_box_content = []
                in_highlight_section = False

            p = Paragraph(para.strip()[3:], styles["Heading3"])
            elements.append(p)

        elif para.strip().startswith("> ") and add_styling:
            # This is a blockquote
            quote_text = para.strip()[2:]
            p = Paragraph(quote_text, styles["Quote"])
            elements.append(p)
            elements.append(Spacer(1, 6))

        elif para.strip().startswith("**KEY POINT**") and add_styling:
            # Start a highlight section
            in_highlight_section = True
            # Add the key point title to the highlight content
            point_text = para.strip().replace("**KEY POINT**", "").strip()
            if point_text:
                highlight_box_content.append(Paragraph(point_text, styles["BoxContent"]))

        elif in_highlight_section and add_styling:
            # Continue adding to the highlight box
            highlight_box_content.append(Paragraph(para.strip(), styles["BoxContent"]))

        else:
            if in_highlight_section and highlight_box_content and add_styling:
                # End of highlight section, add the box
                elements.append(create_highlight_box(highlight_box_content, styles, color_theme))
                highlight_box_content = []
                in_highlight_section = False

            # Regular paragraph
            p = Paragraph(para.strip(), styles["Normal"])
            elements.append(p)
            elements.append(Spacer(1, 6))

    # Check if we still have an open highlight section
    if in_highlight_section and highlight_box_content and add_styling:
        elements.append(create_highlight_box(highlight_box_content, styles, color_theme))

    return elements


def create_highlight_box(
    content_elements: list[Flowable], styles: dict[str, ParagraphStyle], color_theme: dict[str, colors.Color]
) -> BoxedContent:
    """Create a highlighted box with the given content"""
    return BoxedContent(
        content_elements,
        padding=10,
        background_color=colors.HexColor("#F5F9FF"),  # Very light blue
        border_color=color_theme["secondary"],
        border_width=1,
        corner_radius=5,
        drop_shadow=True,
    )


def process_table_content(
    table_data: Any, styles: dict[str, ParagraphStyle], color_theme: Optional[dict[str, colors.Color]] = None
) -> list[Flowable]:
    """Process table content and return a list of flowable elements"""
    elements: list[Flowable] = []

    if not color_theme:
        color_theme = COLOR_THEMES["professional"]

    # Create table with headers
    table_content: list[list[Any]] = [table_data.headers]
    # Add rows
    table_content.extend(table_data.rows)

    # Create the table
    if table_content and all(table_content):
        # Check if all rows have the same number of columns
        num_cols = len(table_content[0])
        for row in table_content:
            if len(row) != num_cols:
                # Pad shorter rows
                row.extend([""] * (num_cols - len(row)))

        table = Table(table_content)

        # Enhanced table styling with theme colors
        style = [
            # Header styling
            ("BACKGROUND", (0, 0), (-1, 0), color_theme["table_header"]),
            ("TEXTCOLOR", (0, 0), (-1, 0), color_theme["primary"]),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),  # Center headers
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            # Alternating row colors
            ("BACKGROUND", (0, 1), (-1, -1), color_theme["table_even"]),
            ("TEXTCOLOR", (0, 1), (-1, -1), color_theme["text"]),
            # Grid styling
            ("GRID", (0, 0), (-1, -1), 0.5, color_theme["secondary"]),
            ("BOX", (0, 0), (-1, -1), 1, color_theme["primary"]),
            # Padding
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ]

        # Add zebra striping for odd rows
        for row_idx in range(1, len(table_content), 2):
            style.append(("BACKGROUND", (0, row_idx), (-1, row_idx), color_theme["table_odd"]))

        # Check for numeric columns and right-align them
        if len(table_content) > 1:
            for col_idx in range(len(table_content[0])):
                # Check if column contains numeric data (except header)
                is_numeric = True
                for row_idx in range(1, len(table_content)):
                    cell_value = table_content[row_idx][col_idx]
                    if not (
                        isinstance(cell_value, (int, float))
                        or (isinstance(cell_value, str) and cell_value.replace(".", "", 1).isdigit())
                    ):
                        is_numeric = False
                        break

                if is_numeric:
                    style.append(("ALIGN", (col_idx, 1), (col_idx, -1), "RIGHT"))

        table.setStyle(style)

        # Wrap table in a BoxedContent for better visual appeal
        boxed_table = BoxedContent(
            [table],
            padding=5,
            background_color=colors.white,
            border_color=color_theme["secondary"],
            border_width=0.5,
            corner_radius=3,
            drop_shadow=True,
        )

        elements.append(boxed_table)

        # Add caption if available
        if hasattr(table_data, "caption"):
            caption = Paragraph(f"Table: {table_data.caption}", styles["Caption"])
            elements.append(caption)

        elements.append(Spacer(1, 15))

    return elements


def process_chart_content(
    chart_data: Any, styles: dict[str, ParagraphStyle], color_theme: Optional[dict[str, colors.Color]] = None
) -> list[Flowable]:
    """Process chart content and return a list of flowable elements"""
    elements: list[Flowable] = []

    if not color_theme:
        color_theme = COLOR_THEMES["professional"]

    # Set matplotlib style based on the theme
    plt.style.use("seaborn-v0_8-whitegrid")

    # Create a chart using matplotlib with theme colors
    plt.figure(figsize=(7, 4.5))

    # Extract colors for the chart
    primary_color = f"#{color_theme['primary'].hexval()[2:]}"
    secondary_color = f"#{color_theme['secondary'].hexval()[2:]}"
    accent_color = f"#{color_theme['accent'].hexval()[2:]}"

    # Create a color palette
    color_palette = [primary_color, secondary_color, accent_color]
    if chart_data.chart_type == "pie" and len(chart_data.categories) > 3:
        # Generate more colors for pie charts with many categories
        import matplotlib.cm as cm

        color_palette = cm.get_cmap("tab10", len(chart_data.categories))
        color_palette = [matplotlib.colors.rgb2hex(color_palette(i)) for i in range(len(chart_data.categories))]

    try:
        if chart_data.chart_type == "bar":
            plt.bar(
                chart_data.categories, chart_data.values, color=color_palette[0], alpha=0.8, edgecolor=primary_color
            )

            # Add data values on top of the bars
            for i, v in enumerate(chart_data.values):
                plt.text(i, v + max(chart_data.values) * 0.02, f"{v:,}", ha="center", fontsize=8, color=primary_color)

        elif chart_data.chart_type == "line":
            plt.plot(
                chart_data.categories, chart_data.values, marker="o", color=primary_color, linewidth=2, markersize=6
            )

            # Add a subtle filling below the line
            plt.fill_between(chart_data.categories, chart_data.values, alpha=0.1, color=primary_color)

        elif chart_data.chart_type == "pie":
            wedges, texts, autotexts = plt.pie(
                chart_data.values,
                labels=chart_data.categories,
                autopct="%1.1f%%",
                colors=color_palette,
                startangle=90,
                shadow=False,
                wedgeprops={"edgecolor": "white", "linewidth": 1.5},
            )

            # Styling for pie chart text
            for autotext in autotexts:
                autotext.set_color("white")
                autotext.set_fontsize(9)

        elif chart_data.chart_type == "scatter":
            # For scatter, handle differently based on series
            if chart_data.series:
                for i, series in enumerate(chart_data.series):
                    plt.scatter(
                        chart_data.categories,
                        series.values,
                        label=series.name,
                        color=color_palette[i % len(color_palette)],
                        s=50,
                        alpha=0.7,
                        edgecolor="white",
                    )
                plt.legend(frameon=True, facecolor="white", framealpha=0.9)
            else:
                plt.scatter(
                    chart_data.categories, chart_data.values, color=primary_color, s=50, alpha=0.7, edgecolor="white"
                )

        # Add title and labels with theme styling
        plt.title(chart_data.title, fontsize=14, color=primary_color, fontweight="bold", pad=15)
        plt.xlabel(chart_data.x_label, fontsize=11, color=secondary_color, labelpad=10)
        plt.ylabel(chart_data.y_label, fontsize=11, color=secondary_color, labelpad=10)

        # Style the grid and axes
        plt.grid(True, linestyle="--", alpha=0.7, color="#E0E0E0")
        plt.tick_params(colors=color_theme["text"].hexval()[2:])

        # Set background color
        plt.gca().set_facecolor("#FAFAFA")
        plt.gcf().set_facecolor("#FFFFFF")

        # Add a subtle border around the plot
        plt.gca().spines["top"].set_visible(False)
        plt.gca().spines["right"].set_visible(False)
        plt.gca().spines["bottom"].set_color("#DDDDDD")
        plt.gca().spines["left"].set_color("#DDDDDD")

        plt.tight_layout()

        # Save the chart to a buffer
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format="png", dpi=300, bbox_inches="tight")
        img_buffer.seek(0)

        # Create a PIL Image and get dimensions
        img = PILImage.open(img_buffer)
        width, height = img.size

        # Scale the image to fit within the document
        max_width = 450  # Maximum width in points
        if width > max_width:
            ratio = max_width / width
            width = max_width
            height = height * ratio

        # Add the image to the PDF
        img_data = img_buffer.getvalue()
        img = Image(io.BytesIO(img_data), width=width, height=height)

        # Create a boxed container for the chart
        chart_box = BoxedContent(
            [img],
            padding=10,
            background_color=colors.white,
            border_color=color_theme["secondary"],
            border_width=0.5,
            corner_radius=5,
            drop_shadow=True,
        )

        elements.append(chart_box)

        # Add caption
        caption = Paragraph(f"Figure: {chart_data.title}", styles["Caption"])
        elements.append(caption)
        elements.append(Spacer(1, 15))

        # Close the matplotlib figure
        plt.close()

    except Exception as e:
        # Handle chart creation errors
        error_text = Paragraph(f"Error creating chart: {e!s}", styles["Italic"])
        elements.append(error_text)
        elements.append(Spacer(1, 10))

    return elements


def process_image_content(
    image_content: Any, styles: dict[str, ParagraphStyle], color_theme: Optional[dict[str, colors.Color]] = None
) -> list[Flowable]:
    """Process image content and return a list of flowable elements"""
    elements: list[Flowable] = []

    if not color_theme:
        color_theme = COLOR_THEMES["professional"]

    # Create a visually appealing placeholder for the image
    image_desc_elements: list[Flowable] = []

    # Add a title for the image
    if ":" in image_content.description and len(image_content.description.split(":")[0]) < 50:
        # Split into title and description if there's a colon
        title, desc = image_content.description.split(":", 1)
        image_title = Paragraph(f"<b>{title.strip()}</b>", styles["BoxHeading"])
        image_desc_elements.append(image_title)
        image_desc = Paragraph(desc.strip(), styles["BoxContent"])
        image_desc_elements.append(image_desc)
    else:
        # Use the whole text as description
        image_desc = Paragraph(image_content.description, styles["BoxContent"])
        image_desc_elements.append(image_desc)

    # Create a styled box for the image placeholder
    image_box = BoxedContent(
        image_desc_elements,
        padding=15,
        background_color=colors.HexColor("#F5F5F5"),  # Light gray background
        border_color=color_theme["secondary"],
        border_width=1,
        corner_radius=8,
        drop_shadow=True,
    )

    elements.append(image_box)
    elements.append(Spacer(1, 15))

    return elements


def process_complex_content(
    complex_content: Any, styles: dict[str, ParagraphStyle], color_theme: Optional[dict[str, colors.Color]] = None
) -> list[Flowable]:
    """Process complex content and return a list of flowable elements"""
    elements: list[Flowable] = []

    if not color_theme:
        color_theme = COLOR_THEMES["professional"]

    # Determine if this should be a horizontal or vertical layout
    is_horizontal = (
        "horizontal" in complex_content.layout_description.lower()
        or "side by side" in complex_content.layout_description.lower()
        or "row" in complex_content.layout_description.lower()
    )

    # If it's horizontal and has 2-3 elements, create a horizontal layout
    if is_horizontal and 2 <= len(complex_content.elements) <= 3:
        # Process each element separately
        horizontal_elements: list[Flowable] = []

        for element in complex_content.elements:
            if element.type == "text":
                # Process text content
                text_content = str(element.content)
                text_flowables = process_text_content(text_content, styles, color_theme, add_styling=False)

                # Create a box for the text content
                text_box = BoxedContent(
                    text_flowables,
                    padding=10,
                    background_color=colors.white,
                    border_color=color_theme["secondary"],
                    border_width=0.5,
                    corner_radius=5,
                )
                horizontal_elements.append(text_box)

            elif element.type in ["table", "chart", "image"]:
                # Create a placeholder for non-text elements
                placeholder_text = Paragraph(f"[{element.type.capitalize()}: {element.content}]", styles["Italic"])
                placeholder_box = BoxedContent(
                    [placeholder_text],
                    padding=10,
                    background_color=colors.HexColor("#F9F9F9"),
                    border_color=color_theme["secondary"],
                    border_width=0.5,
                    corner_radius=5,
                )
                horizontal_elements.append(placeholder_box)

        # Create horizontal layout
        layout_desc = Paragraph(complex_content.layout_description, styles["Normal"])
        elements.append(layout_desc)
        elements.append(Spacer(1, 10))

        # Add horizontal layout with elements
        elements.append(HorizontalLayout(horizontal_elements, spacing=15, alignment="center", padding=0))

    else:
        # For vertical layout or complex layouts with many elements, use standard approach

        # Add the layout description
        layout_desc = Paragraph(complex_content.layout_description, styles["Normal"])
        elements.append(layout_desc)
        elements.append(Spacer(1, 10))

        # Add elements based on their types with styling
        for element in complex_content.elements:
            if element.type == "text":
                # Process text with styling
                text_content = str(element.content)
                text_flowables = process_text_content(text_content, styles, color_theme)
                elements.extend(text_flowables)

            elif element.type in ["table", "chart", "image"]:
                # Create a styled placeholder for non-text elements
                placeholder_text = Paragraph(f"[{element.type.capitalize()}: {element.content}]", styles["Italic"])

                # Use different styling based on element type
                if element.type == "table":
                    background_color = colors.HexColor("#F0F7FF")  # Light blue
                elif element.type == "chart":
                    background_color = colors.HexColor("#F0FFF0")  # Light green
                else:  # image
                    background_color = colors.HexColor("#FFF0F5")  # Light pink

                placeholder_box = BoxedContent(
                    [placeholder_text],
                    padding=15,
                    background_color=background_color,
                    border_color=color_theme["secondary"],
                    border_width=0.5,
                    corner_radius=5,
                    drop_shadow=True,
                )
                elements.append(placeholder_box)

            elements.append(Spacer(1, 15))

    return elements


def create_document_template(
    doc: SimpleDocTemplate, title: str, color_theme: dict[str, colors.Color], layout_style: dict[str, Any]
) -> SimpleDocTemplate:
    """
    Create a document template with custom header, footer, and page layouts

    Args:
        doc: ReportLab document
        title: Document title
        color_theme: Color theme dictionary
        layout_style: Layout style dictionary

    Returns:
        Document template object
    """
    # Get page size and margins
    page_size = doc.pagesize
    margin_left, margin_right, margin_top, margin_bottom = layout_style["margins"]

    # Create a function for the header
    def header_footer(canvas: Any, doc: Any) -> None:
        canvas.saveState()

        # Header
        if layout_style["header_height"] > 0:
            # Draw a colored band for the header
            canvas.setFillColor(color_theme["primary"])
            canvas.rect(
                0,
                page_size[1] - layout_style["header_height"],
                page_size[0],
                layout_style["header_height"],
                fill=1,
                stroke=0,
            )

            # Add the title
            canvas.setFont("Helvetica-Bold", 10)
            canvas.setFillColor(colors.white)
            canvas.drawString(margin_left, page_size[1] - layout_style["header_height"] / 2 - 5, title)

            # Add page number
            canvas.setFont("Helvetica", 9)
            canvas.drawRightString(
                page_size[0] - margin_right, page_size[1] - layout_style["header_height"] / 2 - 5, f"Page {doc.page}"
            )

        # Footer
        if layout_style["footer_height"] > 0:
            # Draw a subtle line above the footer
            canvas.setStrokeColor(color_theme["secondary"])
            canvas.setLineWidth(0.5)
            canvas.line(
                margin_left,
                layout_style["footer_height"] / 2,
                page_size[0] - margin_right,
                layout_style["footer_height"] / 2,
            )

            # Add the date
            canvas.setFont("Helvetica", 8)
            canvas.setFillColor(color_theme["secondary"])
            import datetime

            date_str = datetime.datetime.now().strftime("%Y-%m-%d")
            canvas.drawString(margin_left, layout_style["footer_height"] / 2 - 10, f"Generated on {date_str}")

            # Add "Confidential" or other marking
            canvas.setFont("Helvetica", 8)
            canvas.drawCentredString(page_size[0] / 2, layout_style["footer_height"] / 2 - 10, "Synthetic Document")

        canvas.restoreState()

    # Create page templates based on the selected layout
    if layout_style["columns"] == 1:
        # Single column layout
        frame = Frame(
            margin_left,
            margin_bottom,
            page_size[0] - margin_left - margin_right,
            page_size[1] - margin_top - margin_bottom - layout_style["header_height"] - layout_style["footer_height"],
            leftPadding=0,
            bottomPadding=0,
            rightPadding=0,
            topPadding=0,
        )

        page_template = PageTemplate(id="normal", frames=[frame], onPage=header_footer)

        doc.addPageTemplates([page_template])

    elif layout_style["columns"] == 2:
        # Two column layout
        column_width = (page_size[0] - margin_left - margin_right - layout_style["column_gap"]) / 2

        left_frame = Frame(
            margin_left,
            margin_bottom,
            column_width,
            page_size[1] - margin_top - margin_bottom - layout_style["header_height"] - layout_style["footer_height"],
            leftPadding=0,
            bottomPadding=0,
            rightPadding=0,
            topPadding=0,
            id="left_column",
        )

        right_frame = Frame(
            margin_left + column_width + layout_style["column_gap"],
            margin_bottom,
            column_width,
            page_size[1] - margin_top - margin_bottom - layout_style["header_height"] - layout_style["footer_height"],
            leftPadding=0,
            bottomPadding=0,
            rightPadding=0,
            topPadding=0,
            id="right_column",
        )

        page_template = PageTemplate(id="two_columns", frames=[left_frame, right_frame], onPage=header_footer)

        doc.addPageTemplates([page_template])

    return doc


def pdf_renderer_node(state: dict[str, Any]) -> dict[str, Any]:
    """
    PDF renderer node that creates a PDF from the document structure with visual styling

    Args:
        state: The current state dictionary containing document structure

    Returns:
        Updated state with PDF data
    """
    document = state["document"]
    page_size = state.get("page_size", "A4")

    # Process visual styling selection if not already done
    if "color_theme" not in state or "layout_style" not in state:
        state = select_theme(state)

    color_theme = state["color_theme"]
    layout_style = state["layout_style"]

    # Select page size
    pdf_page_size = letter if page_size.upper() == "LETTER" else A4

    # Create a PDF buffer
    buffer = io.BytesIO()

    # Create a PDF document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=pdf_page_size,
        leftMargin=layout_style["margins"][0],
        rightMargin=layout_style["margins"][1],
        topMargin=layout_style["margins"][2],
        bottomMargin=layout_style["margins"][3],
    )

    # Apply document template with header and footer if advanced layout is enabled
    if state.get("advanced_layout", True):
        doc = create_document_template(doc, document["title"], color_theme, layout_style)

    # Get styles with theme colors
    styles = create_pdf_styles(color_theme)

    # Create a list to hold the flowable elements
    elements = []

    # Add the document title with theme styling
    title = Paragraph(document["title"], styles["Title"])
    title.textColor = color_theme["primary"]
    elements.append(title)
    elements.append(Spacer(1, 20))

    # Function to recursively process sections and add to the PDF
    def add_section_to_pdf(section, level=1):
        # Add section title with appropriate heading style and theme color
        if level == 1:
            section_title = Paragraph(section.title, styles["Heading1"])
        elif level == 2:
            section_title = Paragraph(section.title, styles["Heading2"])
        else:
            section_title = Paragraph(section.title, styles["Heading3"])

        elements.append(section_title)
        elements.append(Spacer(1, 10))

        # Process content based on type with theme colors
        section_elements = []

        try:
            if section.type == "text":
                section_elements = process_text_content(section.content, styles, color_theme)
            elif section.type == "table":
                section_elements = process_table_content(section.content, styles, color_theme)
            elif section.type == "chart":
                section_elements = process_chart_content(section.content, styles, color_theme)
            elif section.type == "image":
                section_elements = process_image_content(section.content, styles, color_theme)
            elif section.type == "complex":
                section_elements = process_complex_content(section.content, styles, color_theme)

            # Add the section elements
            elements.extend(section_elements)

        except Exception as e:
            # Handle errors in content processing
            error_text = Paragraph(f"Error processing {section.type} content: {e!s}", styles["Italic"])
            elements.append(error_text)
            elements.append(Spacer(1, 10))

        # Process subsections
        for subsection in section.subsections:
            add_section_to_pdf(subsection, level + 1)

        # Add extra space after each main section
        if level == 1:
            elements.append(Spacer(1, 15))
            elements.append(PageBreak())

    # Process all sections
    for section in document["sections"]:
        add_section_to_pdf(section)

    # Build the PDF
    doc.build(elements)

    # Get the PDF data
    pdf_data = buffer.getvalue()
    buffer.close()

    return {
        "pdf_data": pdf_data,
        "selected_theme": state["selected_theme"],
        "selected_layout": state["selected_layout"],
    }
