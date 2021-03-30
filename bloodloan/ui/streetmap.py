#!/usr/bin/env python3

"""Mapping functions"""

import json
import logging
import urllib.parse

import ipyleaflet

import namedtupled
import requests


logger = logging.getLogger(__name__)  # pylint: disable=C0103


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
        logger.debug(f"Attempting to get coordinates from URI {uri}")
        httpresults = requests.get(uri).json()
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
