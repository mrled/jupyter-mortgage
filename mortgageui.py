#!/usr/bin/env python3

"""Jupyter wrappers for displaying mortgage information"""

import threading

from IPython.display import (
    HTML,
    display,
)
import ipywidgets
import ipyleaflet

import gmaps
from mako.template import Template

import mortgage
import streetmap
import util


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
        $(document).ready(toggleinputs);
        </script>
        '''))

    # Show title, input code toggle message, and input code toggle button
    display(HTML('''
        <h2>Modifying this notebook</h2>

        <p>Input code for this notebook is by default hidden for easier reading.</p>
        <p>
            For simple inputs, you may not need to view the code;
            you can change values like sale price and APR using the GUI widgets.
            For more complex inputs, such as defining a new set of closing costs,
            you will need to enable input code display, and create a list of closing costs in inline Python.
        </p>
        <p>
            Note: If you're reading this message in another notebook frontend
            (for example, a static rendering on GitHub or NBViewer),
            you will not see the rest of the notebook.
            You must run the notebook from Jupyter itself.
        </p>
        <p><button onclick="toggleinputs()">Toggle input code display</button></p>
        <hr/>
        '''))


def wrap_close(saleprice, loanapr, loanterm, propertytaxes):
    """Show loan amounts and closing costs"""
    costs = mortgage.IRONHARBOR_FHA_CLOSING_COSTS
    monthterm = loanterm * mortgage.MONTHS_IN_YEAR
    result = mortgage.close(saleprice, loanapr, monthterm, propertytaxes, costs)

    templ = Template(filename='templ/close.mako')
    display(HTML(templ.render(closeresult=result)))

    return result


def wrap_schedule(apryearly, principal, years, overpayment, appreciation):
    """Show a loan's mortgage schedule in a Jupyter notebook"""

    term = years * mortgage.MONTHS_IN_YEAR
    overpayments = [overpayment for _ in range(term)]
    appreciationpct = appreciation / 100

    # Calculate the monthly payments for the mortgage schedule detail,
    # yearly payments for the mortgage schedule summary
    # and monthly payments with no overpayments for comparative analysis in prefacetempl
    months = [month for month in mortgage.schedule(
        apryearly, principal, term, overpayments=overpayments, appreciation=appreciationpct)]
    months_no_over = [month for month in mortgage.schedule(
        apryearly, principal, term, overpayments=None, appreciation=appreciationpct)]
    years = [year for year in mortgage.monthly2yearly_schedule(months)]

    prefacetempl = Template(filename='templ/schedule_preface.mako')
    schedtempl = Template(filename='templ/schedule.mako')

    # Display a preface / summary first
    display(HTML(prefacetempl.render(
        apryearly=apryearly,
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
            loanpayments=years,
            paymentinterval_name="Year")))
    with detailout:
        display(HTML(schedtempl.render(
            principal=principal,
            loanpayments=months,
            paymentinterval_name="Month")))

    parentwidg = ipywidgets.Accordion()
    parentwidg.children = [summaryout, detailout]
    parentwidg.set_title(0, 'Yearly summary')
    parentwidg.set_title(1, 'Monthly detail')
    display(parentwidg)


def get_streetmap(address, google_api_key):
    """Show a streetmap"""

    # NOTE: display(HTML(...)) and display(ipywidgets.HTML(...)) intermixed because it lets me
    # be lazy about styling and have it mostly look ok

    output = ipywidgets.Output()
    with output:

        display(HTML(f"<h2>Map & property information</h2>"))

        if google_api_key != "":
            gmaps.configure(api_key=google_api_key)
            geocodes = streetmap.geocode_google(address, google_api_key)
            display(util.html_hbox("Google API key found - using Google maps", "info"))
        else:
            geocodes = streetmap.geocode_nominatim(address)
            display(util.html_hbox("Using OpenStreetMap for map data", "info"))

        if len(geocodes) < 1:
            display(util.html_hbox(
                f"Could not find property at {address}",
                "danger"))
        elif len(geocodes) > 1:
            display(util.html_hbox(
                f"{len(geocodes)} matches returned for {address}; all are displayed below",
                "warning"))

        for idx, geocode in enumerate(geocodes):

            if len(geocodes) != 1:
                display(HTML(f"<h3>Property {idx + 1}</h3>"))
            else:
                display(HTML("<h3>Property information</h3>"))
            display(HTML(f"<p><em>{geocode.displayname}</em></p>"))

            property_info = ipywidgets.Box()
            property_info.layout = ipywidgets.Layout(
                display='flex',
                flex_flow='column',
                align_items='stretch',
                width='20em')

            prop_info_child_layout = ipywidgets.Layout(
                display='flex',
                flex_flow='row',
                justify_content='space-between')

            property_info.children = (
                ipywidgets.Box(
                    children=(
                        ipywidgets.Label("County:"),
                        ipywidgets.Label(geocode.county)),
                    layout=prop_info_child_layout),
                ipywidgets.Box(
                    children=(
                        ipywidgets.Label("Neighborhood:"),
                        ipywidgets.Label(geocode.neighborhood)),
                    layout=prop_info_child_layout),
                ipywidgets.Box(
                    children=(
                        ipywidgets.Label("Latitude:"),
                        ipywidgets.Label(str(geocode.coordinates[0]))),
                    layout=prop_info_child_layout),
                ipywidgets.Box(
                    children=(
                        ipywidgets.Label("Longitude:"),
                        ipywidgets.Label(str(geocode.coordinates[1]))),
                    layout=prop_info_child_layout))
            display(property_info)

            if google_api_key != "":
                property_figure = gmaps.figure(center=geocode.coordinates, zoom_level=14)
                property_figure.add_layer(gmaps.marker_layer([geocode.coordinates]))
            else:
                property_figure = ipyleaflet.Map(center=geocode.coordinates, zoom=14)
                property_figure += ipyleaflet.Marker(location=geocode.coordinates)
            display(property_figure)

    return output


street_map_executor = util.DelayedExecutor()  # pylint: disable=C0103


def propertyinfo():
    """Gather information about a property using Jupyter UI elements"""

    def metawrapper(
            loanapr,
            saleprice,
            years,
            overpayment,
            appreciation,
            propertytaxes,
            address,
            google_api_key):
        """Gather information about a property"""
        closed = wrap_close(saleprice, loanapr, years, propertytaxes)
        wrap_schedule(loanapr, closed.principal_total, years, overpayment, appreciation)

        global street_map_executor  # pylint: disable=W0603,C0103
        streetmap_container = ipywidgets.Box()
        display(streetmap_container)
        street_map_executor.run(
            streetmap_container,
            "Loading maps...",
            get_streetmap,
            action_args=(address, google_api_key))

    display(HTML(Template("templ/instructions.mako").render()))

    widgets_box = ipywidgets.Box(layout=ipywidgets.Layout(
        display='flex',
        flex_flow='column',
        align_items='stretch',
        width='70%'))

    loanapr = util.label_widget("APR", widgets_box, ipywidgets.BoundedFloatText(
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
    address = util.label_widget("Property address", widgets_box, ipywidgets.Text(
        value="1600 Pennsylvania Ave NW, Washington, DC 20500"))
    google_api_key = util.label_widget("Google API key (optional)", widgets_box, ipywidgets.Text(
        value=""))

    output = ipywidgets.interactive_output(metawrapper, {
        'loanapr': loanapr,
        'saleprice': saleprice,
        'years': years,
        'overpayment': overpayment,
        'appreciation': appreciation,
        'propertytaxes': propertytaxes,
        'address': address,
        'google_api_key': google_api_key})

    display(widgets_box, output)
