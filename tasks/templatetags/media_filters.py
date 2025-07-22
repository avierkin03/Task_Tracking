from django import template

register = template.Library()


@register.filter(name="endswith")
def endswith(value, arg):
    """Перевіряє, чи закінчується рядок заданим значенням."""
    if isinstance(value, str):
        return value.lower().endswith(arg.lower())
    return False