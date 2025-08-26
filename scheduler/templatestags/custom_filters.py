from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get a value from a dictionary using a key"""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None

@register.filter
def make_list(value):
    """Create a range list from a number"""
    return range(1, value + 1)