import os
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import requests
import json
from helpers import apology, nearest_library, nearest_hospital, nearest_place, getStreetName, next_nearest_place

#create variable to hold value of API key so it doesn't need to be in the code
API_KEY = os.environ.get("API_KEY")

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///durham_info.db")

# throw error if API key is not set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")

@app.route("/", methods=["GET", "POST"])
def index():
    session.clear()
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("address"):
            return apology("must provide  address", 403)
        address = request.form.get("address")
        url = "https://us1.locationiq.com/v1/search.php"
        data = {'key': API_KEY,'q': address, 'format': 'json'}
        response = requests.get(url, params=data)
        return_info = response.json()
        first_return_dict = return_info[0] #may be multiple dicts returned from API, will always use first
        if 'Durham'  not in first_return_dict['display_name']:
            return apology("please provide a durham address", 403)

        #create variables holding latitude and longitude of user's address
        lat = float(first_return_dict['lat'])
        lon = float(first_return_dict['lon'])

        #user helper functions on helpers.py
        #extracts street address from results of API that found lat and lon
        street_address = getStreetName(first_return_dict['display_name'])
        #find nearest library to user address
        closest_library= nearest_library(lat,lon)
        #find nearest hospital to user address
        closest_hospital= nearest_hospital(lat, lon)
        #find place of interest near users address
        closest_place = nearest_place(lat, lon)

        #load session dict of all display info.
        session["all_results"] = {'prev_place_id':closest_place['id'],
            'user_lat':lat,'user_lon':lon,
            'lib_name':closest_library['name'],
            'lib_address' : closest_library['address'],
            'lib_phone':closest_library['phone'],
            'lib_url' :closest_library['url'],
            'hos_name':closest_hospital['name'],
            'hos_address' : closest_hospital['address'],
            'hos_phone':closest_hospital['phone'],
            'hos_url' :closest_hospital['url'],
            'place_name':closest_place['name'],
            'place_address' : closest_place['address'],
            'place_url' :closest_place['url'],
            'home_address':street_address,
            'electCompName': "Duke Energy",
            'electCompURL': "https://www.duke-energy.com",
            'electCompPhone': "(800)777-9898",
            'waterURL': "https://durhamnc.gov/Faq.aspx?QID:186",
            'waterPhone': "(919) 560-4326",
            'waterAddress': "101 City Hall Plaza 3rd Floor",
            'gasCompName': "Dominion Energy / PSNC",
            'gasCompURL': "https://www.psncenergy.com",
            'gasCompPhone': "(877) 776-2427",
            'internetLookupSite': "highspeedinternet.com",
            'internetURL': "https://www.highspeedinternet.com/nc/durham",
            'TVLookupSite': "cabletv.com",
            'TVURL': "https://www.cabletv.com/"}

        #load template and send results
        return render_template('results.html', **session["all_results"])
    #initial load of template of form has not yet been filled out
    return render_template("index.html")


# Function to handle thumbs up feedback from user. Updates database with user feedback
@app.route("/thumbsup", methods=["GET", "POST"])
def thumbsup():
    thumbs_up_score = db.execute("SELECT * FROM places WHERE id = :session_place_id", session_place_id=session["closest_place"])
    new_thumbs_up_score = thumbs_up_score[0]["likes"] + 1
    session_place_id=session["closest_place"]
    add_thumbs_up = db.execute("UPDATE places SET likes=:new_thumbs_up_score WHERE rowid = :session_place_id",session_place_id=session_place_id, new_thumbs_up_score=new_thumbs_up_score)
    return render_template('thumbs_up.html', **session["all_results"])

# Function to handle thumbs down feedback from user. chooses the next closest place of interest
# and returns it to the end user. also updates database with user feedback and sets location
# to not be displayed further if it has received three more thumbs downs that thumbs ups

@app.route("/thumbsdown", methods=["GET", "POST"])
def thumbsdown():
    thumbs_score = db.execute("SELECT * FROM places WHERE id = :session_place_id", session_place_id=session["closest_place"])
    new_thumbs_down_score = thumbs_score[0]["dislikes"] + 1
    current_thumbs_up_score = thumbs_score[0]["likes"]
    session_place_id=session["closest_place"]
    if new_thumbs_down_score - current_thumbs_up_score >= 3: #stop location from displaying if thumbs downs get 3 greater than thumbs ups
        turn_off_location = db.execute("UPDATE places SET visible='false' WHERE rowid = :session_place_id",session_place_id=session_place_id)
    add_thumbs_down = db.execute("UPDATE places SET dislikes=:new_thumbs_down_score WHERE rowid = :session_place_id",session_place_id=session_place_id, new_thumbs_down_score=new_thumbs_down_score)

    results_dict = session['all_results']
    lat = results_dict['user_lat']
    lon = results_dict['user_lon']
    latest_id = results_dict['prev_place_id']
    closest_place = next_nearest_place(lat, lon, latest_id) #use helper function to find place of interest

    #update session dict with new place of interest since user didn't like the first one
    session["all_results"]['place_name'] = closest_place['name']
    session["all_results"]['place_address'] = closest_place['address']
    session["all_results"]['place_url'] = closest_place['url']
    return render_template('thumbs_down.html', **session["all_results"])

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

#export API_KEY=pk.aa40b962e9898c9fbc72b3d9cd662af7