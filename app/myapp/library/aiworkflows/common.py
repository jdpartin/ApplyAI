from myapp.views.json_views import *
import json
from enum import Enum


class EntityType(Enum):
    CONSOLIDATED_DATA = "consolidated_data"
    USER = "user"
    EDUCATION = "education"
    WORK_EXPERIENCE = "work_experience"
    SKILLS = "skills"
    PROJECTS = "projects"
    CERTIFICATIONS = "certifications"
    

def get_data(request, entity_type: EntityType):
    """
    Get data for a specific entity type.
    Args:
        entity_type (EntityType): The type of entity to fetch.
    Returns:
        dict: Data corresponding to the specified entity type.
    """
    if entity_type == EntityType.CONSOLIDATED_DATA:
        data = consolidated_user_data(request)
    elif entity_type == EntityType.USER:
        data = user_info_data(request)
    elif entity_type == EntityType.EDUCATION:
        data = education_data(request)
    elif entity_type == EntityType.WORK_EXPERIENCE:
        data = work_experience_data(request)
    elif entity_type == EntityType.SKILLS:
        data = skill_data(request)
    elif entity_type == EntityType.PROJECTS:
        data = project_data(request)
    elif entity_type == EntityType.CERTIFICATIONS:
        data = certification_data(request)
    else:
        raise ValueError(f"Unknown entity type: '{entity_type}'")

    return json.loads(data.content.decode('utf-8'))
