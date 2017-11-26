#!/usr/bin/env python3

"""Jupyter wrappers for displaying mortgage information"""

import logging
import os

from IPython.display import (
    HTML,
    display,
)
import ipywidgets

from mako.template import Template

from bloodloan import util
from bloodloan.mortgage import closing
from bloodloan.mortgage import expenses
from bloodloan.mortgage import mmath
from bloodloan.mortgage import schedule
from bloodloan.ui import streetmap


SCRIPTDIR = os.path.dirname(os.path.realpath(__file__))
TEMPL = os.path.join(SCRIPTDIR, 'templ')
logger = logging.getLogger(__name__)  # pylint: disable=C0103


def dollar(amount):
    """Return a string dollar amount from a float

    For example, dollar(1926.2311831442486) => "$1,926.23"

    We aren't too concerned about the lost accuracy;
    this function should only be used for *display* values

    NOTE: I'm not sure why, but I often find that if I don't wrap a dollar()
    call in <span> tags, Jupyter does something really fucked up to my text
    """
    return '${:,.2f}'.format(amount)


def disablecellscroll():
    """Disable in-cell scrolling"""

    display(HTML('''
        <script>
        IPython.OutputArea.prototype._should_scroll = function(lines) {
            return false;
        }
        </script>
        '''))


def toggleinputcells():
    """Enable toggling input cells"""

    # Enable toggling display of input cells
    display(HTML('''
        <script>
        show_inputs = true;
        function toggleinputs() {
            if (show_inputs){
                $('div.input').hide();
            } else {
                $('div.input').show();
            }
            show_inputs = !show_inputs;
        }
        // Uncomment this to automatically hide input cells when notebook is run:
        //$(document).ready(toggleinputs);
        </script>
        '''))

    # Show title, input code toggle message, and input code toggle button
    display(HTML('''
        <h2>Modifying this notebook</h2>

        <p>Input code for this notebook can be hidden for easier reading (and printing).</p>
        <p>
            For simple inputs, you may not need to view the code;
            you can change values like sale price and interest rate using the GUI widgets.
            For more complex inputs, such as defining a new set of closing costs,
            you will need to enable input code display, and create a list of closing costs in inline Python.
        </p>
        <p><button onclick="toggleinputs()">Toggle input code display</button></p>
        <hr/>
        '''))


def wrap_close(saleprice, interestrate, loanterm, propertytaxes):
    """Show loan amounts and closing costs"""
    costs = closing.IRONHARBOR_FHA_CLOSING_COSTS
    monthterm = loanterm * mmath.MONTHS_IN_YEAR
    result = closing.close(saleprice, interestrate, monthterm, propertytaxes, costs)

    templ = Template(filename=os.path.join(TEMPL, 'close.mako'))
    display(HTML(templ.render(closeresult=result)))

    return result


def wrap_schedule(interestrate, value, principal, saleprice, years, overpayment, appreciation):
    """Show a loan's mortgage schedule in a Jupyter notebook"""

    term = years * mmath.MONTHS_IN_YEAR
    overpayments = [overpayment for _ in range(term)]

    # Calculate the monthly payments for the mortgage schedule detail,
    # yearly payments for the mortgage schedule summary
    # and monthly payments with no overpayments for comparative analysis in prefacetempl
    months = [month for month in schedule.schedule(
        interestrate, value, principal, saleprice, term,
        overpayments=overpayments, appreciation=appreciation,
        monthlycosts=expenses.IRONHARBOR_FHA_MONTHLY_COSTS + expenses.CAPEX_MONTHLY_COSTS)]
    months_no_over = [month for month in schedule.schedule(
        interestrate, value, principal, saleprice, term, overpayments=None, appreciation=appreciation)]
    years = [year for year in schedule.monthly2yearly_schedule(months)]

    prefacetempl = Template(filename=os.path.join(TEMPL, 'schedule_preface.mako'))
    schedtempl = Template(filename=os.path.join(TEMPL, 'schedule.mako'))

    # Display a preface / summary first
    display(HTML(prefacetempl.render(
        interestrate=interestrate,
        principal=principal,
        term=term,
        overpayment=overpayment,
        appreciation=appreciation,
        monthlypayments=months,
        monthlypayments_no_over=months_no_over)))

    # Create new Output objects, and call display(HTML(...)) in them
    # We do this because IPython.display.HTML() has nicer talbles
    # than ipywidgets.HTML(), but only ipywidgets-type widgets can be put
    # into an Accordion.
    summaryout = ipywidgets.Output()
    detailout = ipywidgets.Output()
    with summaryout:
        display(HTML(schedtempl.render(
            principal=principal,
            value=value,
            loanpayments=years,
            paymentinterval_name="Year")))
    with detailout:
        display(HTML(schedtempl.render(
            principal=principal,
            value=value,
            loanpayments=months,
            paymentinterval_name="Month")))

    parentwidg = ipywidgets.Accordion()
    parentwidg.children = [summaryout, detailout]
    parentwidg.set_title(0, 'Yearly summary')
    parentwidg.set_title(1, 'Monthly detail')
    display(parentwidg)

    return months


# def wrap_monthly_expenses(schedule, costs, saleprice):
#     """Show monthly expenses"""
#     months = [month for month in mortgage.monthly_expenses(schedule, costs, saleprice)]
#     htmlstr = "<table>"
#     for midx, month in enumerate(months):
#         htmlstr += f"<tr><th>Month {midx + 1} total</th><th>{dollar(sum([e.value for e in month]))}</th></tr>"
#         for expense in month:
#             log.info(f"Retrieving calculated expense: '{expense}'")
#             htmlstr += f"<tr><td>{expense.label}</td><td>{dollar(expense.value)}</td></tr>"
#     htmlstr += "</table>"
#     display(HTML(htmlstr))


