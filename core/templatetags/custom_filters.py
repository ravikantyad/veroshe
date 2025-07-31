from django import template

register = template.Library()

@register.filter
def get_range(value, start):
    return range(start, value+1)

