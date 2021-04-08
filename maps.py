import datetime
import json

import requests


class GooglePlaces(object):
    def __init__(self, apiKey=''):
        super(GooglePlaces, self).__init__()
        self.apiKey = apiKey

    def get_place_details(self, place_id, fields=['opening_hours']):
        endpoint_url = "https://maps.googleapis.com/maps/api/place/details/json"

        params = {
            'placeid': place_id,
            'fields': ",".join(fields),
            'key': self.apiKey
        }

        response = requests.get(endpoint_url, params=params)
        result = json.loads(response.content)

        return result["result"]

    def query(self, query):
        query = "+".join(query.split(" "))
        endpoint_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            'query': query,
            'key': self.apiKey
        }

        response = requests.get(endpoint_url, params=params)
        result = json.loads(response.content)

        return result["results"]  # list of results


# def get_time_format(time):
#     time_format = "%I:%M %p"
    
#     if not any(time.find(option) != -1 for option in ['am', 'pm', "AM", "PM"]):
#         time_format = "%I:%M"

#     return time_format



# if __name__ == "__main__":
def getMapsInfo(user_query="Museum of fine arts"):
    with open('keys.json') as json_file:
        keys = json.load(json_file)

    api = GooglePlaces(keys["gmaps"])

    places = api.query(user_query)
    choice = places[0]  # the first result is fine for now

    print("Name:", choice["name"])
    print("Address:", choice["formatted_address"])
    print("Geo Location:", choice["geometry"]["location"])

    
    place_details = api.get_place_details(choice['place_id'])
    if place_details != {}:
        # Get the number of days between the current day and each day of the week
        offset = {}
        today = datetime.date.today()
        for i, day in enumerate(["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]):
            offset[day] = -today.weekday() + i

        week_details = {}
        for info in place_details["opening_hours"]["weekday_text"]:

            day, times = info.split(": ")
            day = day.lower()

            if times != "Closed":

                if times.lower() == "open 24 hours":
                    opening_time = "00:00:00"
                    closing_time = "24:00:00"

                    opening_date = today + datetime.timedelta(days=offset[day], weeks=0)
                    closing_date = today + datetime.timedelta(days=offset[day], weeks=0)
                
                else:
                    opening_time, closing_time = times.split(" – ")

                    if opening_time[-2:] not in ['am', 'pm', "AM", "PM"]:
                        opening_time += " " + closing_time[-2:]

                    opening_time = datetime.datetime.strptime(opening_time, "%I:%M %p")
                    closing_time = datetime.datetime.strptime(closing_time, "%I:%M %p")

                    offset_open = offset[day]
                    offset_close = offset[day]

                    if closing_time < opening_time:  # if place closes the next day (in the AMs)
                        print(closing_time, opening_time)
                        offset_close += 1

                    # Convert to string in 24 hour format
                    opening_time = datetime.datetime.strftime(opening_time, "%H:%M:%S %p")[:-3]
                    closing_time = datetime.datetime.strftime(closing_time, "%H:%M:%S %p")[:-3]

                    # Get calender date of opening and closing time
                    opening_date = today + datetime.timedelta(days=offset_open, weeks=0)
                    closing_date = today + datetime.timedelta(days=offset_close, weeks=0)

                # Store values in required format
                opening_time = str(opening_date) + "T" + opening_time
                closing_time = str(closing_date) + "T" + closing_time

            else:
                opening_time = "Closed"
                closing_time = "Closed"

            timings = {
                "openingTime": opening_time,
                "closingTime": closing_time,
                "info": times,
            }

            week_details[day] = timings

        # Print results
        for day, info in week_details.items():
            print(day)

            for k, v in info.items():
                print(k, v)

            print()

        place_details = {
            "name": choice["name"],
            "Address:": choice["formatted_address"],
            "Geo Location:": choice["geometry"]["location"],
            "week_details":week_details
            }
        return place_details
    else:
        place_details = {
            "name": choice["name"],
            "Address:": choice["formatted_address"],
            "Geo Location:": choice["geometry"]["location"]
            }

        return place_details


place_details = getMapsInfo("MIT Dome")