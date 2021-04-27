# Easy Route

Choose your favorite locations and landmarks and let us plan your day!

## Basically

The internet has an abundance of articles on the best spots to visit in each area but no simple way to connect all these locations and make an optimal itineray. Easy Route allows you to find all these places you want to visit and create the perfect route base on location and opening time. 

## Stack

* Language: Python, HTML, CSS
* Framework: Flask
* Database: SQLite

## Technically 

The backend is entirely written with python and api calls to Google maps API and Bing maps API. Google maps is used to search for places and find their addresses and opening times. Bing maps is used to generate the optimal route. Bing map's multi-itnerary optimization service solves efficiently our request using a traveling salesman with time windows' algorithm.  
SQLite is used for the authentification.  
Flask is used to the front-end of this app.

## Workflow

* Create an account
* Login 
* Create a new trip
* Search for places through the query search bar
* Select how long you want to stay at each place
* Click the place you want to visit to save it in your unscheduled itinenary
* Input all the places you would like to visit
* Confirm your list
* Select the day you want to travel, your starting and ending time and locations
* Create and view your scheduled itinerary in table and map format
* Make edits to your inputs if needed

## Set up
### Local machine set up:  
* [Python 3.9.2](https://www.python.org/downloads/)
* [pip 21.0.1](https://pip.pypa.io/en/stable/installing/)
* [virtualenv 20.4.2](https://packaging.python.org/key_projects/#virtualenv)

### Initial Steps:  
Clone project:   
```
git clone https://github.com/usef-kh/easyroute.git
```

Create virtual environment:  
```
virtualenv ~/easyroute-env 
```

Activate Virtual Environmnet:  
```
source ~/easyroute-env/bin/activate
```

Download Flask to project: 
```
pip install Flask
```

[Get a Google maps api key](https://developers.google.com/maps/documentation/embed/get-api-key)  

[Get a Bing maps api key](https://docs.microsoft.com/en-us/bingmaps/getting-started/bing-maps-dev-center-help/getting-a-bing-maps-key)  

Create a **keys.json** file in the main directory **easyroute** like this:
```
{
  "bingRouting": "<Your Bing API Key>",
  "gmaps": "<Your Google maps API Key"
}
```  

Run your app locally:
```
flask run
```


## Useful Links
- [Demo](https://drive.google.com/file/d/1Z-PYvm9hh573mX1lndrtSaVEIxrtGSSu/view?usp=sharing)
- [Google Maps API](https://developers.google.com/maps)
- [Bing API](https://www.microsoft.com/en-us/maps/multi-itinerary-optimization)

## Contact
- Yousif Khaireddin ykh@bu.edu
- Maxime Sabet maximesabetdacre@gmail.com


