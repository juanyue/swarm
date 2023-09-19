"""This script generates a GEOJson based on the user checkins"""

import json
import calendar
import argparse
import time
from foursquareapi import FoursquareApi

FILENAME = "swarm_geojson_" + str(calendar.timegm(time.gmtime())) + ".json"

parser = argparse.ArgumentParser()
parser.add_argument("-l", "--limit", type=int,
                    help="process the latest specified number of checkins")
args = parser.parse_args()


def create_features(checkins):
    """Creates a GEOJson Feature object based on the user checkins"""

    features = []
    for checkin in checkins['items']:
        checkin_venue = checkin["venue"]
        checkin_location = checkin_venue["location"]
        features.append(build_feature(checkin_location["lng"], checkin_location["lat"],
                                      checkin_venue["name"], checkin["createdAt"]))
    return json.dumps(features)[1:-1]


def write_features(checkins_number):
    """Retrieves the user checkins and writes the GEOJson features in a file"""

    _offset = 0
    _limit = 100
    while _offset < checkins_number:
        if _offset + _limit > checkins_number:
            _query_size = checkins_number - _offset
        else:
            _query_size = _limit
        with open(FILENAME, "a", encoding="utf8") as _outfile:
            FoursquareApi.print_progress(_offset, _limit, checkins_number)
            _outfile.write(create_features(FoursquareApi.retrieve_checkins(_offset, _query_size)))
            _offset += _query_size
            if _offset < checkins_number:
                _outfile.write(",")
    print(end='\x1b[2K')


def build_feature(lng, lat, name, timestamp):
    """Builds a GEOJson feature object based on a template"""

    return {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [lng, lat]
        },
        "properties": {
            "name": name,
            "checkedIn": timestamp
        }
    }


_checkins_number = FoursquareApi.retrieve_checkins_number(args.limit)

with open(FILENAME, "w", encoding="utf8") as outfile:
    outfile.write("{\"type\": \"FeatureCollection\", \"features\":[")

write_features(_checkins_number)

with open(FILENAME, "a", encoding="utf8") as outfile:
    outfile.write("]}")
