#!/usr/bin/env python3

"""Jupyter wrappers for displaying mortgage information"""

import os

from IPython.display import (
    HTML,
    display,
)
import ipywidgets

import gmaps
import gmaps.datasets

import googlemaps

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


def streetmap():
    client = googlemaps.Client(key=os.environ["GOOGLE_API_KEY"])
    gmaps.configure(api_key=os.environ["GOOGLE_API_KEY"])

    def f(address):
        geocode = client.geocode(address)
        if len(geocode) != 1:
            raise Exception(f"Expected just one result for address, but got {len(geocode)}")

        # for component in geocode[0]['address_components']:
        #     if 'administrative_area_level_2' in component['types']:
        #         county = component['long_name']
        #         break
        # if not county:
        #     raise Exception("Could not find county")
        # for component in geocode[0]['address_components']:
        #     if 'postal_code' in component['types']:
        #         zipcode = component['long_name']
        #         break
        # if not zipcode:
        #     raise Exception("Could not find zip code")
        # for component in geocode[0]['address_components']:
        #     if 'postal_code_suffix' in component['types']:
        #         zipcode = f"{zipcode}-{component['long_name']}"
        #         break
        # if len(zipcode) != 10:
        #     raise Exception("Could not find zipcode suffix")

        # prettyaddr = geocode[0]['formatted_address']

        coordinates = (
            geocode[0]['geometry']['location']['lat'],
            geocode[0]['geometry']['location']['lng'])

        fig = gmaps.figure(center=coordinates, zoom_level=6)
        
        # display(fig)
        fig

    AddressWidget = ipywidgets.Text(
        value="1600 Pennsylvania Ave SE, Washington, DC 20003",
        description="Property address")

    widget = ipywidgets.interactive(
        f,
        address=AddressWidget)

    display(widget)
