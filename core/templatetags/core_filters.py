from django import template
from datetime import date
import inflect

register = template.Library()

@register.filter
def format_meeting_date(day_of_month):
    """
    Converts an integer day of the month into a date string.
    Uses the current month and year for context.
    """
    if not day_of_month:
        return ""
    try:
        today = date.today()
        formatted_date = date(today.year, today.month, day_of_month)
        return formatted_date.strftime('%Y/%m/%d')
    except ValueError:
        return "Invalid date"

@register.filter
def zip_lists(a, b):
    return zip(a, b)

@register.filter
def get_item(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(key, None)
    return None 

# Create the number-to-words filter
@register.filter
def number_to_words(value):
    p = inflect.engine()
    try:
        return p.number_to_words(value)
    except Exception:
        return ''

@register.filter(name="replace")
def replace(value, arg):
    """Replace underscores with spaces"""
    return value.replace("_", " ") if value else value

# Debugging registered filters
# print(register.filters)

