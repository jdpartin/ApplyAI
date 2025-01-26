import io
import json
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from .json_views import single_resume_info
from myapp.library.pdf_workflows import generate_resume


# This file is for views that return a path to a file for download


@login_required
def download_resume(request):
    print("download_resume view called")  # Log entry into the view

    resume_id = request.GET.get('id')
    if not resume_id:
        print("No resume ID provided")  # Log missing ID
        return JsonResponse({'error': 'Resume ID is required'}, status=400)

    # Fetch and parse the resume JSON
    try:
        print(f"Fetching resume with ID: {resume_id}")  # Log fetching action
        resume_response = single_resume_info(request, resume_id)
        print("Resume fetched successfully")  # Log successful fetch

        resume_json = json.loads(resume_response.content.decode('utf-8'))
        print(f"Resume JSON parsed successfully: {resume_json}")  # Log parsed JSON
    except KeyError as e:
        print(f"KeyError encountered: {e}")  # Log missing key error
        return JsonResponse({'error': f'Missing required key: {e}'}, status=400)
    except Exception as e:
        print(f"Exception during resume fetch or parse: {e}")  # Log other exceptions
        return JsonResponse({'error': f'Failed to retrieve or parse resume: {e}'}, status=500)

    # Generate the PDF in memory
    pdf_buffer = io.BytesIO()
    try:
        print("Generating resume PDF")  # Log start of PDF generation
        generate_resume(pdf_buffer, resume_json)
        print("Resume PDF generated successfully")  # Log successful generation
    except Exception as e:
        print(f"Exception during PDF generation: {e}")  # Log any errors during generation
        return JsonResponse({'error': f'Failed to generate resume: {e}'}, status=500)

    # Return the PDF as a response
    try:
        response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{resume_json.get("name", "resume")}.pdf"'
        print("PDF response prepared successfully")  # Log response preparation
        return response
    except Exception as e:
        print(f"Exception during response preparation: {e}")  # Log any errors during response preparation
        return JsonResponse({'error': f'Failed to prepare PDF response: {e}'}, status=500)



@login_required
def download_cover_letter(request):
    cover_letter_id = request.GET.get('id')

    if not cover_letter_id:
        return JsonResponse({'error': 'Cover Letter ID is required'}, status=400)

    # Fetch and parse the cover letter JSON
    try:
        cover_letter_response = single_cover_letter_info(request, cover_letter_id)
        cover_letter_json = json.loads(cover_letter_response.content.decode('utf-8'))
    except KeyError as e:
        return JsonResponse({'error': f'Missing required key: {e}'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Failed to retrieve or parse cover letter: {e}'}, status=500)

    # Extract text from JSON
    cover_letter_text = cover_letter_json.get('text', '')
    if not cover_letter_text:
        return JsonResponse({'error': 'Cover letter text is missing'}, status=400)

    # Generate the PDF in memory
    pdf_buffer = io.BytesIO()
    try:
        generate_coverletter(pdf_buffer, cover_letter_text)
    except Exception as e:
        return JsonResponse({'error': f'Failed to generate cover letter: {e}'}, status=500)

    # Return the PDF as a response
    response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{cover_letter_json.get("name", "cover_letter")}.pdf"'
    return response
