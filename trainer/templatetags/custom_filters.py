from django import template
from django.forms.boundfield import BoundField

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    """
    Adds a CSS class to a form field.
    Handles both form fields and non-form field values without raising an error.
    """
    if isinstance(field, BoundField):
        return field.as_widget(attrs={"class": css_class})
    return field  # Return the value as-is if it's not a form field
