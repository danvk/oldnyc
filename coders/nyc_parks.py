#!/usr/bin/python
#
# Look for well-known NYC parks.


import fileinput
import re
import sys
from collections import defaultdict

import coders.registration
from data.item import Item, blank_item

# TODO: move these into a data file, maybe GeoJSON
parks = {
    "Bronx Park": (40.856389, -73.876667),
    "Claremont Park": (40.840546, -73.907469),
    "Crotona Park": (40.8388, -73.8952),
    # 'Fulton Park': None,
    "Morris Park Race Track": (40.85, -73.855556),
    "Poe Park": (40.865278, -73.894444),
    "Pulaski Park": (40.805239, -73.924409),
    "Starlight Park": (40.834176, -73.881968),
    "Highland Park": (40.688370, -73.887480),
    "Marine Park": (40.59804, -73.92083),
    "Prospect Park Plaza": (40.6743, -73.9702),
    "Prospect Park": (40.66143, -73.97035),  # BIG!
    "Battery Park": (40.703717, -74.016094),
    "Bryant Park": (40.753792, -73.983607),
    "Central Park": (40.782865, -73.965355),  # BIG!
    "Colonial Park": (40.824293, -73.942172),
    "Cooper Park": (40.716014, -73.937268),
    "Jefferson Park": (40.793366, -73.935247),
    "Morningside Park": (40.805093, -73.959127),
    "Riverside Park": (40.801234, -73.972310),
    "Astoria Park": (40.775934, -73.925275),
    "Baisley Park": (40.677778, -73.784722),
    "Chisholm Park": (40.792833, -73.851857),
    "Rainey Park": (40.766070, -73.940758),
    "Barrett Park": (40.6251, -74.1157),
    "Flushing Meadow Park": (40.739714, -73.840785),
    "City Hall Park": (40.713160, -74.006389),
    "Pelham Bay Park": (40.861500, -73.797200),
    "Van Cortlandt Park": (40.894709, -73.890918),
    "Inwood Hill Park": (40.871542, -73.925695),
    "Carl Schurz Park": (40.775130, -73.943697),
    "Jacob Riis Park": (40.566623, -73.876081),
    "High Bridge Park": (40.843104, -73.932910),
    "Fort Tryon Park": (40.861619, -73.933622),
    "Fort Greene Park": (40.690344, -73.973833),
    "Morris Park": (40.852201, -73.850728),  # Neighborhood
    "Fort Washington Park": (40.849475, -73.946673),
    "Washington Square Park": (40.730823, -73.997332),
    "Mount Morris Park": (40.804508, -73.944046),
    "Union Square Park": (40.735708, -73.990442),
    "Stuyvesant Square Park": (40.733611, -73.984000),
    "Juniper Valley Park": (40.720101, -73.881488),
    "Starlight Amusement Park": (40.834176, -73.881968),
    "Seton Falls Park": (40.886753, -73.838231),
    "Madison Square Park": (40.742216, -73.988036),
    "Golden City Park": (40.629194, -73.883929),
    "Golden City Amusement Park": (40.629194, -73.883929),
    "Corlears Hook Park": (40.711697, -73.979697),
    "College Point Park": (40.785778, -73.846501),
    "Marine Park at Marine Park": (40.595700, -73.921198),
    "Hamilton Fish Park": (40.720029, -73.981559),
    "Garden City Amusement Park": (40.629194, -73.883929),
    # 'Fulton Park': (),
    "Fort Green Park": (40.690344, -73.973833),
    "Canarsie Beach Park": (40.629194, -73.883929),
}

central_park = {
    "The Pond": (40.766014, -73.974004),
    "Pond in winter": (40.766014, -73.974004),
    "The Lake": (40.776223, -73.973085),
    "Reservoirs - Lower reservoir": (40.781289, -73.966664),
    "Reservoirs - Upper reservoir": (40.785719, -73.963902),
    # 'Pathways': (),
    "The Mall": (40.772352, -73.971590),
    # 'Playgrounds': (),
    # 'Transverse roads': (),
    # 'Miscellaneous': (),
    "Bridal path": (40.796840, -73.957826),
    "[View of the Arsenal Building]": (40.767618, -73.971311),
    # 'The Seal Pool': (),
    "The Obelisk": (40.779638, -73.965400),
    "Transportation of the Obelisk": (40.779638, -73.965400),
    "Terrace Fountain and the Lake": (40.753982, -73.984127),
    # 'looking west from Fifth Avenue apartment': (),
    # 'Sailboat pond': (),
    # 'Rustic Arbor': (),
    "Harlem Mere": (40.796464, -73.951596),
    # 'West Drive': (),
    # 'The Sailboat Pool': (),
    # 'Drives': (),
    # 'Cliffs': (),
}


