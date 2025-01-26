from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


class PDFGenerator:
    def __init__(self, output=None):
        """
        Initialize the PDFGenerator with the output file path or a BytesIO object.

        :param output: Path to save the generated PDF or a BytesIO object.
        """
        self.output = output
        self.page_size = letter

    def generate_pdf(self, content_callback):
        """
        Generate the PDF by passing a callback function for custom content.

        :param content_callback: Function that defines custom content on the PDF.
        """
        doc = SimpleDocTemplate(self.output, pagesize=self.page_size, leftMargin=40, rightMargin=40, topMargin=50, bottomMargin=50)
        story = []

        # The callback defines the content to add
        content_callback(self, story)

        # Build the document
        doc.build(story)
        if hasattr(self.output, 'seek'):
            self.output.seek(0)

    def add_paragraph(self, story, text, style_name="Normal", space_after=12):
        """
        Adds a paragraph to the PDF.

        :param story: The story list where content is added.
        :param text: The text content to add.
        :param style_name: The style name for the paragraph.
        :param space_after: Space to add after the paragraph.
        """
        styles = getSampleStyleSheet()
        style = styles[style_name]
        story.append(Paragraph(text, style))
        story.append(Spacer(1, space_after))

    def add_section_header(self, story, text):
        """
        Adds a section header to the PDF.

        :param story: The story list where content is added.
        :param text: The header text.
        """
        self.add_paragraph(story, text, style_name="Heading2", space_after=16)

    def add_bullet_list(self, story, items):
        """
        Adds a bullet list to the PDF.

        :param story: The story list where content is added.
        :param items: List of strings to add as bullets.
        """
        bullet_style = ParagraphStyle(
            name="Bullet",
            parent=getSampleStyleSheet()["Normal"],
            bulletFontName="Helvetica",
            bulletIndent=20,
            leftIndent=30,
        )
        for item in items:
            story.append(Paragraph(f"\u2022 {item}", bullet_style))
        story.append(Spacer(1, 12))

    def add_table(self, story, data, col_widths=None):
        """
        Adds a table to the PDF.

        :param story: The story list where content is added.
        :param data: 2D list containing table data.
        :param col_widths: List of column widths.
        """
        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        story.append(table)
        story.append(Spacer(1, 12))
