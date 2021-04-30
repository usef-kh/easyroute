class ItineraryItem(dict):

    def __init__(self, name, location, arrivingTime="N/A", leavingTime="N/A", dwellTime="N/A"):
        self["name"] = name
        self["location"] = location

        self["arrivingTime"] = arrivingTime
        self["leavingTime"] = leavingTime
        self["dwellTime"] = dwellTime


class AgentInfo(dict):

    def __init__(self, place, time, start=True):
        self["name"] = place["name"]

        location = {
            "latitude": place["geometry"]["location"]["lat"],
            "longitude": place["geometry"]["location"]["lng"]
        }

        if start:
            self["startLocation"] = location
            self["startTime"] = time

        else:

            self["endLocation"] = location
            self["endTime"] = time
