import datetime
import json

import requests

from modules import AgentInfo


def this_week(dateString):
    '''returns true if a dateString in %Y%m%d format is part of the current week'''
    d1 = datetime.datetime.strptime(dateString, '%Y-%m-%d')
    d2 = datetime.datetime.today()
    return d1.isocalendar()[1] == d2.isocalendar()[1] and d1.year == d2.year


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
                closing_date = today + \
                               datetime.timedelta(days=offset[day], weeks=0)

            else:
                opening_time, closing_time = times.split(" – ")

                if opening_time[-2:] not in ['am', 'pm', "AM", "PM"]:
                    opening_time += " " + closing_time[-2:]

                opening_time = datetime.datetime.strptime(
                    opening_time, "%I:%M %p")
                closing_time = datetime.datetime.strptime(
                    closing_time, "%I:%M %p")

                offset_open = offset[day]
                offset_close = offset[day]

                # if place closes the next day (in the AMs)
                if closing_time < opening_time:
                    # print(closing_time, opening_time)
                    offset_close += 1

                # Convert to string in 24 hour format
                opening_time = datetime.datetime.strftime(
                    opening_time, "%H:%M:%S %p")[:-3]
                closing_time = datetime.datetime.strftime(
                    closing_time, "%H:%M:%S %p")[:-3]

                # Get calender date of opening and closing time
                opening_date = today + \
                               datetime.timedelta(days=offset_open, weeks=0)
                closing_date = today + \
                               datetime.timedelta(days=offset_close, weeks=0)

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

        if "result" not in result:
            timings = reformat_timings({})

        else:
            timings = reformat_timings(result["result"])

        return timings

    def route(self, itinerary, data):
        # print(itinerary)

        if not this_week(data["date"]):
            today = datetime.date.today()

            day_number = datetime.datetime.strptime(data["date"], '%Y-%m-%d').weekday()
            day = str(today + datetime.timedelta(days=-today.weekday() + day_number,
                                                 weeks=0))  # if tuesday give tuesday of this week
            data["date"] = day

        failures = []

        input_info_dic = {"itineraryItems": []}
        agentName = "agentName"
        input_info_dic["agents"] = [{"name": agentName, "shifts": [{}]}]

        for place in itinerary:
            timing_details = self.get_timing_details(place["place_id"])

            if place["name"] == data["starting_point"]:
                time = data["date"] + "T" + data["start_time"] + ":00"
                info = AgentInfo(place, time=time, start=True)

                input_info_dic["agents"][0]["shifts"][0].update(info)

                if place["name"] == data["ending_point"]:
                    time = data["date"] + "T" + data["end_time"] + ":00"
                    info = AgentInfo(place, time=time, start=False)

                    input_info_dic["agents"][0]["shifts"][0].update(info)

            elif place["name"] == data["ending_point"]:
                time = data["date"] + "T" + data["end_time"] + ":00"
                info = AgentInfo(place, time=time, start=False)

                input_info_dic["agents"][0]["shifts"][0].update(info)

            else:
                check, item = prep_place_info(place, timing_details, data["date"])
                print(check, item)
                if check:
                    input_info_dic["itineraryItems"].append(item)

                else:
                    failure = dict(name=place["name"], reason=item)
                    failures.append(failure)

        # Making the dic from all the info into json for the bing api call
        input_info = json.dumps(input_info_dic)

        print(failures)

        # Make an Bing API call
        endpoint_url = "https://dev.virtualearth.net/REST/V1/Routes/OptimizeItinerary"
        response = requests.post(f"{endpoint_url}?key={self.bing_key}", data=input_info)

        try:
            response_dic = json.loads(response.content)

            for unshedualed_item in response_dic["resourceSets"][0]["resources"][0]["unscheduledItems"]:
                unshedualed_item["reason"] = "Not possible or too far"
                failures.append(unshedualed_item)

            # the results is found after 3 nested dicts/lists (all indexed at 0)
            instructions = response_dic["resourceSets"][0]["resources"][0]["agentItineraries"][0]["instructions"]

            return True, (instructions, failures)

        except Exception as e:
            return False, e


if __name__ == '__main__':
    maps = Maps()

    places = maps.query("Stoked pizza")

    place = places[0]

    print(maps.get_timing_details(place["place_id"]))
    print("2021-04-16" + "T" + "08:00" + ":00")
