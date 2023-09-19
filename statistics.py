"""This sctipt provides statistics like how many countries were visited and its states based on
the user checkin history """

import argparse
from foursquareapi import FoursquareApi

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--states",
                    help="displays the visited countries and states", action="store_true")
parser.add_argument("-c", "--countryCode",
                    help="displays country code instead of the full name", action="store_true")
parser.add_argument("-l", "--limit", type=int,
                    help="process the latest specified number of checkins")
args = parser.parse_args()

countries = {}


def get_state(location):
    """Gets the state from a location"""

    if "state" in location:
        return location["state"]
    return ""


def update_subset_countries(checkins):
    """Populates a map of countries with its states visited based on the checkins"""

    for checkin in checkins['items']:
        if args.countryCode:
            _country = checkin["venue"]["location"]["cc"]
        else:
            _country = checkin["venue"]["location"]["country"]
        _state = get_state(checkin["venue"]["location"])
        if _country in countries:
            countries[_country].add(_state)
        else:
            countries[_country] = set({_state})


def populate_countries(checkins_number):
    """Retrieves the checkins from Foursquare API and populates a map of visited countries and
    its states"""

    _offset = 0
    _limit = 100
    while _offset < checkins_number:
        if _offset + _limit > checkins_number:
            _query_size = checkins_number - _offset
        else:
            _query_size = _limit
        FoursquareApi.print_progress(_offset, _limit, checkins_number)
        update_subset_countries(FoursquareApi.retrieve_checkins(_offset, _query_size))
        _offset += _query_size
    print(end='\x1b[2K')


_checkins_number = FoursquareApi.retrieve_checkins_number(args.limit)

populate_countries(_checkins_number)

print("You have visited " + str(len(countries)) + " countries:")
if args.states:
    for country in sorted(countries):
        print(country + ":")
        for state in sorted(countries[country]):
            if state != "":
                print("\t" + state)
else:
    print(sorted(countries.keys()))
