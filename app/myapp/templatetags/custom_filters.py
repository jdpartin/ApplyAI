from django import template

register = template.Library()

@register.filter
def get_dict_item(dictionary, key):
    """
    Returns the value from a dictionary for the given key.
    """
    try:
        return dictionary.get(key, '')
    except AttributeError:
        return ''
