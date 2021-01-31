from django import template
register = template.Library()

@register.filter
def get_dict_value(dictionary, key):
    return dictionary.get(key, '')

@register.filter
def minus(v1, v2):
    return v1-v2

@register.filter
def mul(v1, v2):
    return v1*v2

@register.filter
def div(v1, v2):
    return v1/v2 if v2 else 0

@register.filter
def percent(v1, v2):
    return (v1/v2)*100 if v1 and v2 else 0
