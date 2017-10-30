#!/usr/bin/env python3

"""Jupyter wrappers for displaying mortgage information"""

import collections
import os

from IPython.display import (
    HTML,
    display,
)
import ipywidgets

import gmaps
import gmaps.datasets

import googlemaps

import namedtupled

import mortgage


def dollar(amount):
    """Return a string dollar amount from a float

    For example, dollar(1926.2311831442486) => "$1,926.23"

    We aren't too concerned about the lost accuracy;
    this function should only be used for *display* values
    """
    return '${:,.2f}'.format(amount)


def htmlschedule(apryearly, principal, term, overpayment, loanpayments, yearly=False):
    """Create an HTML table of a loan schedule

    apryearly:      yearly APR of the loan
    principal:      total amount of the loan
    term:           loan term in months
    overpayment:    an extra amount to apply to *every* month's loan principal
    loanpayments:   array of LoanPayment objects
    """

    htmlstr  = "<h1>Mortgage amortization schedule</h1>"
    htmlstr += "<p>"
    # Not sure why I need the <span> here,
    # but if I don't include it Jupyter does something really fucked up to my text
    htmlstr += f"Amortization schedule for a <span>{dollar(principal)}</span> loan "
    htmlstr += f"over {term} months "
    htmlstr += f"at {apryearly}% interest, "
    htmlstr += f"including a {dollar(overpayment)} overpayment each month."
    htmlstr += "</p>"

    htmlstr += "<table>"

    htmlstr += "<tr>"
    if yearly:
        htmlstr += "<th>Year</th>"
    else:
        htmlstr += "<th>Month</th>"
    htmlstr += "<th>Regular payment</th>"
    htmlstr += "<th>Interest</th>"
    htmlstr += "<th>Balance</th>"
    htmlstr += "<th>Overpayment</th>"
    htmlstr += "<th>Remaining principal</th>"
    htmlstr += "</tr> "

    htmlstr += "<tr>"
    htmlstr += "<td>Initial loan amount</td>"
    htmlstr += "<td></td>"
    htmlstr += "<td></td>"
    htmlstr += "<td></td>"
    htmlstr += "<td></td>"
    htmlstr += f"<td>{dollar(principal)}</td>"
    htmlstr += "</tr> "

    for payment in loanpayments:
        htmlstr += "<tr>"
        htmlstr += f"<td>{payment.index}</td>"
        htmlstr += f"<td>{dollar(payment.totalpmt)}</td>"
        htmlstr += f"<td>{dollar(payment.interestpmt)}</td>"
        htmlstr += f"<td>{dollar(payment.balancepmt)}</td>"
        htmlstr += f"<td>{dollar(payment.overpmt)}</td>"
        htmlstr += f"<td>{dollar(payment.principal)}</td>"
        htmlstr += "</tr> "

    htmlstr += "</table>"

    return htmlstr


def schedule():
    """Show a loan's mortgage schedule in a Jupyter notebook"""

    def f(apryearly, principal, years, overpayment, period):
        term = years * mortgage.MONTHS_IN_YEAR
        months = mortgage.schedule(apryearly, principal, term, [overpayment for _ in range(term)])
        if period == "Monthly detail":
            display(HTML(htmlschedule(apryearly, principal, term, overpayment, months)))
        elif period == "Yearly summary":
            years = mortgage.monthly2yearly_schedule(months)
            display(HTML(htmlschedule(apryearly, principal, term, overpayment, years, yearly=True)))
        else:
            raise Exception(f"Invalid period: '{period}'")

    desc_width = '10em'

    apr_widget = ipywidgets.FloatText(
        value=3.75,
        description="APR",
        style={'description_width': desc_width})
    principal_widget = ipywidgets.IntText(
        value=250_000,
        description="Loan amount",
        style={'description_width': desc_width})
    term_widget = ipywidgets.Dropdown(
        options=[15, 20, 25, 30],
        value=30,
        description="Loan term in years",
        style={'description_width': desc_width})
    overpayment_widget = ipywidgets.IntText(
        value=0,
        description="Monthly overpayment amount",
        style={'description_width': desc_width})
    period_widget = ipywidgets.Dropdown(
        options=["Yearly summary", "Monthly detail"],
        description="Report type",
        style={'description_width': desc_width})

    widget = ipywidgets.interactive(
        f,
        apryearly=apr_widget,
        principal=principal_widget,
        years=term_widget,
        overpayment=overpayment_widget,
        period=period_widget)

    display(widget)


def streetmap():
    """Show a street map in a Jupyter notebook"""

    client = googlemaps.Client(key=os.environ["GOOGLE_API_KEY"])
    gmaps.configure(api_key=os.environ["GOOGLE_API_KEY"])

    def f(address):

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

            htmlstr  = "<h1>Property information</h1>"
            htmlstr += "<table>"
            htmlstr += f"<tr><th>Address:</th><td>{geocode.formatted_address}</td></tr>"
            htmlstr += f"<tr><th>County:</th><td>{county}</td></tr>"
            htmlstr += f"<tr><th>Neighborhood:</th><td>{neighborhood}</td></tr>"
            htmlstr += f"<tr><th>Coordinates:</th><td>{coordinates}</td></tr>"
            htmlstr += "</table>"
            display(HTML(htmlstr))

            fig = gmaps.figure(center=coordinates, zoom_level=14)

            # Drop a pin on the property location
            fig.add_layer(
                gmaps.marker_layer([coordinates]))

            display(fig)

    address_widget = ipywidgets.Text(
        value="1600 Pennsylvania Ave SE, Washington, DC 20003",
        description="Property address")

    print("Enter an address, then click the 'Run Interact' button to show a map")

    ipywidgets.interact_manual(
        f,
        address=address_widget)