def get_displayable_geocode(geocode, title):
    """Retrieve display()-able streetmap and property information for a list of geocodes

    geocodes    list of GeocodeResult objects
    title       value for an <h3> element

    return      an OutputChildren, for adding to the .children property of an ipywidgets.Box
    """
    result = util.OutputChildren()

    result.display(HTML(f"<h3>{title}</h3>"))
    result.display(HTML(f"<p><em>{geocode.displayname}</em></p>"))

    property_info = ipywidgets.Box(layout=ipywidgets.Layout(
        display='flex',
        flex_flow='column',
        align_items='stretch',
        width='20em'))

    def info_row(label, value):
        """Return an informational row for displaying property info"""
        return ipywidgets.Box(
            children=(
                ipywidgets.Label(label),
                ipywidgets.Label(value)),
            layout=ipywidgets.Layout(
                display='flex',
                flex_flow='row',
                justify_content='space-between'))

    property_info.children = (
        info_row("County", geocode.county),
        info_row("Neighborhood", geocode.neighborhood),
        info_row("Latitude", geocode.coordinates[0]),
        info_row("Longitude", geocode.coordinates[1]))

    result.display(property_info)
    result.display(geocode.figure)

    return result


def wrap_streetmap(address, google_api_key=None):
    """Show street maps and property information"""

    if google_api_key:
        mapper = streetmap.GoogleMapper(google_api_key)
    else:
        mapper = streetmap.OpenStreetMapper()
    geocodes = mapper.geocode(address)

    result = util.OutputChildren()
    result.display(util.html_hbox(f"Using {mapper} for maps", "info"))
    result.display(HTML(f"<h2>Map & property information</h2>"))

    if len(geocodes) < 1:
        result.display(
            util.html_hbox(f"Could not find property at {address}", "danger"))
    elif len(geocodes) > 1:
        result.display(
            util.html_hbox(f"{len(geocodes)} matches returned for {address}", "warning"))

    for idx, geocode in enumerate(geocodes):
        if len(geocodes) != 1:
            maptitle = f"Property {idx + 1}</h3>"
        else:
            maptitle = "Property information"
        result += get_displayable_geocode(geocode, maptitle)

    return result


street_map_executor = util.DelayedExecutor()  # pylint: disable=C0103


def propertyinfo():
    """Gather information about a property using Jupyter UI elements"""

    def metawrapper(
            interestrate,
            saleprice,
            years,
            overpayment,
            appreciation,
            propertytaxes,
            address,
            google_api_key):
        """Gather information about a property"""

        interestrate = mmath.percent2decimal(interestrate)
        appreciation = mmath.percent2decimal(appreciation)

        closed = wrap_close(saleprice, interestrate, years, propertytaxes)

        # TODO: currently assuming sale price is value; allow changing to something else
        months = wrap_schedule(
            interestrate, saleprice, closed.principal_total, saleprice, years, overpayment,
            appreciation)

        # wrap_monthly_expenses(
        #     months,
        #     expenses.IRONHARBOR_FHA_MONTHLY_COSTS + expenses.CAPEX_MONTHLY_COSTS,
        #     saleprice)

        global street_map_executor  # pylint: disable=W0603,C0103
        streetmap_container = ipywidgets.Box()
        street_map_executor.run(
            streetmap_container,
            "Loading maps...",
            wrap_streetmap,
            action_args=(address, google_api_key))
        display(streetmap_container)

    instructionstempl = Template(filename=os.path.join(TEMPL, 'instructions.mako'))
    display(HTML(instructionstempl.render()))

    widgets_box = ipywidgets.Box(layout=ipywidgets.Layout(
        display='flex',
        flex_flow='column',
        align_items='stretch',
        width='70%'))

    interestrate = util.label_widget("Interest rate", widgets_box, ipywidgets.BoundedFloatText(
        value=3.75,
        min=0.01,
        step=0.25))
    saleprice = util.label_widget("Sale price", widgets_box, ipywidgets.BoundedFloatText(
        value=250_000,
        min=1,
        max=1_000_000_000,
        step=1000))
    years = util.label_widget("Loan term in years", widgets_box, ipywidgets.Dropdown(
        options=[15, 20, 25, 30],
        value=30))
    overpayment = util.label_widget(
        "Monthly overpayment amount", widgets_box, ipywidgets.BoundedIntText(
            value=50,
            min=0,
            max=1_000_000,
            step=5))
    appreciation = util.label_widget(
        "Yearly appreciation", widgets_box, ipywidgets.BoundedFloatText(
            value=0.5,
            min=-20.0,
            max=20.0,
            step=0.5))
    propertytaxes = util.label_widget(
        "Yearly property taxes", widgets_box, ipywidgets.BoundedIntText(
            value=5500,
            min=0,
            max=1_000_000,
            step=5))
    address = util.label_widget("Property address", widgets_box, ipywidgets.Textarea(
        value="1600 Pennsylvania Ave NW, Washington, DC 20500"))
    google_api_key = util.label_widget("Google API key (optional)", widgets_box, ipywidgets.Text(
        value=""))

    output = ipywidgets.interactive_output(metawrapper, {
        'interestrate': interestrate,
        'saleprice': saleprice,
        'years': years,
        'overpayment': overpayment,
        'appreciation': appreciation,
        'propertytaxes': propertytaxes,
        'address': address,
        'google_api_key': google_api_key})

    display(widgets_box, output)
