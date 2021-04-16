import collections
import datetime
from flask import Flask, render_template, request, redirect, url_for

from databases.users import Users

from maps import *

app = Flask(__name__, template_folder='templates', static_folder='static')

selections =[]
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
    data = collections.defaultdict(str)
    if request.method == "GET":
        return render_template("create.html", data=data, date=datetime.date.today(), query_results=[], selections = [], placeId="")
    global selections
    data = request.form
    # print(data)
    if "search" in data:
        print("display new search results")
        #print(data)
        #data_dict = dict(data)
        #print(data_dict)
        places = getMapsInfo(data["query"])
        
        # only get first 10
        query_results = places[:10]

        # print(query_maps_results["name"],query_maps_results["Address:"] )
        # place = query_maps_results["name"] + ", "+query_maps_results["Address:"]
        # query_results = [place]
        return render_template("create.html", data=data, date=data["date"], query_results = query_results, selections = selections)
    elif "confirm" in data:
        print("confirm")
    else:
        print("Update selected spot table")
        print(list(data.keys())[0])
        selections.append(list(data.keys())[0])
        print(selections)
        query_results = []
        return render_template("create.html", data=data, date="", query_results = query_results, selections = selections, placeId="")

    query_results = []
    return render_template("create.html", data=data, date="", query_results = query_results, selections = selections, placeId="")


@app.route('/user/view', methods=['POST', 'GET'])
def view():
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.run(debug=True)
