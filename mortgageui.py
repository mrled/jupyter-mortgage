#!/usr/bin/env python3

"""Jupyter wrappers for displaying mortgage information"""

import collections
import os

from IPython.display import (
    HTML,
    display,
)
import ipywidgets

from mako.template import Template

import gmaps
import gmaps.datasets

import googlemaps

import namedtupled

import mortgage


WIDGET_DESC_WIDTH = '10em'


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
        <h1>Rental investment propety worksheet</h1>

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


def wrap_streetmap(address):
    """Show a streetmap"""

    client = googlemaps.Client(key=os.environ["GOOGLE_API_KEY"])
    gmaps.configure(api_key=os.environ["GOOGLE_API_KEY"])

    geocodes = client.geocode(address)

    if len(geocodes) < 1:
        display(HTML(f"<p>Could not find property at {address}</p>"))
    elif len(geocodes) > 1:
        display(HTML(f"<p/><p style='font-size: 150%'>Multiple matches returned for {address}; all are displayed below:</p>"))

    for idx in range(len(geocodes)):

        propertyindex = None
        if len(geocodes) != 1:
            propertyindex = idx + 1

        geocode = namedtupled.map(geocodes[idx])
        # The geocode object will now look something like the following
        # (lol yep there's a 1600 Pennsylvania Avenue, Austin TX)
        # NT(
        #   address_components=[
        #       NT(long_name='1600', short_name='1600', types=['street_number']),
        #       NT(long_name='Pennsylvania Avenue', short_name='Pennsylvania Ave', types=['route']),
        #       NT(long_name='East Austin', short_name='East Austin', types=['neighborhood', 'political']),
        #       NT(long_name='Austin', short_name='Austin', types=['locality', 'political']),
        #       NT(long_name='Travis County', short_name='Travis County', types=['administrative_area_level_2', 'political']),
        #       NT(long_name='Texas', short_name='TX', types=['administrative_area_level_1', 'political']),
        #       NT(long_name='United States', short_name='US', types=['country', 'political']),
        #       NT(long_name='78702', short_name='78702', types=['postal_code'])],
        #   formatted_address='1600 Pennsylvania Ave, Austin, TX 78702, USA',
        #   geometry=NT(
        #       bounds=NT(
        #           northeast=NT(lat=30.2716364, lng=-97.72220109999999),
        #           southwest=NT(lat=30.27142869999999, lng=-97.7223849)),
        #       location=NT(lat=30.2715326, lng=-97.722293),
        #       location_type='ROOFTOP',
        #       viewport=NT(
        #           northeast=NT(lat=30.2728815302915, lng=-97.72094401970848),
        #           southwest=NT(lat=30.2701835697085, lng=-97.72364198029149))),
        #   place_id='ChIJ9XSHLL-1RIYRqAa7cApCto4',
        #   types=['premise'])

        coordinates = (
            geocode.geometry.location.lat,
            geocode.geometry.location.lng)

        county = "UNKNOWN"
        neighborhood = "UNKNOWN"
        for component in geocode.address_components:
            if "administrative_area_level_2" in component.types:
                county = component.long_name
            elif "neighborhood" in component.types:
                neighborhood = component.long_name

        templ = Template(filename='templ/propertyinfo.mako')
        display(HTML(templ.render(
            address=geocode.formatted_address,
            county=county,
            neighborhood=neighborhood,
            coordinates=coordinates,
            propertyindex=propertyindex)))

        fig = gmaps.figure(center=coordinates, zoom_level=14)

        # Drop a pin on the property location
        fig.add_layer(
            gmaps.marker_layer([coordinates]))

        display(fig)


def propertyinfo():
    """Gather information about a property using Jupyter UI elements"""

    def metawrapper(loanapr, saleprice, years, overpayment, appreciation, propertytaxes, address):
        closed = wrap_close(saleprice, loanapr, years, propertytaxes)
        wrap_schedule(loanapr, closed.principal_total, years, overpayment, appreciation)

        display(HTML("<p>Some actions, such as showing a map, are not suited for live updates; to run them, enter the required information and then click 'Run Interact'.</p>"))
        ipywidgets.interact_manual(
            wrap_streetmap,
            address=address)

    def metawrapper_manual(address):
        wrap_streetmap(address)

    ipywidgets.interact(
        metawrapper,
        loanapr=ipywidgets.BoundedFloatText(
            value=3.75,
            min=0.01,
            step=0.25,
            description="APR",
            style={'description_width': WIDGET_DESC_WIDTH}),
        saleprice=ipywidgets.BoundedFloatText(
            value=250_000,
            min=1,
            max=1_000_000_000,
            step=1000,
            description="Sale price",
            style={'description_width': WIDGET_DESC_WIDTH}),
        years=ipywidgets.Dropdown(
            options=[15, 20, 25, 30],
            value=30,
            description="Loan term in years",
            style={'description_width': WIDGET_DESC_WIDTH}),
        overpayment=ipywidgets.BoundedIntText(
            value=50,
            min=0,
            max=1_000_000,
            step=5,
            description="Monthly overpayment amount",
            style={'description_width': WIDGET_DESC_WIDTH}),
        appreciation=ipywidgets.BoundedFloatText(
            value=0.5,
            min=-20.0,
            max=20.0,
            step=0.5,
            description="Yearly appreciation",
            style={'description_width': WIDGET_DESC_WIDTH}),
        propertytaxes=ipywidgets.BoundedIntText(
            value=5500,
            min=0,
            max=1_000_000,
            step=5,
            description="Yearly property taxes",
            style={'description_width': WIDGET_DESC_WIDTH}),
        address=ipywidgets.Text(
            value="1600 Pennsylvania Ave NW, Washington, DC 20500",
            description="Address",
            style={'description_width': WIDGET_DESC_WIDTH}))

    # display(HTML("<p>Some actions, such as showing a map, are not suited for live updates; to run them, enter the required information and then click 'Run Interact'.</p>"))
    # ipywidgets.interact_manual(
    #     wrap_streetmap,
    #     address=ipywidgets.Text(
    #         value="",
    #         description="Address",
    #         style={'description_width': WIDGET_DESC_WIDTH}))
