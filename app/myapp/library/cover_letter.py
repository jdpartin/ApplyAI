from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from myapp.models import CoverLetter
import json


@login_required
def add_cover_letter(request, data=None):
    """
    A consolidated function to add a cover letter, defaults to the request body if data is not provided
    Args:
        request: a user request
        data(optional): a JSON object containing the name, purpose, and text of the cover letter
    Returns: 
        On Success: A JsonResponse with status: success, message and cover_letter_id. Code 200
        On Failure: A JsonResponse with status: error, and message. Code 400 or 500
    """
    try:
        if not data:
            data = json.loads(request.body) # Strange error in this file where the request body is not accessible to the view

        cover_letter = CoverLetter.objects.create(
                user=request.user,
                name=data.get('name', 'Untitled Cover Letter'),
                purpose=data.get('purpose', ''),
                text=data.get('text', ''),
            )

        cover_letter.save()

        return JsonResponse({'status': 'success', 'message': 'Cover Letter created successfully.', 'cover_letter_id': cover_letter.id}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON format.'}, status=400)
    except KeyError as e:
        return JsonResponse({'status': 'error', 'message': f'Missing key: {e}'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'An error occurred: {str(e)}'}, status=500)