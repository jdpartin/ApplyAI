from reportlab.platypus import Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from myapp.library.pdf import PDFGenerator


def format_date(date):
    """Format dates consistently."""
    return date if date != "None" else "Present"


def generate_resume(output, resume_info):
    """
    Generate a resume PDF from a JSON-like object using PDFGenerator.

    :param output: Path or BytesIO object where the PDF will be saved.
    :param resume_info: Dictionary containing resume information.
    """
    pdf_generator = PDFGenerator(output)

    def resume_content(pdf_gen, story):
        styles = getSampleStyleSheet()

        # Add Horizontal Line Function
        def add_section_header(title):
            story.append(Spacer(1, 12))
            story.append(Paragraph(f"<b>{title}</b>", styles["Heading2"]))
            story.append(HRFlowable(width="100%", thickness=1, color="black"))
            story.append(Spacer(1, 12))

        # Add Applicant Information
        include_info = resume_info.get("includePersonalInfo", {})
        if include_info.get("name"):
            story.append(Paragraph(f"<b>{include_info['name']} Resume</b>", styles["Title"]))
        if include_info.get("phone"):
            story.append(Paragraph(f"Phone: {include_info['phone']}", styles["Normal"]))
        if include_info.get("email"):
            story.append(Paragraph(f"Email: {include_info['email']}", styles["Normal"]))
        if include_info.get("address"):
            story.append(Paragraph(f"Address: {include_info['address']}", styles["Normal"]))
        if include_info.get("summary"):
            story.append(Spacer(1, 12))
            add_section_header("Summary")
            story.append(Paragraph(include_info["summary"], styles["Normal"]))
        story.append(Spacer(1, 20))  # Add extra space before next section

        # Add Education
        if "educations" in resume_info:
            add_section_header("Education")
            for edu in resume_info["educations"]:
                text = f"{edu.get('degree', '')} in {edu.get('field_of_study', '')} - {edu.get('school_name', '')}"
                start_date = format_date(edu.get("start_date", ""))
                end_date = format_date(edu.get("end_date", "Present"))
                story.append(Paragraph(f"{text} ({start_date} - {end_date})", styles["Normal"]))

        # Add Work Experience
        if "workExperiences" in resume_info:
            add_section_header("Work Experience")
            for work in resume_info["workExperiences"]:
                title = f"{work.get('title', '')} at {work.get('company', '')}"
                start_date = format_date(work.get("start_date", ""))
                end_date = format_date(work.get("end_date", "Present"))
                story.append(Paragraph(f"<b>{title}</b> ({start_date} - {end_date})", styles["Normal"]))
                if work.get("description"):
                    story.append(Spacer(1, 8))
                    story.append(Paragraph(work["description"], styles["Normal"]))
                story.append(Spacer(1, 12))

        # Add Skills
        if "skills" in resume_info:
            add_section_header("Skills")
            skills = [f"{skill['name']} ({skill['years_of_experience']} years)" for skill in resume_info["skills"]]
            story.append(Paragraph(", ".join(skills), styles["Normal"]))

        # Add Projects
        if "projects" in resume_info:
            add_section_header("Projects")
            for project in resume_info["projects"]:
                title = project.get("title", "")
                description = project.get("description", "")
                technologies = project.get("technologies_used", "N/A")
                story.append(Paragraph(f"<b>{title}</b>: {description} (Technologies: {technologies})", styles["Normal"]))

        # Add Certifications
        if "certifications" in resume_info:
            add_section_header("Certifications")
            for cert in resume_info["certifications"]:
                text = f"{cert.get('title', '')} - {cert.get('issuer', '')}"
                issue_date = format_date(cert.get("issue_date", ""))
                expiration_date = format_date(cert.get("expiration_date", "No Expiration"))
                story.append(Paragraph(f"{text} ({issue_date} - {expiration_date})", styles["Normal"]))

    pdf_generator.generate_pdf(resume_content)
