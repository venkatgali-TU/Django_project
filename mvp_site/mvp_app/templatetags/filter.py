from django import template

register = template.Library()


@register.filter(name='split')
def split(value, key):
    """
      Returns the value turned into a list.
    """
    if isinstance(value,str):
        return value.split(key)
    else:
        temp_value = str(value)
        return temp_value.split(key)

