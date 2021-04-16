import ast
import collections
import datetime

from flask import Flask, render_template, request, redirect, url_for

from databases.users import Users
from maps import GoogleMaps

app = Flask(__name__, template_folder='templates', static_folder='static')
gmaps = GoogleMaps()
selections = []  # this is a global variable that contains where the user wats to go


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
    global selections

    if request.method == "GET":
        return render_template(
            "create.html",
            data=collections.defaultdict(str),
            query_results=[],
            selections=[],
        )

    data = request.form

    if "search" in data:  # display new search results

        places = gmaps.query(data["query"])

        count = min(len(places), 10)
        query_results = places[:count]

        # create a dictionary where we will add all the info in later (check the else clause)
        info = {
            "dwell_time": data["dwell_time"]
        }

        selections.append(info)

    else:  # add my selection to sidebar

        selection = list(data.keys())[0]  # only one selection will be made
        selection = ast.literal_eval(selection)  # convert selection from str to dict

        selections[-1].update(selection)  # theres already dictionary that has dwell_time, update it
        query_results = []  # reset query results, after choosing

    return render_template("create.html", data=data, query_results=query_results, selections=selections)


@app.route('/user/complete', methods=['POST', 'GET'])
def complete():
    global selections

    if request.method == "GET":
        return render_template(
            "complete.html",
            data=collections.defaultdict(str),
            date=datetime.date.today(),
            selections=selections,
        )

    # change this later so that we take care of the post method and show a map / schedule
    return render_template(
        "complete.html",
        data=collections.defaultdict(str),
        date=datetime.date.today(),
        selections=selections,
    )


@app.route('/user/view', methods=['POST', 'GET'])
def view():
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.run(debug=True)
