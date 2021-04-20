import datetime
import json

import requests


def reformat_timings(place_details):
    days = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday"
    ]

    # If we have no timing info, default to 24/7
    if place_details == {}:

        place_details["opening_hours"] = {}

        weekday_text = []
        for day in days:
            weekday_text.append(day + ": open 24 hours")

        place_details["opening_hours"]["weekday_text"] = weekday_text

    offset = {}
    today = datetime.date.today()
    for i, day in enumerate(days):
        offset[day] = -today.weekday() + i

    week_details = {}
    for info in place_details["opening_hours"]["weekday_text"]:

        day, times = info.split(": ")
        day = day.lower()

        calender_date = today + datetime.timedelta(days=offset[day], weeks=0)

        if times != "Closed":

            if times.lower() in ["open 24 hours", ""]:
                opening_time = "00:00:00"
                closing_time = "24:00:00"

                opening_date = calender_date
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
                    # print(closing_time, opening_time)
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

        week_details[str(calender_date)] = timings

    return week_details


def prep_place_info(place, timing_details, day_picked, priority=1):
    dwellTime = str(datetime.timedelta(hours=float(place["dwell_time"]))) + ".0000000"

    if day_picked in timing_details:
        timing_info = timing_details[day_picked]

        if timing_info['openingTime'] == "Closed":
            return False, "Place closed"

        else:
            place_details_formatted = {
                "name": place["name"],
                "openingTime": timing_info["openingTime"],
                "closingTime": timing_info["closingTime"],
                "dwellTime": dwellTime,
                "priority": priority,
                "quantity": [],
                "location": {
                    "latitude": place["geometry"]["location"]["lat"],
                    "longitude": place["geometry"]["location"]["lng"]
                }
            }
            return True, place_details_formatted
    else:
        return False, "Day entered doesnt exit"


class Maps(object):
    def __init__(self):
        super(Maps, self).__init__()

        with open('keys.json') as json_file:
            keys = json.load(json_file)

        self.gmaps_key = keys["gmaps"]
        self.bing_key = keys["bingRouting"]

    def query(self, query):
        query = "+".join(query.split(" "))
        endpoint_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            'query': query,
            'key': self.gmaps_key
        }

        response = requests.get(endpoint_url, params=params)
        result = json.loads(response.content)

        return result["results"]  # list of results

    def get_timing_details(self, place_id, fields=['opening_hours']):
        endpoint_url = "https://maps.googleapis.com/maps/api/place/details/json"

        params = {
            'placeid': place_id,
            'fields': ",".join(fields),
            'key': self.gmaps_key
        }

        response = requests.get(endpoint_url, params=params)

        result = json.loads(response.content)
        # print(result)
        if "result" not in result:
            timings = reformat_timings({})

        else:
            timings = reformat_timings(result["result"])

        return timings

    def route(self, itinerary, data):
        # print(itinerary)
        input_info_dic = {}
        input_info_dic["itineraryItems"] = []
        agentName = "agentName"
        input_info_dic["agents"] = [{"name": agentName, "shifts": [{}]}]

        for place in itinerary:
            # print(place )
            # print("\n")
            timing_details = self.get_timing_details(place["place_id"])

            if place["name"] == data["starting_point"]:
                start_time = data["date"] + "T" + data["start_time"] + ":00"
                start_info = {
                    "name": place["name"],
                    "startTime": start_time,
                    "startLocation": {
                        "latitude": place["geometry"]["location"]["lat"],
                        "longitude": place["geometry"]["location"]["lng"]
                    }
                }
                input_info_dic["agents"][0]["shifts"][0] = {**input_info_dic["agents"][0]["shifts"][0], **start_info}

                if place["name"] == data["ending_point"]:
                    end_time = data["date"] + "T" + data["end_time"] + ":00"
                    end_info = {
                        "name": place["name"],
                        "endTime": end_time,
                        "endLocation": {
                            "latitude": place["geometry"]["location"]["lat"],
                            "longitude": place["geometry"]["location"]["lng"]
                        }
                    }
                    input_info_dic["agents"][0]["shifts"][0] = {**input_info_dic["agents"][0]["shifts"][0], **end_info}

            elif place["name"] == data["ending_point"]:
                end_time = data["date"] + "T" + data["end_time"] + ":00"
                end_info = {
                    "name": place["name"],
                    "endTime": end_time,
                    "endLocation": {
                        "latitude": place["geometry"]["location"]["lat"],
                        "longitude": place["geometry"]["location"]["lng"]
                    }
                }

                input_info_dic["agents"][0]["shifts"][0] = {**input_info_dic["agents"][0]["shifts"][0], **end_info}

            else:
                check, item = prep_place_info(place, timing_details, data["date"])
                if check:
                    input_info_dic["itineraryItems"].append(item)

        # Making the dic from all the info into json for the bing api call
        input_info = json.dumps(input_info_dic)

        # Make an Bing API call
        endpoint_url = "https://dev.virtualearth.net/REST/V1/Routes/OptimizeItinerary"
        response = requests.post(endpoint_url + "?key=" + self.bing_key, data=input_info)

        try:
            # print(response.content)
            response_dic = json.loads(response.content)
            return True, response_dic["resourceSets"][0]["resources"][0]["agentItineraries"][0]["instructions"]

        except Exception as e:
            return False, e


if __name__ == '__main__':
    maps = Maps()

    places = maps.query("Stoked pizza")

    place = places[0]

    print(maps.get_timing_details(place["place_id"]))
    print("2021-04-16" + "T" + "08:00" + ":00")
