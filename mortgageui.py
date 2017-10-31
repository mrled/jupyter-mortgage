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
    """
    return '${:,.2f}'.format(amount)


def schedule():
    """Show a loan's mortgage schedule in a Jupyter notebook"""

    def wrap_schedule(apryearly, principal, years, overpayment, appreciation):
        """Show a loan's mortgage schedule in a Jupyter notebook"""

        term = years * mortgage.MONTHS_IN_YEAR
        overpayments = [overpayment for _ in range(term)]
        appreciationpct = appreciation / 100
        months = [month for month in mortgage.schedule(apryearly, principal, term, overpayments=overpayments, appreciation=appreciationpct)]
        years = [year for year in mortgage.monthly2yearly_schedule(months)]
        schedtempl = Template(filename='templ/schedule.mako')

        # Create new Output objects, and call display(HTML(...)) in them
        # We do this because IPython.display.HTML() has nicer talbles
        # than ipywidgets.HTML(), but only ipywidgets-type widgets can be put
        # into an Accordion.
        summaryout = ipywidgets.Output()
        detailout = ipywidgets.Output()
        with summaryout:
            display(HTML(schedtempl.render(
                apryearly=apryearly,
                principal=principal,
                term=term,
                overpayment=overpayment,
                appreciation=appreciation,
                monthlypayments=months,
                yearlypayments=years)))
        with detailout:
            display(HTML(schedtempl.render(
                apryearly=apryearly,
                principal=principal,
                term=term,
                overpayment=overpayment,
                appreciation=appreciation,
                monthlypayments=months,
                yearlypayments=None)))

        parentwidg = ipywidgets.Accordion()
        parentwidg.children = [summaryout, detailout]
        parentwidg.set_title(0, 'Yearly summary')
        parentwidg.set_title(1, 'Monthly detail')
        display(parentwidg)

    ipywidgets.interact(
        wrap_schedule,
        apryearly=ipywidgets.BoundedFloatText(
            value=3.75,
            min=0.01,
            step=0.25,
            description="APR",
            style={'description_width': WIDGET_DESC_WIDTH}),
        principal=ipywidgets.BoundedIntText(
            value=250_000,
            min=1,
            max=1_000_000_000,
            step=1000,
            description="Loan amount",
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
            style={'description_width': WIDGET_DESC_WIDTH}))#,


def streetmap():
    """Show a street map in a Jupyter notebook"""

    client = googlemaps.Client(key=os.environ["GOOGLE_API_KEY"])
    gmaps.configure(api_key=os.environ["GOOGLE_API_KEY"])

    def wrap_streetmap(address):
        """Show a streetmap"""

        for geocode_dict in client.geocode(address):

            geocode = namedtupled.map(geocode_dict)
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
                coordinates=coordinates)))

            fig = gmaps.figure(center=coordinates, zoom_level=14)

            # Drop a pin on the property location
            fig.add_layer(
                gmaps.marker_layer([coordinates]))

            display(fig)

    display(HTML("<p>Enter an address, then click the 'Run Interact' button to show a map</p>"))

    ipywidgets.interact_manual(
        wrap_streetmap,
        address=ipywidgets.Text(
            value="1600 Pennsylvania Ave SE, Washington, DC 20003",
            description="Address"))


def close():
    """Show loan amounts and closing costs"""

    def wrap_close(saleprice, loanapr, loanterm, propertytaxes):
        """Show loan amounts and closing costs"""
        costs = mortgage.IRONHARBOR_FHA_CLOSING_COSTS
        result = mortgage.close(saleprice, loanapr, loanterm, propertytaxes, costs)

        templ = Template(filename='templ/close.mako')
        display(HTML(templ.render(closeresult=result)))

    ipywidgets.interact(
        wrap_close,
        saleprice=ipywidgets.BoundedFloatText(
            value=250_000,
            min=1,
            max=1_000_000_000,
            step=1000,
            description="Sale price",
            style={'description_width': WIDGET_DESC_WIDTH}),
        loanapr=ipywidgets.BoundedFloatText(
            value=3.75,
            min=0.01,
            step=0.25,
            description="APR",
            style={'description_width': WIDGET_DESC_WIDTH}),
        loanterm=ipywidgets.Dropdown(
            options=[15, 20, 25, 30],
            value=30,
            description="Loan term in years",
            style={'description_width': WIDGET_DESC_WIDTH}),
        propertytaxes=ipywidgets.BoundedIntText(
            value=5500,
            min=0,
            max=1_000_000,
            step=5,
            description="Yearly property taxes",
            style={'description_width': WIDGET_DESC_WIDTH}))
