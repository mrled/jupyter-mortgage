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

    desc_width = '10em'

    AprWidget = ipywidgets.FloatText(
        value=3.75,
        description="APR",
        style={'description_width': desc_width})
    PrincipalWidget = ipywidgets.IntText(
        value=250_000,
        description="Loan amount",
        style={'description_width': desc_width})
    TermWidget = ipywidgets.Dropdown(
        options=[15, 20, 25, 30],
        value=30,
        description="Loan term in years",
        style={'description_width': desc_width})
    OverpaymentWidget = ipywidgets.IntText(
        value=0,
        description="Monthly overpayment amount",
        style={'description_width': desc_width})

    widget = ipywidgets.interactive(
        f,
        apryearly=AprWidget,
        principal=PrincipalWidget,
        years=TermWidget,
        overpayment=OverpaymentWidget)

    display(widget)

