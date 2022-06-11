########################################################################################
##################################### watchlist.py #####################################
############### Handles all functions related to the watchlist section #################
########################################################################################


########################################################################################
######################################### IMPORTS ######################################
########################################################################################
import functools
from flask import (Blueprint, flash, g, redirect, render_template, request, url_for)
from spotr.common import logAction
from spotr.db import get_db
from datetime import datetime
import json
import os
import traceback
from .common import searchSpotify
########################################################################################


########################################################################################
######################################## FLASK INIT ####################################
########################################################################################
bp_watchlist = Blueprint('watchlist', __name__, url_prefix="/watchlist")
########################################################################################



########################################################################################
######################################## VARIABLES #####################################
########################################################################################
gv_artistList              = []     #{artist: artist, id: id, image: imageurl}
gv_playlistInfo            = {}
gv_watchlistItems          = []     #list of {"id:" , "type": , "name": , "image": , "dateAdded": , "dateLastCheck": , "noOfNewItems": , "listOfNewItemsID": }
gv_newTracksToSave         = []     # list of tracks ID's of new tracks to add to NewPlaylistTracks DB
########################################################################################


########################################################################################
##################################### FLASK INTERFACE ##################################
########################################################################################
'''--> html routing'''
@bp_watchlist.route("/", methods=["GET","POST"])
def watchlist_main():
    '''--> main routine'''
    '''--> initialize gloval variables'''
    global gv_artistList              
    global gv_playlistInfo 
    global gv_watchlistItems  #contains details of every watchlist entry - used for page reload
    global gv_newTracksToSave


    '''--> read query parameters'''
    args=request.args      


    '''--> page load'''
    if request.method == "GET" and not ("addArtist" in args):
        try:
            #page load  - show playlist items with info
            gv_watchlistItems = []  #list empty, initialize it every reload
            db = get_db() #grab from db
            data = db.execute('SELECT * FROM WatchList').fetchall()    #returns list of dicts https://docs.python.org/3/library/sqlite3.html

            if data is None:
                flash("No entries in watchlist yet!", category="error")
                logAction("msg - watchlist.py - watchlist_main --> page reload --> no items to show!")
            else:
                print(str(data))
                for row in data:

                    #json.dumps() function converts a Python object into a json string.
                    data_encoded = json.dumps(row["list_of_current_items"])
                    print("data_encoded: " + data_encoded)
                    # print("album: " + row["id"])

            return render_template('watchlist.html')

        except Exception as ex:
            logAction("err - watchlist.py - watchlist_main2 --> error while loading page --> " + str(type(ex)) + " - " + str(ex.args) + " - " + str(ex))
            logAction("TRACEBACK --> " + traceback.format_exc())
            return ''
        

    '''--> search artist - button pressed'''
    if request.method == "POST" and  ("artist_search" in request.form):
        try:
            gv_artistList   = [] #(re-)initialize global artist list
            input           = request.form["searchartistinput"] #searchterm entered in page

            logAction("msg - watchlist.py - watchlist_main3 --> searching for artist " + input)
            response = searchSpotify(input, "artist", 10, 0)
            

            '''--> check response before continuing'''
            if response == '':
                logAction("err - watchlist.py - watchlist_main4 --> empty api response for searching artist.")
                return ''


            '''--> only show 10 first results, for now'''
            for item in response["artists"]["items"]:
                #check images list
                if len(item["images"]) != 0:
                    imageurl = item["images"][0]["url"]
                else:
                    imageurl = ""
                toAdd={"artist": item["name"], "id": item["id"], "image": imageurl}
                gv_artistList.append(toAdd)

            '''--> return html'''
            return render_template("watchlist.html", artistList = gv_artistList, showArtistBtn = "active", showArtistTab = "show active", showPlaylistBtn ="" , showPlaylistTab = "", showUserBtn = "", showUserTab = "")

        except Exception as ex:
            logAction("err - watchlist.py - watchlist_main5 --> error while loading page --> " + str(type(ex)) + " - " + str(ex.args) + " - " + str(ex))
            logAction("TRACEBACK --> " + traceback.format_exc())
            return ''



    '''--> add artist to watchlist - button pressed'''
    if request.method == "GET" and ("addArtist" in args):
        pass




        # for item in WatchList.query.all():  #{id: string, trackList: pickletype (list)}
        #     toAdd = {"id": item.id, "type": item.type, "name": item.name, "image": item.imageURL, "dateAdded": item.date_added, "dateLastCheck": item.last_time_checked, "noOfNewItems": item.new_items_since_last_check, "listOfNewItemsID": item.list_of_current_items}
        #     gv_watchlistItems.append(toAdd)

        # print('Page loaded...')
        # logAction("watchlist.py --> Page loaded...")

        # return render_template("watchlist.html",  artistList = gv_artistList, playlistInfo = gv_playlistInfo, displayList = gv_watchlistItems, showArtistBtn = "active", showArtistTab = "show active", showPlaylistBtn ="" , showPlaylistTab = "", showUserBtn = "", showUserTab = "")



















    
    # if request.method == 'GET':
    #     print("- - - - GET")

    #     #fetch rows from db, if any
    #     db = get_db()
    #     data = db.execute('SELECT * FROM NewWatchListTracks').fetchall()    #returns list of dicts https://docs.python.org/3/library/sqlite3.html

    #     # print("1 - " + data[0]["id"])
    #     # print(data[0].keys())

    #     if data is None:
    #         error = 'no entries in db!'
    #     else:
    #         for row in data:
    #             #json.dumps() function converts a Python object into a json string.
    #             # data_encoded = json.dumps(row["trackList"])
    #             # print("artist: " + row["artist"])
    #             print("album: " + row["id"])

    #     return render_template('watchlist.html')

    # elif request.method == 'POST':
    #     print("- - - - POST")
    #     db = get_db()
    #     error = None

    #     tempVar = {"id": "id12" + str(datetime.now()), "album": "homework", "artist": "daft punk", "date_added": str(datetime.now())}
    #     # json.dumps() function converts a Python object into a json string
    #     tempVar_Serialized = json.dumps(tempVar)
    #     #convert to json string before storing in db
    #     #https://stackoverflow.com/questions/20444155/python-proper-way-to-store-list-of-strings-in-sqlite3-or-mysql
    #     try:
    #         date_ = str(datetime.now())
    #         db.execute(
    #             'INSERT INTO NewWatchListTracks (id, trackList) VALUES (?,?)', (date_ + "id", tempVar_Serialized)
    #         )
    #         # db.execute(
    #         #     "INSERT INTO NewWatchListTracks (id, trackList) VALUES (?, ?)",
    #         #     (id, toStore),
    #         # )
    #         db.commit()
    #         print("added entry to DB!" )
    #     except db.IntegrityError:
    #         print("failed to add entry to DB!" )
    #         error = f"Id {id} is already registered."

    #     #show data
    #     data = db.execute('SELECT * FROM NewWatchListTracks').fetchall()
    #     print(data[0]["trackList"])
    #     print(data[0].keys())

    #     #convert list of JSON strings to list of dicts
    #     data_parsed= []
    #     for row in data:
    #         # print("type: " + str(type(row)))
    #         print(str(row))
    #         parsed = json.loads(row[1])
    #         print(row[1])
    #         print(parsed["album"])
    #         data_parsed.append(parsed)
    #         # data_parsed.append(json.loads(row))

    #     # print("parsed: " + data_parsed[9]["trackList"]["album"])
    #     logAction("TESTTEST")

    #     flash(error)
    #     return render_template('watchlist.html', data = data_parsed)

########################################################################################





