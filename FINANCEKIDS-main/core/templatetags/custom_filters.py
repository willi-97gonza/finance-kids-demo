from django import template
register = template.Library()

@register.filter
def get_item(dictionary, key):
    if dictionary is None or not isinstance(dictionary, dict):
        return ''  # o return None
    return dictionary.get(key)
