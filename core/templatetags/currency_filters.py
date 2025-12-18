# core/templatetags/currency_filters.py
from django import template

register = template.Library()

@register.filter
def format_currency(value):
    """Format value as CDF currency"""
    if value is None:
        return "CDF 0"
    
    try:
        # Format with commas for thousands
        formatted = f"{float(value):,.0f}".replace(",", " ")
        return f"CDF {formatted}"
    except (ValueError, TypeError):
        return f"CDF {value}"
