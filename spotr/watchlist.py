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
from .common import apiGetSpotify, getTracksFromArtist, searchSpotify, returnSearchResults
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
    global gv_searchType     
    global gv_searchTerm         
    global gv_offset                  
    global gv_limit                   
    global gv_total                   


    '''--> read query parameters'''
    args=request.args      


    #--> PAGE LOAD #
    if request.method == "GET" and not ("addArtist" in args) and not ("delItem" in args) and not ("offs" in args) and not ("lim" in args) and not ("searchTerm" in args) and not ("searchType" in args):
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


            '''--> return html'''
            return render_template('watchlist.html', 
                                    showArtistBtn = "active", 
                                    showArtistTab = "show active", 
                                    showPlaylistBtn ="" , 
                                    showPlaylistTab = "", 
                                    showUserBtn = "", 
                                    showUserTab = "")

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
                return render_template('watchlist.html', 
                        showArtistBtn = "active", 
                        showArtistTab = "show active", 
                        showPlaylistBtn ="" , 
                        showPlaylistTab = "", 
                        showUserBtn = "", 
                        showUserTab = "")


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
                                    showUserTab = "")


    #--> ADD ARTIST TO WATCHLIST - BUTTON PRESSED #
    if request.method == "GET" and ("addArtist" in args) and not ("delItem" in args) and not ("offs" in args) and not ("lim" in args) and not ("searchTerm" in args) and not ("searchType" in args):
        try:
            '''--> artist details'''
            artistID        = args["addArtist"]
            logAction("msg - watchlist.py - watchlist_main19 --> add artist " + artistID + " to watchlist --> starting.") 
            print("ADDING ARTIST " + artistID)
            artistResponse  = apiGetSpotify("artists/" + artistID)


            '''--> check response before continuing'''
            if artistResponse == '':
                logAction("err - watchlist.py - watchlist_main20 --> empty api response for searching artist.")
                flash("Error when searching for artist " + gv_searchTerm + ", empty response.", category="error")
                return render_template("watchlist.html")


            '''--> db'''
            db = get_db()


            '''--> artist in watchlist?'''
            cursor = db.cursor()
            if cursor.execute('SELECT id FROM WatchList WHERE id = ?', (artistID,)).fetchone() == None:
                pass    #not in db yet
            else:
                logAction("msg - watchlist.py - watchlist_main21 --> artist " + artistResponse["name"] + " already in watchlist.")
                flash("Artist " + artistResponse["name"] + " already in watchlist.", category="error")


                '''--> return html'''
                return render_template('watchlist.html', 
                                        artistList = gv_artistList,
                                        showArtistBtn = "active", 
                                        showArtistTab = "show active", 
                                        showPlaylistBtn ="" , 
                                        showPlaylistTab = "", 
                                        showUserBtn = "", 
                                        showUserTab = "")


            '''-->artist's tracks'''
            trackList       = getTracksFromArtist(artistID, False)
            logAction("msg - watchlist.py - watchlist_main20 --> grabbed artist " + artistID + "'s tracks: " + str(len(trackList)))


            '''--> check data'''
            if artistResponse["name"]:
                name = artistResponse["name"]
            else:
                name = ""

            if artistResponse["images"]:
                imglink = artistResponse["images"][0]["url"]
            else:
                imglink = ""


            '''--> add to db'''
            db.execute(
                'INSERT INTO WatchList (id, _type, _name, date_added, last_time_checked, no_of_items_checked, href, list_of_current_items, imageURL, new_items_since_last_check) VALUES (?,?,?,?,?,?,?,?,?,?)', 
                (artistID, "artist", name, datetime.now(), datetime.now(), len(trackList), "", json.dumps(trackList), imglink, 0)
            )
            db.commit()
            logAction("msg - watchlist.py - watchlist_main22 --> artist " + artistResponse["name"] + " added to watchlist.")
            flash("Artist " + artistResponse["name"] + " added to watchlist.", category="message")


            '''--> return html'''
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
                        tot = gv_total, 
                        searchTerm = gv_searchTerm, 
                        searchType = gv_searchType)


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
                                    showUserTab = "")



#--> DELETE ITEM FROM WATCHLIST - BUTTON PRESSED #
    if request.method == "GET" and not ("addArtist" in args) and ("delItem" in args) and not ("offs" in args) and not ("lim" in args) and not ("searchTerm" in args) and not ("searchType" in args):
        # https://pynative.com/python-mysql-delete-data/
        try:
            '''--> item'''
            toDelID = args["delItem"]
            logAction("msg - watchlist.py - watchlist_main30 --> delete item " + toDelID + " from watchlist --> starting.") 


            '''--> db'''
            db = get_db()

  
            '''--> delete from db'''
            cursor = db.cursor()
            cursor.execute('DELETE FROM WatchList WHERE id = ?', (toDelID,))

            if cursor.rowcount != 0:
                flash("Succesfully deleted "+ str(cursor.rowcount) + " item (" + toDelID + ") from watchlist.", category="message")
                logAction("msg - watchlist.py - watchlist_main31 --> succesfully deleted " + str(cursor.rowcount) + " item (" + toDelID + ") from watchlist.")
            else:
                flash("Nothing found while deleting item " + toDelID + " from watchlist...", category="error")
                logAction("msg - watchlist.py - watchlist_main32 --> nothing found while deleting item " + toDelID + " from watchlist.")

            db.commit()


            '''--> return html'''
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
                                    tot = gv_total, 
                                    searchTerm = gv_searchTerm, 
                                    searchType = gv_searchType)


        except Exception as ex:
            flash("Error deleting item " + toDelID + " from watchlist!", category="error")
            logAction("err - watchlist.py - watchlist_main33 --> Error deleting item " + toDelID + " --> " + str(type(ex)) + " - " + str(ex.args) + " - " + str(ex))
            logAction("TRACEBACK --> " + traceback.format_exc())
            return render_template('watchlist.html', 
                                    artistList = gv_artistList,
                                    showArtistBtn = "active", 
                                    showArtistTab = "show active", 
                                    showPlaylistBtn ="" , 
                                    showPlaylistTab = "", 
                                    showUserBtn = "", 
                                    showUserTab = "")

  
########################################################################################


##################################### FLASK INTERFACE ##################################
########################################################################################
# def loadHomePage():
#     return render_template('watchlist.html', 
#             artistList = gv_artistList,
#             showArtistBtn = "active", 
#             showArtistTab = "show active", 
#             showPlaylistBtn ="" , 
#             showPlaylistTab = "", 
#             showUserBtn = "", 
#             showUserTab = "", 
#             offs = gv_offset, 
#             lim = gv_limit, 
#             tot = gv_total, 
#             searchTerm = gv_searchTerm, 
#             searchType = gv_searchType)
########################################################################################



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





