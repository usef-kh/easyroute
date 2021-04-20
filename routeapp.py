from route import *


def main():
    user_query = ""
    places_details = []
    # while user_query != "Exit":
    places_test = ["Museum of fine arts", "Dominos", "Uniqlo", "MIT Dome"]
    # Bug with uniqlo to fix
    for i in places_test:
        # print("Write Exit if you want to exit else \n")
        # user_query = input("Enter you query:")
        # print("OK")
        # if user_query == "Exit":
        #     continue
        # else:
        week_details = getMapsInfo(i)
        places_details.append(week_details)
    # format places times 
    itineraryItems = []
    for place in places_details:
        place_details_formatted = places2SetUp(place, "friday")
        itineraryItems.append(place_details_formatted)
    input_info_dic = {"itineraryItems": itineraryItems}

    print(input_info_dic)
    # Format agents
    input_info_dic["agents"] = [
        {
            "name": "agentName",
            "shifts": [
                {
                    "startTime": "2021-04-16T08:00:00",
                    "startLocation": {
                        "latitude": 42.3416936,
                        "longitude": -71.0869444
                    },
                    "endTime": "2021-04-16T18:00:00",
                    "endLocation": {
                        "latitude": 42.3416936,
                        "longitude": -71.0869444
                    }
                }
            ]
        }
    ]
    # Finding the optimized route
    resulting_route = getOptimizedRoute(input_info_dic)
    for k, v in resulting_route[0]["resources"][0].items():
        print(k, v)


if __name__ == "__main__":
    main()