islands = {
    "Barren Island": (40.592778, -73.893056),
    "Barren": (40.592778, -73.893056),
    "Bedloe's Island": (40.690050, -74.045068),
    "City Island": (40.846820, -73.787498),
    "City": (40.846820, -73.787498),
    "Coney Island beach": (40.572130, -73.979330),
    "Coney Island pier": (40.571413, -73.983822),
    "Coney Island": (40.574926, -73.985941),
    "Coney": (40.574926, -73.985941),
    "Ellis Island": (40.699472, -74.039560),
    "Ellis": (40.699472, -74.039560),
    "Governor's Island": (40.689450, -74.016792),
    "Governors Island": (40.689450, -74.016792),
    "Governors": (40.689450, -74.016792),
    "Hart's Island": (40.853627, -73.770585),
    "High Island": (40.859525, -73.785639),
    "Hoffman Island": (40.578873, -74.053688),
    "Hoffman": (40.578873, -74.053688),
    "Hunter Island": (40.875028, -73.790219),
    "Hunter": (40.875028, -73.790219),
    "North Brother Island": (40.800720, -73.898137),
    "North Brothers Island": (40.800720, -73.898137),
    "North Brothers": (40.800720, -73.898137),
    "North Brother": (40.800720, -73.898137),
    "Plumb Island": (40.584722, -73.915000),
    "Randall's Island": (40.793227, -73.921286),
    "Randalls Island": (40.793227, -73.921286),
    "Rikers Island": (40.793128, -73.886010),
    "Shooters Island": (40.643333, -74.159722),
    "South Brother Island": (40.796402, -73.898137),
    "South Brother": (40.796402, -73.898137),
    "Ward's Island": (40.793227, -73.921286),
    "Welfare Island": (40.762161, -73.949964),
    "Welfare": (40.762161, -73.949964),
}

bridges = {
    "Brooklyn Bridge": (40.706096, -73.996823),
    "Triborough Bridge": (40.788232, -73.927871),
    "triborough Bridge": (40.788232, -73.927871),
    "Triborough Bridge and": (40.788232, -73.927871),
    "Queensboro Bridge": (40.756732, -73.954224),
    "Queensborough Bridge": (40.756732, -73.954224),
    "Manhattan Bridge": (40.707471, -73.990774),
    "George Washington Bridge": (40.850425, -73.945942),
    "Washington Bridge": (40.846944, -73.928056),
    "Hell Gate Bridge": (40.782596, -73.921913),
    "Williamsburg Bridge": (40.713690, -73.972616),
    "Harlem River Bridges": (40.815139, -73.933096),
    "Bayonne Bridge": (40.639706, -74.142963),
    "Kill Van Kull Bridge": (40.639706, -74.142963),
    "High Bridge": (40.842308, -73.930277),
    "Penny Bridge": (40.72777, -73.9292),
    "Washington Bridge over Harlem River": (40.846944, -73.928056),
    "Verrazano Narrows Bridge": (40.606589, -74.044648),
    "Triborough and Hell Gate Bridge": (40.788232, -73.927871),
    "Northern Boulevard Bridge": (40.763428, -73.751743),
    "Marine Parkway Bridge": (40.573697, -73.885145),
    "Lemon Creek Bridge": (40.521727, -74.202524),
    "Kosciusko Bridge": (40.72777, -73.9292),
    "Henry Hudson Bridge": (40.877713, -73.922302),
    "Gowanus Canal Bridge": (40.674106, -73.996503),
    "Ninth Street drawbridge Bridge": (40.674106, -73.996503),
    "Vernon Boulevard Bridge": (40.760673, -73.943330),
    "Triborough and Hell Gate Bridges": (40.788232, -73.927871),
    "Henry Hudson Memorial Bridge": (40.877713, -73.922302),
    "Goethals Bridge": (40.635381, -74.195978),
    #   2	'Flushing Creek Bridge': (),
    #   2	'City Island Bridge': (),
    #   2	'Broadway Bridge': (),
    #   2	'Bridge over Coney Island': ()
    #   1	Throgs Neck Bridge
    #   1	Strongs Causeway Bridge
    #   1	Pelham Bridge
    #   1	Outerbridge Crossing site Bridge
    #   1	Outerbridge Crossing Bridge
    #   1	New York and Putnam Railroad Bridge
    #   1	New York Central Railroad Bridge
    #   1	Metropolitan Avenue Bridge
    #   1	Madison Avenue Bridge
    #   1	Kosciusko Bridge over Newtown Creek in
    #   1	Kings Bridge
    #   1	Hells Gate Bridge
    #   1	Hell Gate and Triborough Bridge
    #   1	Harlem River Bridge
    #   1	Flushing River Bridge
    #   1	Farmers Bridge
    #   1	East River Bridge
    #   1	Cross Bay Veterans Memorial Bridge
    #   1	Cross Bay Boulevard Bridge
    #   1	Brroklyn Bridge
    #   1	Brooklyn and Manhattan Bridges over East
    #   1	Baltimore and Ohio Railroad Bridge
}

