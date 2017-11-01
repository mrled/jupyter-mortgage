# Street map documentation

I have used both Google Maps and OpenStreetMaps for map data

## Reverse geocode searching with Nominatim

My `streetmap.geocode_nominatim()` function uses [Nominatim](https://wiki.openstreetmap.org/wiki/Nominatim) for a reverse geocode search - that is, searching for a geocode by address.

The main reason I wanted to do this was that it doesn't require an API key, like Google does - so you can actually just paste the URL below in your browser and it'll show the JSON result immediately. Firefox, and possibly some other browsers, will even format the JSON nicely for you automatically.

To look up the address of the White House, `1600 Pennsylvania Ave NW, Washington, DC 20500`, query the Nominatim HTTP endpoint like this: `http://nominatim.openstreetmap.org/search/1600%20Pennsylvania%20Ave%20NW%2C%20Washington%2C%20DC%2020500?format=json&addressdetails=1&extratags=1&namedetails=1`. The result of that query looks like this as of 2017-11-01:

    [
        {
            "place_id": "127954863",
            "licence": "Data \u00a9 OpenStreetMap contributors, ODbL 1.0. http://www.openstreetmap.org/copyright",
            "osm_type": "way",
            "osm_id": "238241022",
            "boundingbox": [
                "38.8974898",
                "38.897911",
                "-77.0368542",
                "-77.0362526"
            ],
            "lat": "38.8976998",
            "lon": "-77.0365534886228",
            "display_name": "White House, 1600, Pennsylvania Avenue Northwest, Golden Triangle, Washington, District of Columbia, 20500, United States of America",
            "class": "office",
            "type": "government",
            "importance": 0.6819189346824,
            "address": {
                "address29": "White House",
                "house_number": "1600",
                "pedestrian": "Pennsylvania Avenue Northwest",
                "neighbourhood": "Golden Triangle",
                "city": "Washington",
                "state": "District of Columbia",
                "postcode": "20500",
                "country": "United States of America",
                "country_code": "us"
            },
            "extratags": {
                "image": "http://upload.wikimedia.org/wikipedia/commons/a/af/WhiteHouseSouthFacade.JPG",
                "wikidata": "Q35525",
                "wikipedia": "en:White House",
                "wheelchair": "yes",
                "wikipedia:de": "Wei\u00dfes Haus",
                "wikipedia:es": "Casa Blanca",
                "wikipedia:fr": "Maison-Blanche",
                "wikipedia:it": "Casa Bianca"
            },
            "namedetails": {
                "name": "White House",
                "name:de": "Wei\u00dfes Haus",
                "name:en": "White House",
                "name:fa": "\u06a9\u0627\u062e \u0633\u0641\u06cc\u062f",
                "name:fr": "Maison Blanche",
                "name:hu": "Feh\u00e9r H\u00e1z",
                "name:it": "Casa Bianca",
                "name:ja": "\u30db\u30ef\u30a4\u30c8\u30cf\u30a6\u30b9",
                "name:ko": "\ubc31\uc545\uad00",
                "name:pt": "Casa Branca",
                "name:ro": "Casa Alb\u0103",
                "name:sk": "Biely dom",
                "name:uk": "\u0411\u0456\u043b\u0438\u0439 \u0434\u0456\u043c",
                "name:zh": "\u767d\u5bae",
                "addr:housename": "The White House"
            }
        },
        {
            "place_id": "125028570",
            "licence": "Data \u00a9 OpenStreetMap contributors, ODbL 1.0. http://www.openstreetmap.org/copyright",
            "osm_type": "way",
            "osm_id": "238241016",
            "boundingbox": [
                "38.8973238",
                "38.8976897",
                "-77.0378226",
                "-77.0372952"
            ],
            "lat": "38.8974983",
            "lon": "-77.0375590052579",
            "display_name": "The West Wing, 1600, Pennsylvania Avenue Northwest, Golden Triangle, Washington, District of Columbia, 20500, United States of America",
            "class": "office",
            "type": "government",
            "importance": 0.61787433190242,
            "address": {
                "address29": "The West Wing",
                "house_number": "1600",
                "pedestrian": "Pennsylvania Avenue Northwest",
                "neighbourhood": "Golden Triangle",
                "city": "Washington",
                "state": "District of Columbia",
                "postcode": "20500",
                "country": "United States of America",
                "country_code": "us"
            },
            "extratags": {
                "wikidata": "Q1932621",
                "wikipedia": "en:West Wing",
                "wheelchair": "yes"
            },
            "namedetails": {
                "name": "The West Wing",
                "name:de": "Westfl\u00fcgel",
                "name:en": "The West Wing",
                "addr:housename": "The West Wing"
            }
        },
        {
            "place_id": "125400138",
            "licence": "Data \u00a9 OpenStreetMap contributors, ODbL 1.0. http://www.openstreetmap.org/copyright",
            "osm_type": "way",
            "osm_id": "238241018",
            "boundingbox": [
                "38.8973817",
                "38.897768",
                "-77.0357843",
                "-77.0355017"
            ],
            "lat": "38.89756155",
            "lon": "-77.0356429619915",
            "display_name": "The East Wing, 1600, Pennsylvania Avenue Northwest, Golden Triangle, Washington, District of Columbia, 20500, United States of America",
            "class": "office",
            "type": "government",
            "importance": 0.60415391385023,
            "address": {
                "address29": "The East Wing",
                "house_number": "1600",
                "pedestrian": "Pennsylvania Avenue Northwest",
                "neighbourhood": "Golden Triangle",
                "city": "Washington",
                "state": "District of Columbia",
                "postcode": "20500",
                "country": "United States of America",
                "country_code": "us"
            },
            "extratags": {
                "wikidata": "Q2777428",
                "wikipedia": "en:East Wing",
                "wheelchair": "yes"
            },
            "namedetails": {
                "name": "The East Wing",
                "name:de": "Ostfl\u00fcgel",
                "name:en": "The East Wing",
                "addr:housename": "The East Wing"
            }
        }
    ]


## Reverse geocode searching with Google

Google reverse geocoding works like this, which uses the official `googlemaps` Python module from Google, and `namedtupled` which is a third party module (_not_ the built-in `collections.namedtuple`) that makes it easier for us:

    client = googlemaps.Client(key=os.environ["GOOGLE_API_KEY"])
    geocodes = client.geocode(address)
    for idx in range(len(geocodes)):
        geocode = namedtupled.map(geocodes[idx])

If my address was `1600 Pennsylvania Avenue, Austin TX` (lol yep, there's a 1600 Pennsylvania Ave in Austin), the `geocode` object will now look something like the following:

    NT(
        address_components=[
            NT(long_name='1600', short_name='1600', types=['street_number']),
            NT(long_name='Pennsylvania Avenue', short_name='Pennsylvania Ave', types=['route']),
            NT(long_name='East Austin', short_name='East Austin', types=['neighborhood', 'political']),
            NT(long_name='Austin', short_name='Austin', types=['locality', 'political']),
            NT(long_name='Travis County', short_name='Travis County', types=['administrative_area_level_2', 'political']),
            NT(long_name='Texas', short_name='TX', types=['administrative_area_level_1', 'political']),
            NT(long_name='United States', short_name='US', types=['country', 'political']),
            NT(long_name='78702', short_name='78702', types=['postal_code'])],
        formatted_address='1600 Pennsylvania Ave, Austin, TX 78702, USA',
        geometry=NT(
            bounds=NT(
                northeast=NT(lat=30.2716364, lng=-97.72220109999999),
                southwest=NT(lat=30.27142869999999, lng=-97.7223849)),
            location=NT(lat=30.2715326, lng=-97.722293),
            location_type='ROOFTOP',
            viewport=NT(
                northeast=NT(lat=30.2728815302915, lng=-97.72094401970848),
                southwest=NT(lat=30.2701835697085, lng=-97.72364198029149))),
        place_id='ChIJ9XSHLL-1RIYRqAa7cApCto4',
        types=['premise'])
