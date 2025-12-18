# core/templatetags/language_tags.py
from django import template
from django.conf import settings

register = template.Library()

@register.simple_tag(takes_context=True)
def change_language(context, lang):
    """Generate URL for changing language"""
    request = context['request']
    current_path = request.path
    
    # Remove language prefix if present
    for code, name in settings.LANGUAGES:
        prefix = f'/{code}/'
        if current_path.startswith(prefix):
            current_path = current_path[len(prefix)-1:]  # Keep leading /
    
    return f'/{lang}{current_path}'
