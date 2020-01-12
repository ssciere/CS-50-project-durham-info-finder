import os
import requests
import urllib.parse
from cs50 import SQL
from flask import redirect, render_template, request, session
from functools import wraps

db = SQL("sqlite:///durham_info.db")

def apology(message, code=400):
    return render_template("apology.html", error=message)

def nearest_library(lat, lon):
    # Query database for library info
    libraries = db.execute("SELECT * FROM libraries")
     #find closest library based on coordinates
    shortest_distance = 1000000
    for location in libraries:
        print(location)
        current_lat = float(location['lat'])
        current_lon = float(location['lon'])
        current_distance = abs(current_lat - lat) + abs(current_lon  - lon)
        if current_distance < shortest_distance:
            id_for_closest = location['id']
            shortest_distance = current_distance

    closest_list = db.execute("SELECT * FROM libraries WHERE id = :final_id_for_closest",
                                final_id_for_closest=id_for_closest)
    closest = closest_list[0]
    return (closest)

def nearest_hospital(lat, lon):
    # Query database for library info
    hospitals = db.execute("SELECT * FROM hospitals")
     #find closest library based on coordinates
    shortest_distance = 1000000
    for location in hospitals:
        current_lat = float(location['lat'])
        current_lon = float(location['lon'])
        current_distance = abs(current_lat - lat) + abs(current_lon  - lon)
        if current_distance < shortest_distance:
            id_for_closest = location['id']
            shortest_distance = current_distance

    closest_list = db.execute("SELECT * FROM hospitals WHERE id = :final_id_for_closest",
                                final_id_for_closest=id_for_closest)
    closest = closest_list[0]
    return (closest)


def nearest_place(lat, lon):

    places = db.execute("SELECT * FROM places")
     #find closest place based on coordinates
    shortest_distance = 1000000
    id_for_closest = 1 #set default location choice
    for location in places:
        current_lat = float(location['lat'])
        current_lon = float(location['lon'])
        current_distance = abs(current_lat - lat) + abs(current_lon  - lon)
        if current_distance < shortest_distance and location['visible'] == "true":
            id_for_closest = location['id']
            shortest_distance = current_distance
    closest_list = db.execute("SELECT * FROM places WHERE id = :final_id_for_closest",
                                final_id_for_closest=id_for_closest)
    closest = closest_list[0]

    session["closest_place"] = id_for_closest
    return (closest)

def next_nearest_place(lat, lon, previous_id):

    places = db.execute("SELECT * FROM places")
     #find closest place based on coordinates
    shortest_distance = 1000000
    id_for_closest = 1 #set default location choice
    for location in places:
        current_lat = float(location['lat'])
        current_lon = float(location['lon'])
        current_distance = abs(current_lat - lat) + abs(current_lon  - lon)
        if current_distance < shortest_distance and location['visible'] == "true" and location['id'] != previous_id:
            id_for_closest = location['id']
            shortest_distance = current_distance
    closest_list = db.execute("SELECT * FROM places WHERE id = :final_id_for_closest",
                                final_id_for_closest=id_for_closest)
    closest = closest_list[0]

    session["closest_place"] = id_for_closest
    return (closest)

def getStreetName(address): #takes address returned by API &  creates a new string using only text before first 2 commas (house # and street)
    comma_count = 0
    street_name = ""
    for character in address:
        if character != ",":
            street_name += character
        else:
            comma_count += 1
            if comma_count == 2:
                break
    return(street_name)


