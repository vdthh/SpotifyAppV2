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
from .common import searchSpotify, returnSearchResults
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
gv_searchType              = ""
gv_searchTerm              = ""
gv_offset                  = 0
gv_limit                   = 0
gv_total                   = 0
########################################################################################


########################################################################################
##################################### FLASK INTERFACE ##################################
########################################################################################
# HTML ROUTING #
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


    #--> PAGE LOAD #
    if request.method == "GET" and not ("addArtist" in args) and not ("offs" in args) and not ("lim" in args) and not ("searchTerm" in args) and not ("searchType" in args):
        try:
            '''--> page load  - show playlist items with info'''
            '''--> initialize variables'''
            '''TODO'''
            gv_watchlistItems = []  #list empty, initialize it every reload


            '''--> db operation'''
            db = get_db() #grab from db
            data = db.execute('SELECT * FROM WatchList').fetchall()    #returns list of dicts https://docs.python.org/3/library/sqlite3.html


            '''--> check data'''
            if data is None:
                flash("No entries in watchlist yet!", category="error")
                logAction("msg - watchlist.py - watchlist_main --> page reload --> no items to show!")
            else:
                for row in data:           
                    data_encoded = json.dumps(row["list_of_current_items"])  #json.dumps() function converts a Python object into a json string.

            '''--> return html'''
            return render_template('watchlist.html', showArtistBtn = "active", showArtistTab = "show active", showPlaylistBtn ="" , showPlaylistTab = "", showUserBtn = "", showUserTab = "")

        except Exception as ex:
            logAction("err - watchlist.py - watchlist_main2 --> error while loading page --> " + str(type(ex)) + " - " + str(ex.args) + " - " + str(ex))
            logAction("TRACEBACK --> " + traceback.format_exc())
        

    #--> SEARCH ARTIST - BUTTON PRESSED - PAGINATION # 
    if (request.method == "POST" and  ("artist_search" in request.form)) or (request.method == "GET" and not ("addArtist" in args) and ("offs" in args) and ("lim" in args) and ("searchTerm" in args) and ("searchType" in args)):
        try:
            '''--> pagination or search button press?'''
            if (request.method == "GET" and not ("addArtist" in args) and ("offs" in args) and ("lim" in args) and ("searchTerm" in args) and ("searchType" in args)):
                paginReq = True
            else:
                paginReq = False


            '''--> initialize variables'''
            gv_artistList   = [] #(re-)initialize global artist list


            '''--> update variables'''
            if paginReq:
                print("PAGINATIONççç")
                gv_searchTerm   = args["searchTerm"]
                gv_searchType   = args["searchType"]
                gv_offset       = int(args["offs"])
                gv_limit        = int(args["lim"])
            else:
                print("SEARCH BUTTON PRESS")
                gv_searchTerm   = request.form["searchartistinput"] #searchterm entered in page
                gv_searchType   = "artist"
                gv_offset       = 0
                gv_limit        = 10


            '''--> api request'''
            logAction("msg - watchlist.py - watchlist_main3 --> searching for artist " + gv_searchTerm)
            response = searchSpotify(gv_searchTerm, gv_searchType, gv_limit, gv_offset)
            

            '''--> check response before continuing'''
            if response == '':
                logAction("err - watchlist.py - watchlist_main4 --> empty api response for searching artist.")
                flash("Error when searching for artist " + gv_searchTerm + ", empty response.", category="error")
                return render_template("watchlist.html")


            '''--> retrieve pagination'''
            total       = response[gv_searchType  + 's']['total']
            gv_limit    = response[gv_searchType  + 's']['limit']
            gv_offset   = response[gv_searchType  + 's']['offset']


            '''--> fill artistList'''
            for item in returnSearchResults(response, "artist"):
                gv_artistList.append({"artist": item["artist"], "id": item['id'], "popularity": item['popularity'], "image": item['imageurl']})


            '''--> return html'''
            return render_template("watchlist.html", 
                                    artistList = gv_artistList, 
                                    showArtistBtn = "active", 
                                    showArtistTab = "show active", 
                                    showPlaylistBtn ="" , 
                                    showPlaylistTab = "", 
                                    showUserBtn = "", 
                                    showUserTab = "",
                                    tot = total,
                                    lim = gv_limit,
                                    offs = gv_offset,
                                    searchType = gv_searchType,
                                    searchTerm = gv_searchTerm)

        except Exception as ex:
            flash("Error while searching for artist " + gv_searchTerm + ".", category="error")
            logAction("err - watchlist.py - watchlist_main5 --> error while loading page --> " + str(type(ex)) + " - " + str(ex.args) + " - " + str(ex))
            logAction("TRACEBACK --> " + traceback.format_exc())
            return render_template('watchlist.html', 
                                    artistList = gv_artistList,
                                    showArtistBtn = "active", 
                                    showArtistTab = "show active", 
                                    showPlaylistBtn ="" , 
                                    showPlaylistTab = "", 
                                    showUserBtn = "", 
                                    showUserTab = "", 
                                    offs = gv_offset, 
                                    lim = gv_limit, 
                                    tot = total, 
                                    searchTerm = gv_searchTerm, 
                                    searchType = gv_searchType)


    #--> ADD ARTIST TO WATCHLIST - BUTTON PRESSED #
    if request.method == "GET" and ("addArtist" in args) and not ("offs" in args) and not ("lim" in args) and not ("searchTerm" in args) and not ("searchType" in args):
        try:
            '''--> STOPPED HERE 20220613'''

        except Exception as ex:
            flash("Error ...", category="error")
            logAction("err - watchlist.py - watchlist_main10 --> ... --> " + str(type(ex)) + " - " + str(ex.args) + " - " + str(ex))
            logAction("TRACEBACK --> " + traceback.format_exc())
            return render_template('watchlist.html', 
                                    artistList = gv_artistList,
                                    showArtistBtn = "active", 
                                    showArtistTab = "show active", 
                                    showPlaylistBtn ="" , 
                                    showPlaylistTab = "", 
                                    showUserBtn = "", 
                                    showUserTab = "", 
                                    offs = gv_offset, 
                                    lim = gv_limit, 
                                    tot = total, 
                                    searchTerm = gv_searchTerm, 
                                    searchType = gv_searchType)
  




        # for item in WatchList.query.all():  #{id: string, trackList: pickletype (list)}
        #     toAdd = {"id": item.id, "type": item.type, "name": item.name, "image": item.imageURL, "dateAdded": item.date_added, "dateLastCheck": item.last_time_checked, "noOfNewItems": item.new_items_since_last_check, "listOfNewItemsID": item.list_of_current_items}
        #     gv_watchlistItems.append(toAdd)

        # print('Page loaded...')
        # logAction("watchlist.py --> Page loaded...")

        # return render_template("watchlist.html",  artistList = gv_artistList, playlistInfo = gv_playlistInfo, displayList = gv_watchlistItems, showArtistBtn = "active", showArtistTab = "show active", showPlaylistBtn ="" , showPlaylistTab = "", showUserBtn = "", showUserTab = "")





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





