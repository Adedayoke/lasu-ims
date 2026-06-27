from django import template

register = template.Library()


@register.filter
def split(value, sep=','):
    return [x.strip() for x in value.split(sep)]


@register.filter
def in_list(value, arg):
    return value in [x.strip() for x in arg.split(',')]


@register.filter
def naira(value, decimals=None):
    """Format a number as Nigerian Naira with thousands separators.
    Usage: {{ value|naira }} → ₦150,000.00
           {{ value|naira:0 }} → ₦150,000
    """
    try:
        val = float(value)
        if decimals is not None and str(decimals) == '0':
            return f"₦{val:,.0f}"
        return f"₦{val:,.2f}"
    except (ValueError, TypeError):
        return "—"
