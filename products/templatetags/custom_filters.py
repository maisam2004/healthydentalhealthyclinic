# myapp/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def stars(rating):
    try:
        rating = float(rating)
    except (ValueError, TypeError):
        return ''

    full_stars = int(rating)
    half_star = 1 if rating - full_stars >= 0.5 else 0

    return (
        '<i class="fa fa-star"></i>' * full_stars +
        '<i class="fa-solid fa-star-half-stroke"></i>' * half_star +
        '<i class="fa fa-star-o"></i>' * (5 - full_stars - half_star)
    )

@register.filter
def range_filter(value):
    return range(1, value+1)