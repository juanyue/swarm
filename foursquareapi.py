"""This script define the class FoursquareApi"""

import time
import math
import configparser
import requests


class FoursquareApi:
    """This class provides methods to interact and retrieve data from the Foursquare API"""

    _RATE = 5

    @staticmethod
    def __retrieve_history_search(offset, limit):
        """Makes the REST call GET to retrieve the checkins of a user"""

        config = configparser.ConfigParser()
        config.read('config.ini')
        foursquare_api_config = config['foursquare.api']

        try:
            response = requests.get(foursquare_api_config['ApiURL'] + "/users/" +
                                    foursquare_api_config[
                                        'UserId'] + "/historysearch?locale=en&v=" +
                                    foursquare_api_config['APIVersion'] + "&offset=" + str(offset) +
                                    "&limit=" + str(limit) + "&sort=newestfirst&oauth_token=" +
                                    foursquare_api_config['OAUTHToken'], timeout=5)
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            raise SystemExit(err) from err

        return response.json()

    @staticmethod
    def retrieve_checkins_number(limit):
        """Retrieves the number of checkins of a user or set a specific value (n latest checkins)"""

        if limit and limit > 0:
            checkins_number = limit
        else:
            checkins_number = FoursquareApi.__retrieve_history_search(0, 1)["response"]["checkins"][
                "count"]
        print("Number of checkins: " + str(checkins_number))
        return checkins_number

    @staticmethod
    def retrieve_checkins(offset, limit):
        """Retrieves the checkins of a user given an offset"""

        checkins = FoursquareApi.__retrieve_history_search(offset, limit)['response']['checkins']
        time.sleep(FoursquareApi._RATE)
        return checkins

    @staticmethod
    def __percentage_completed(offset, checkins_number):
        """Calculates the percentage of checkins processed"""

        return round((offset * 100) / checkins_number)

    @staticmethod
    def __estimated_time_left(offset, limit, checkins_number):
        """Calculates the time left based of checkins retrieved per second"""

        seconds_left = (math.ceil((checkins_number - offset) / limit)) * FoursquareApi._RATE
        if seconds_left < 120:
            return str(round(seconds_left)) + " seconds"
        return str(round(seconds_left / 60)) + " minutes"

    @staticmethod
    def print_progress(offset, limit, checkins_number):
        """Print the progress to retrieve all the checkins"""

        print("Retrieving checkins... (progress " +
              str(FoursquareApi.__percentage_completed(offset, checkins_number)) +
              "% - estimated time left: " +
              FoursquareApi.__estimated_time_left(offset, limit, checkins_number) + ")     ",
              end="\r", flush=True)
