#!/usr/bin/env python3

"""Mapping functions"""

import json
import urllib.parse
import urllib.request

import gmaps
import googlemaps

import ipyleaflet

import namedtupled


class GeocodeResult():
    """The result of a geocode lookup"""

    def __init__(
            self,
            coordinates=None,
            displayname="",
            neighborhood="Unknown",
            county="Unknown",
            figure=None):
        """Initialize

        coordinates     tuple containing (lat, long) coordinates
        displayname     address of the property, including title if any, from the maps API
        neighborhood    neighborhood where the coordinates are located
        county          county where the coordinates are located
        figure          display()-able streetmap of the coordinates
        """
        self.coordinates = coordinates or ()
        self.displayname = displayname
        self.neighborhood = neighborhood
        self.county = county
        self.figure = figure


class MapperInterface():
    """An abstract class intended as an interface for different mapping backends"""

    def __str__(self):
        """Describe the mapper for an end user"""
        raise NotImplementedError("NOT IMPLEMENTED")

    def geocode(self, address, zoomlevel):
        """Return list of GeocodeResult objects for an address

        address     address to look up
        zoomlevel   zoom level for the display()-able map of each result
        """
        raise NotImplementedError("NOT IMPLEMENTED")


class GoogleMapper(MapperInterface):
    """Retrieve mapping data from Google"""

    def __init__(self, apikey):
        self.apikey = apikey
        gmaps.configure(api_key=apikey)

    def __str__(self):
        return "Google Maps"

    def geocode(self, address, zoomlevel=14):
        client = googlemaps.Client(key=self.apikey)
        geocodes = client.geocode(address)
        georesults = []

        for idx, geocode in enumerate(geocodes):
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

            figure = self.map(geocode.coordinates, zoomlevel)
            georesults.append(GeocodeResult(
                coordinates, displayname, neighborhood, county, figure))

        return georesults

    def map(self, coordinates, zoomlevel):
        """Return a display()-able map for coordinates"""
        figure = gmaps.figure(center=coordinates, zoom_level=zoomlevel)
        figure.add_layer(gmaps.marker_layer([coordinates]))
        return figure


class OpenStreetMapper(MapperInterface):
    """Retrieve mapping data from OpenStreetMap"""

    def __str__(self):
        return "OpenStreetMap"

    def geocode(self, address, zoomlevel=14):
        uritempl = "".join([
            "http://nominatim.openstreetmap.org/search/",
            "{0}",
            "?format=json&addressdetails=1&extratags=1&namedetails=1&dedupe=1"])
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
            figure = self.map(coordinates, zoomlevel)
            georesults.append(GeocodeResult(
                coordinates, displayname, neighborhood, county, figure))
        return georesults

    def map(self, coordinates, zoomlevel):
        """Return a display()-able map for coordinates"""
        figure = ipyleaflet.Map(center=coordinates, zoom=zoomlevel)
        figure += ipyleaflet.Marker(location=coordinates)
        return figure
