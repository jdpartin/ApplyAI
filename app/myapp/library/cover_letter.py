from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from myapp.models import CoverLetter
import json


@login_required
def add_or_update_cover_letter(request, data=None):
    """
    A consolidated function to add or update a cover letter.
    Defaults to the request body if data is not provided.

    Args:
        request: a user request
        data(optional): a JSON object containing the id (optional), name, purpose, and text of the cover letter.

    Returns: 
        On Success: A JsonResponse with status: success, message and cover_letter_id. Code 200
        On Failure: A JsonResponse with status: error, and message. Code 400 or 500
    """
    try:
        if not data:
            data = json.loads(request.body)  # Parse the JSON from the request body if data is not provided

        cover_letter_id = data.get('id')  # Check if an ID is provided
        if cover_letter_id:
            # Try to update the existing cover letter
            try:
                cover_letter = CoverLetter.objects.get(id=cover_letter_id, user=request.user)
                cover_letter.name = data.get('name', cover_letter.name)
                cover_letter.purpose = data.get('purpose', cover_letter.purpose)
                cover_letter.text = data.get('text', cover_letter.text)
                cover_letter.save()
                return JsonResponse({'status': 'success', 'message': 'Cover Letter updated successfully.', 'cover_letter_id': cover_letter.id}, status=200)
            except CoverLetter.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Cover Letter not found or does not belong to the user.'}, status=404)

        # If no ID is provided, create a new cover letter
        cover_letter = CoverLetter.objects.create(
            user=request.user,
            name=data.get('name', 'Untitled Cover Letter'),
            purpose=data.get('purpose', ''),
            text=data.get('text', ''),
        )
        return JsonResponse({'status': 'success', 'message': 'Cover Letter created successfully.', 'cover_letter_id': cover_letter.id}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON format.'}, status=400)
    except KeyError as e:
        return JsonResponse({'status': 'error', 'message': f'Missing key: {e}'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'An error occurred: {str(e)}'}, status=500)
