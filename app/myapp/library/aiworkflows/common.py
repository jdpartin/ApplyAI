from myapp.views.view_utils import json_utils
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
    try:
        if entity_type == EntityType.CONSOLIDATED_DATA:
            data = json_utils.consolidated_user_data(request)
        elif entity_type == EntityType.USER:
            data = json_utils.user_info_data(request)
        elif entity_type == EntityType.EDUCATION:
            data = json_utils.education_data(request)
        elif entity_type == EntityType.WORK_EXPERIENCE:
            data = json_utils.work_experience_data(request)
        elif entity_type == EntityType.SKILLS:
            data = json_utils.skill_data(request)
        elif entity_type == EntityType.PROJECTS:
            data = json_utils.project_data(request)
        elif entity_type == EntityType.CERTIFICATIONS:
            data = json_utils.certification_data(request)
        else:
            raise ValueError(f"Unknown entity type: '{entity_type}'")

    except Exception as e:
        print(e)

    return json.loads(data.content.decode('utf-8'))
