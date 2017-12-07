"""UI utility functions
"""

# Note: This module exists to break a circular dependency
#       Normally Python is pretty good with those,
#       but apparent when ui.py has dollar(), and imports templ.py,
#       and templ.py has a template which uses ui.dollar(),
#       we get a runtime error.

from bloodloan.mortgage import mmath


def dollar(amount):
    """Return a string dollar amount from a float

    For example, dollar(1926.2311831442486) => "$1,926.23"

    We aren't too concerned about the lost accuracy;
    this function should only be used for *display* values

    NOTE: I'm not sure why, but I often find that if I don't wrap a dollar()
    call in <span> tags, Jupyter does something really fucked up to my text
    """
    return '${:,.2f}'.format(amount)


def percent(decimal):
    """Return a string percentage from a float

    For example, percent(0.0320) => 3.2000%

    The result is rounded to four decimal places (of the *return* value).

    This function *loses precision* (and returns a string),
    so it should only be relied upon to *display* a percentage value.
    """
    return '{:.4f}%'.format(mmath.decimal2percent(decimal))
