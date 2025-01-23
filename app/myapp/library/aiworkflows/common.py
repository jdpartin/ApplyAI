from myapp.views.json_views import *
import json
from enum import Enum


class EntityType(Enum):
    USER = "user"
    EDUCATION = "education"
    WORK_EXPERIENCE = "work_experience"
    SKILLS = "skills"
    PROJECTS = "projects"
    CERTIFICATIONS = "certifications"
    

def get_data(entity_type: EntityType):
    """
    Get data for a specific entity type.
    Args:
        entity_type (EntityType): The type of entity to fetch.
    Returns:
        dict: Data corresponding to the specified entity type.
    """
    global CURRENT_REQUEST

    if entity_type == EntityType.USER:
        data = user_info_data(CURRENT_REQUEST)
    elif entity_type == EntityType.EDUCATION:
        data = education_data(CURRENT_REQUEST)
    elif entity_type == EntityType.WORK_EXPERIENCE:
        data = work_experience_data(CURRENT_REQUEST)
    elif entity_type == EntityType.SKILLS:
        data = skill_data(CURRENT_REQUEST)
    elif entity_type == EntityType.PROJECTS:
        data = project_data(CURRENT_REQUEST)
    elif entity_type == EntityType.CERTIFICATIONS:
        data = certification_data(CURRENT_REQUEST)
    else:
        raise ValueError(f"Unknown entity type: '{entity_type}'")

    return json.loads(data.content.decode('utf-8'))
