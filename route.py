
import requests
import json

#Function that makes call to get optimized route from bings api
#Takes dic input in with format from: https://docs.microsoft.com/en-us/bingmaps/rest-services/routes/optimized-itinerary#api-templates
def getOptimizedRoute(input_info_dic):
    #Transforms dic to json
    input_info = json.dumps(input_info_dic)
    # Get api key
    with open('keys.json') as json_file:
        data = json.load(json_file)
        bing_key = data["bingRouting"]
    #Makes api call
    response = requests.post("https://dev.virtualearth.net/REST/V1/Routes/OptimizeItinerary?key="+bing_key,data=input_info)
    #Puts response to a dic and return the part that contains the path
    try:
        response_dic = json.loads(response.content)
        return response_dic["resourceSets"]
    except:
        return "Failed"


def places2SetUp(place_details, day_picked, dwellTime ="00:30:08.3850000", priority=1):
    if "week_details" in place_details:
        week_details = place_details["week_details"]
    else:
        return "This place doesnt have opening or closing times"
    if day_picked in week_details:
        if week_details[day_picked]['openingTime'] == "Closed":
            return "Place closed"
        else:
            place_details_formatted ={
                "name": place_details["name"],
                "openingTime": week_details[day_picked]["openingTime"],
                "closingTime": week_details[day_picked]["closingTime"],
                "dwellTime": dwellTime,
                "priority": priority,
                "quantity" : [],             
                "location": {
                    "latitude": place_details["Geo Location:"]["lat"],
                    "longitude": place_details["Geo Location:"]["lng"]
                }
            }
            return place_details_formatted
    else:
        return "Day entered doesnt exit"


# input_info_dic = {
#     "agents": [
#         {
#             "name": "agentName",
#             "shifts": [
#                 {
#                     "startTime": "2019-11-09T08:00:00",
#                     "startLocation": {
#                         "latitude": 47.694117204371,
#                         "longitude": -122.378188970181
#                     },
#                     "endTime": "2019-11-09T18:00:00",
#                     "endLocation": {
#                         "latitude": 47.7070790545669,
#                         "longitude": -122.355226696231
#                     }
#                 }
#             ]
#         }
#     ],
#     "itineraryItems": [
#         {
#             "name": "loc1",
#             "openingTime": "2019-11-09T09:00:00",
#             "closingTime": "2019-11-09T18:00:00",
#             "dwellTime": "01:31:08.3850000",
#             "priority": 1,
#             "quantity" : [],             
#             "location": {
#                 "latitude": 47.692290770423,
#                 "longitude": -122.385954752402
#             }
#         },
#         {
#             "name": "loc2",
#             "openingTime": "2019-11-09T09:00:00",
#             "closingTime": "2019-11-09T18:00:00",
#             "dwellTime": "01:00:32.6770000",
#             "priority": 1,
#             "quantity" :[],
#             "location": {
#                 "latitude": 47.6798098928389,
#                 "longitude": -122.383036445391
#             }
#         },
#         {
#             "name": "loc3",
#             "openingTime": "2019-11-09T09:00:00",
#             "closingTime": "2019-11-09T18:00:00",
#             "dwellTime": "01:18:33.1900000",
#             "priority": 1,
#             "quantity" :[],
#             "location": {
#                 "latitude": 47.6846639223203,
#                 "longitude": -122.364839942855
#             },
#         },
#         {
#             "name": "loc4",
#             "openingTime": "2019-11-09T09:00:00",
#             "closingTime": "2019-11-09T18:00:00",
#             "dwellTime": "01:04:48.7630000",
#             "priority": 1,
#             "quantity" :[],
#             "location": {
#                 "latitude": 47.6867440824094,
#                 "longitude": -122.354711700877
#             },
#         },
#         {
#             "name": "loc5",
#             "openingTime": "2019-11-09T09:00:00",
#             "closingTime": "2019-11-09T18:00:00",
#             "dwellTime": "02:34:48.5430000",
#             "priority": 1,
#             "quantity" :[],
#             "location": {
#                 "latitude": 47.6962193175262,
#                 "longitude": -122.342180147243
#             }
#         }
#     ]
# }


# resulting_route = getOptimizedRoute(input_info_dic)
# print(resulting_route)