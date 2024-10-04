from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(value, css_class):
     # Check if the value has the 'as_widget' method (i.e., it's a form field)
    if hasattr(value, 'as_widget'):
        return value.as_widget(attrs={'class': css_class})
    # If it's a string, just return it (or handle this case differently)
    return value

