from django import template

register = template.Library()


@register.filter
def uglify(field):
    result = ""
    for i in range(len(field)):
        if i % 2 == 0:
            result += field[i].lower()
        else:
            result += field[i].upper()
    return result