# Bridges
# "East River - River scenes - View of Brooklyn Bridge and financial district from Manhattan Bridge"
# "East River - River scenes - Brooklyn Bridge -Early shipping."

# Beaches
# - Midland Beach, Staten Island, NY

boros_re = "(?:New York|Manhattan|Brooklyn|Bronx|Queens|Staten Island)"
park_re = r"^%s: ([A-Za-z ]+ Park)(?: |$)" % boros_re
non_parks_re = r"Park (?:Avenue|West|East|North|South|Court|Place|Row|Terrace|Blvd|Boulevard)"

island_re = r"^Islands - ([A-Za-z ]+) "
bridge_re = r"^Bridges - ([A-Za-z ]+) "

missing_parks = defaultdict(int)
missing_islands = defaultdict(int)
missing_bridges = defaultdict(int)


class NycParkCoder:
    def __init__(self):
        pass

    def codeRecord(self, r: Item):
        title = re.sub(r"\.$", "", r.title)

        m = re.search(park_re, title)
        if m:
            park = m.group(1)
            if not re.search(non_parks_re, title):
                if park not in parks:
                    missing_parks[park] += 1
                else:
                    latlon = None
                    if park == "Central Park":
                        for place in central_park:
                            if ("Central Park - %s" % place) in title:
                                latlon = central_park[place]
                    if not latlon:
                        latlon = parks[park]
                    return {
                        "address": "@%s,%s" % latlon,
                        "source": m.group(0),
                        "type": "point_of_interest",
                    }

        m = re.search(island_re, title)
        if m:
            island = m.group(1)
            if island not in islands:
                missing_islands[island] += 1
            else:
                latlon = islands[island]
                return {
                    "address": "@%s,%s" % latlon,
                    "source": m.group(0),
                    "type": "point_of_interest",
                }

        m = re.search(bridge_re, title)
        if m:
            bridge = m.group(1)
            # if not ('Bridge' in bridge or 'bridge' in bridge):
            # XXX this is weird
            if not "Bridge" in bridge or "bridge" in bridge:  # noqa: E713
                bridge += " Bridge"
            if bridge not in bridges:
                missing_bridges[bridge] += 1
            else:
                latlon = bridges[bridge]
                return {
                    "address": "@%s,%s" % latlon,
                    "source": m.group(0),
                    "type": "point_of_interest",
                }

        return None

    def _getLatLonFromGeocode(self, geocode, data):
        for result in geocode["results"]:
            # data['type'] is something like 'address' or 'intersection'.
            if data["type"] in result["types"]:
                loc = result["geometry"]["location"]
                return (loc["lat"], loc["lng"])

    def getLatLonFromGeocode(self, geocode, data, r: Item):
        latlon = self._getLatLonFromGeocode(geocode, data)
        if not latlon:
            return None
        return latlon

    def finalize(self):
        for missing in [missing_parks, missing_islands, missing_bridges]:
            vs = [(v, k) for k, v in missing.items()]
            for v, k in reversed(sorted(vs)):
                sys.stderr.write("%4d\t%s\n" % (v, k))

    def name(self):
        return "nyc-parks"


coders.registration.registerCoderClass(NycParkCoder)


# For fast iteration
if __name__ == "__main__":
    coder = NycParkCoder()
    r = blank_item()
    num_ok, num_bad = 0, 0
    for line in fileinput.input():
        addr = line.strip()
        if not addr:
            continue
        r.address = addr
        result = coder.codeRecord(r)

        if result:
            num_ok += 1
            print('"%s" -> %s' % (addr, result))
        else:
            num_bad += 1

    coder.finalize()

    sys.stderr.write(
        "Parsed %d / %d = %.4f records\n"
        % (num_ok, num_ok + num_bad, 1.0 * num_ok / (num_ok + num_bad))
    )
