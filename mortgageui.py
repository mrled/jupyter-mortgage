#!/usr/bin/env python3

"""Jupyter wrappers for displaying mortgage information"""

from IPython.display import (
    HTML,
    display,
)
import ipywidgets

import mortgage


def htmlschedule():
    def f(apryearly, principal, years, overpayment):
        term = years * mortgage.MONTHS_IN_YEAR
        display(HTML(mortgage.htmlschedule(apryearly, principal, term, overpayment)))

    widget = ipywidgets.interactive(
        f,
        apryearly=ipywidgets.FloatSlider(min=0.0, max=10.0, step=0.25, value=3.75),
        principal=ipywidgets.IntSlider(min=0, max=1_000_000, step=5000, value=250_000),
        years=ipywidgets.IntSlider(min=15, max=30, step=5, value=30),
        overpayment=ipywidgets.IntSlider(min=0, max=5000, step=50, value=0))
    display(widget)

