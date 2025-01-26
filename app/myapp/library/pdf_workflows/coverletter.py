from myapp.library.pdf import PDFGenerator


def generate_coverletter(output, text):
    """
    Generate a cover letter PDF from a block of text.

    :param output: Path or BytesIO object where the PDF will be saved.
    :param text: The block of text to format as a cover letter.
    """
    pdf_generator = PDFGenerator(output)

    def cover_letter_content(pdf_gen, story):
        lines = text.split("\n")
        for line in lines:
            pdf_gen.add_paragraph(story, line)

    pdf_generator.generate_pdf(cover_letter_content)