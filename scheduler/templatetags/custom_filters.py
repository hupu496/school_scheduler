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

@register.filter
def dict_get(d, key):
    """Safely get value from dict or return empty dict/list"""
    if d is None:
        return {}
    return d.get(key, {})
