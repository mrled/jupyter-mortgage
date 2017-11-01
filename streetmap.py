#!/usr/bin/env python3

"""Mapping functions"""

import json
import urllib.parse
import urllib.request

import googlemaps

import namedtupled


class GeocodeResult():
    """The result of a reverse geocode lookup"""

    coordinates = None
    displayname = ""
    neighborhood = "Unknown"
    county = "Unknown"

    def __init__(self, coordinates=None, displayname="", neighborhood="Unknown", county="Unknown"):
        self.coordinates = coordinates or ()
        self.displayname = displayname
        self.neighborhood = neighborhood
        self.county = county


def geocode_nominatim(address):
    uritempl = "http://nominatim.openstreetmap.org/search/{0}?format=json&addressdetails=1&extratags=1&namedetails=1&dedupe=1"
    uri = uritempl.format(urllib.parse.quote(address))
    with urllib.request.urlopen(uri) as resulthandle:
        httpresults = json.loads(resulthandle.read())
    georesults = []
    for result in httpresults:
        try:
            coordinates = (result['lat'], result['lon'])
        except KeyError:
            coordinates = ()
        try:
            displayname = result['display_name']
        except KeyError:
            displayname = ""
        try:
            neighborhood = result['address']['neighborhood']
        except KeyError:
            neighborhood = "Unknown"
        try:
            county = result['address']['county']
        except KeyError:
            county = "Unknown"
        georesults.append(GeocodeResult(coordinates, displayname, neighborhood, county))
    return georesults


def geocode_google(address, google_api_key):
    client = googlemaps.Client(key=google_api_key)
    geocodes = client.geocode(address)
    georesults = []
    for idx in range(len(geocodes)):
        geocode = namedtupled.map(geocodes[idx])

        coordinates = (
            geocode.geometry.location.lat,
            geocode.geometry.location.lng)
        displayname = geocode.formatted_address

        county = "Unknown"
        neighborhood = "Unknown"
        for component in geocode.address_components:
            if "administrative_area_level_2" in component.types:
                county = component.long_name
            elif "neighborhood" in component.types:
                neighborhood = component.long_name

        georesults.append(GeocodeResult(coordinates, displayname, neighborhood, county))
    return georesults
