import ast
import collections
import datetime

from flask import Flask, render_template, request, redirect, url_for

from databases.users import Users
from maps import Maps
from modules import ItineraryItem

app = Flask(__name__, template_folder='templates', static_folder='static')
maps = Maps()
itinerary = []  # this is a global variable that contains where the user wats to go


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/user/signup', methods=['POST', 'GET'])
def signup():
    if request.method == "GET":
        return render_template("signup.html", data=collections.defaultdict(str))

    users = Users()

    username = request.form["username"]
    password = request.form["password"]
    password2 = request.form["password2"]
    email = request.form["email"]

    if username in users:
        return render_template("signup.html", data=request.form, error="Username is already in use.")

    if password != password2:
        return render_template("signup.html", data=request.form, error="Passwords do not match")

    users.add(username, password, email)

    return redirect(url_for('login'))


@app.route('/user/login', methods=['POST', 'GET'])
def login():
    if request.method == "GET":
        return render_template("login.html", data=collections.defaultdict(str))

    users = Users()

    data = request.form

    username = data['username']
    password = data['password']

    check, error = users.login(username, password)

    if not check:
        return render_template("login.html", data=data, error=error)

    return redirect(url_for('home'))


@app.route('/user/home', methods=['POST', 'GET'])
def home():
    return render_template("home.html", data=collections.defaultdict(str))


@app.route('/user/create', methods=['POST', 'GET'])
def create():
    global itinerary

    if request.method == "GET":
        itinerary = []  # reset itinerary

        data = collections.defaultdict(str)
        data["dwell_time"] = 1

        return render_template(
            "create.html",
            data=data,
            query_results=[],
            itinerary=itinerary,
        )

    data = request.form.to_dict()
    query_results = []
    error = ""

    if "search" in data:  # display new search results
        query = data["query"]

        if query:
            places = maps.query(query)

            count = min(len(places), 10)
            query_results = places[:count]

            if query_results:

                # create a dictionary where we will add all the info in later (check the else clause)
                info = {
                    "dwell_time": data["dwell_time"]
                }

                if itinerary and "name" not in itinerary[-1]:
                    itinerary[-1] = info

                else:
                    itinerary.append(info)

    elif "itinerary" in data:  # remove unwanted itinerary item

        selection = data["itinerary"]
        idx = None

        for i, item in enumerate(itinerary):
            if item["name"] == selection:
                idx = i
                break

        if idx is not None:
            itinerary.pop(idx)
        else:
            error = "Removal Unsuccessful"

    else:  # add my selection to sidebar

        selection = list(data.keys())[0]  # only one selection will be made
        # convert selection from str to dict
        selection = ast.literal_eval(selection)

        # theres already dictionary that has dwell_time, update it
        itinerary[-1].update(selection)
        query_results = []  # reset query results, after choosing

    if "dwell_time" not in data:
        data["dwell_time"] = 1
    

    return render_template("create.html", data=data, query_results=query_results, itinerary=itinerary, error=error)


@app.route('/user/complete', methods=['POST', 'GET'])
def complete():
    global itinerary

    def get_time(datetimestring):
        return datetimestring.split("T")[1].split("+")[0]

    if request.method == "GET":
        return render_template(
            "complete.html",
            data=collections.defaultdict(str),
            date=datetime.date.today(),
            itinerary=itinerary,
        )

    data = request.form
    check, info = maps.route(itinerary, data)

    # if something goes bad, try again
    if not check:
        return render_template(
            "complete.html",
            data=collections.defaultdict(str),
            date=datetime.date.today(),
            itinerary=itinerary,
            error=info,
        )
    instructions, failures = info
    print(failures)
    schedule = []
    for instruction in instructions:
        if instruction["instructionType"] == "LeaveFromStartPoint":
            place = instruction["itineraryItem"]

            item = ItineraryItem(
                name=data["starting_point"],
                leavingTime=get_time(instruction["startTime"]),
                location=place["location"]
            )

            schedule.append(item)

        elif instruction["instructionType"] == "TravelBetweenLocations":
            continue  # for now lets ignore showing travel times

        elif instruction["instructionType"] == "VisitLocation":
            place = instruction["itineraryItem"]

            item = ItineraryItem(
                name=place["name"],
                dwellTime=place["dwellTime"],
                arrivingTime=get_time(instruction["startTime"]),
                leavingTime=get_time(instruction["endTime"]),
                location=place["location"]
            )

            schedule.append(item)

        elif instruction["instructionType"] == "ArriveToEndPoint":
            place = instruction["itineraryItem"]

            item = ItineraryItem(
                name=data["ending_point"],
                arrivingTime=get_time(instruction["startTime"]),
                location=place["location"]
            )

            schedule.append(item)

    return redirect(url_for('view', info={"schedule": schedule, "failures": failures}))


@app.route('/user/view', methods=['POST', 'GET'])
def view():
    info_dic = ast.literal_eval(request.args['info'])

    key = f"https://maps.googleapis.com/maps/api/js?key={maps.gmaps_key}&callback=initMap"

    return render_template(
        "view.html",
        schedule=info_dic['schedule'],
        failures=info_dic['failures'],
        key=key,
    )


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.run(debug=True)
