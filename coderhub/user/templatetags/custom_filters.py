# templatetags/custom_filters.py
from datetime import timedelta
from django import template

register = template.Library()

@register.filter
def add_days(value, days):
    try:
        return value + timedelta(days=int(days))
    except (ValueError, TypeError):
        return value