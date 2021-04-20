import ast
import collections
import datetime

from flask import Flask, render_template, request, redirect, url_for

from databases.users import Users
from maps import Maps

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
        return render_template(
            "create.html",
            data=collections.defaultdict(str),
            query_results=[],
            itinerary=[],
        )

    data = request.form

    if "search" in data:  # display new search results

        places = maps.query(data["query"])

        count = min(len(places), 10)
        query_results = places[:count]

        # create a dictionary where we will add all the info in later (check the else clause)
        info = {
            "dwell_time": data["dwell_time"]
        }

        itinerary.append(info)

    else:  # add my selection to sidebar

        selection = list(data.keys())[0]  # only one selection will be made
        selection = ast.literal_eval(selection)  # convert selection from str to dict

        itinerary[-1].update(selection)  # theres already dictionary that has dwell_time, update it
        query_results = []  # reset query results, after choosing

    return render_template("create.html", data=data, query_results=query_results, itinerary=itinerary)


@app.route('/user/complete', methods=['POST', 'GET'])
def complete():
    global itinerary

    if request.method == "GET":
        return render_template(
            "complete.html",
            data=collections.defaultdict(str),
            date=datetime.date.today(),
            itinerary=itinerary,
        )
    # if starting or ending need to make sure that the time matches the time of the place if it has opening or closing time

    data = request.form
    check, info = maps.route(itinerary, data)

    if check:

        schedule = []

        for instruction in info:
            if instruction["instructionType"] == "LeaveFromStartPoint":
                print("Leave your starting point,", data["starting_point"])

            elif instruction["instructionType"] == "TravelBetweenLocations":
                print("travel to the next location", "duration=", instruction["duration"], "distance=",
                      instruction["distance"])
            elif instruction["instructionType"] == "VisitLocation":
                location = instruction["itineraryItem"]
                print("Enjoy your time at", location["name"], "for", location["dwellTime"])

            elif instruction["instructionType"] == "ArriveToEndPoint":
                print("Get to your ending point", data["ending_point"])

    else:

        return render_template(
            "complete.html",
            data=collections.defaultdict(str),
            date=datetime.date.today(),
            itinerary=itinerary,
            error=info,
        )

    return redirect(url_for('view', route=route))



@app.route('/user/view', methods=['POST', 'GET'])
def view():
    return "helllo"
    # return redirect(url_for('index'))


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.run(debug=True)
