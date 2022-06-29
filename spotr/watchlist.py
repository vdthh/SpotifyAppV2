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
from spotr.db import get_db_connection
from datetime import datetime
import json
import os
import traceback
from .common import apiGetSpotify, checkIfTrackInDB, getTracksFromArtist, getTracksFromPlaylist, searchSpotify, returnSearchResults, getTrackInfo
########################################################################################


########################################################################################
######################################## FLASK INIT ####################################
########################################################################################
bp_watchlist = Blueprint('watchlist', __name__, url_prefix="/watchlist")
########################################################################################



########################################################################################
######################################## VARIABLES #####################################
########################################################################################
gv_artistList              = []     #list of {"artist": , "id": , "popularity": , "image": }
gv_playlistList            = []     #list of {"name": , "id": , "description": , "image": , "owner": , "totaltracks": }
gv_watchlistItems          = []     #list of {"id:" , "type": , "name": , "image": , "dateAdded": , "dateLastCheck": , "noOfNewItems": , "listOfNewItemsID": }
gv_newTracksToSave         = []     #list of tracks ID's of new tracks to add to NewPlaylistTracks DB
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
    global gv_playlistList     
    global gv_watchlistItems    
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
            db = get_db_connection() #grab from db
            data = db.execute('SELECT * FROM WatchList').fetchall()    #returns list of dicts https://docs.python.org/3/library/sqlite3.html


            '''--> check data'''
            if data is None:
                flash("No entries in watchlist yet!", category="error")
                logAction("msg - watchlist.py - watchlist_main --> page reload --> no items to show!")


            '''--> (re)load watchlist items'''
            loadWatchlistItems()


            '''--> return html'''
            return render_template('watchlist.html', 
                                    watchlistItems = gv_watchlistItems,
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
            gv_watchlistItems = []


            '''--> (re)load watchlist items'''
            loadWatchlistItems()


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
            for item in returnSearchResults(response, "artist"):  #{"artist": , "id": , "popularity": , "image": }
                gv_artistList.append({"artist": item["artist"], "id": item['id'], "popularity": item['popularity'], "image": item['imageurl']})


            '''--> return html'''
            return render_template("watchlist.html", 
                                    watchlistItems = gv_watchlistItems,
                                    artistList = gv_artistList, 
                                    playlistList = gv_playlistList,
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


    #--> SEARCH PLAYLIST - BUTTON PRESSED - PAGINATION # 
    if (request.method == "POST" and  ("playlist_search" in request.form)) or (request.method == "GET" and not ("addArtist" in args) and ("offs" in args) and ("lim" in args) and ("searchTerm" in args) and ("searchType" in args)):
        try:
            '''--> pagination or search button press?'''
            if (request.method == "GET" and not ("addPlaylist" in args) and ("offs" in args) and ("lim" in args) and ("searchTerm" in args) and ("searchType" in args)):
                paginReq = True
                print("search playlist - pagination")
            else:
                paginReq = False
                print("search playlist - button press")

            '''--> initialize variables'''
            gv_playlistList   = [] #(re-)initialize global artist list
            gv_watchlistItems = []


            '''--> (re)load watchlist items'''
            loadWatchlistItems()


            '''--> update variables'''
            if paginReq:
                gv_searchTerm   = args["searchTerm"]
                gv_searchType   = args["searchType"]
                gv_offset       = int(args["offs"])
                gv_limit        = int(args["lim"])
            else:
                gv_searchTerm   = request.form["searchplaylistinput"] #searchterm entered in page
                gv_searchType   = "playlist"
                gv_offset       = 0
                gv_limit        = 10


            '''--> api request'''
            logAction("msg - watchlist.py - watchlist_main50 --> searching for playlist " + gv_searchTerm)
            response = searchSpotify(gv_searchTerm, gv_searchType, gv_limit, gv_offset)
            

            '''--> check response before continuing'''
            if response == '':
                logAction("err - watchlist.py - watchlist_main51 --> empty api response for searching playlist.")
                flash("Error when searching for playlist " + gv_searchTerm + ", empty response.", category="error")
                return render_template('watchlist.html', 
                        showArtistBtn = "", 
                        showArtistTab = "", 
                        showPlaylistBtn ="active" , 
                        showPlaylistTab = "show active", 
                        showUserBtn = "", 
                        showUserTab = "")


            '''--> retrieve pagination'''
            total       = response[gv_searchType  + 's']['total']
            gv_limit    = response[gv_searchType  + 's']['limit']
            gv_offset   = response[gv_searchType  + 's']['offset']


            '''--> fill playlistList'''
            for item in returnSearchResults(response, "playlist"):  #{"name": , "id": , "description": , "image": , "owner": , "totaltracks": }
                gv_playlistList.append({"name": item["name"], "id": item['id'], "description": item['description'], "image": item['imageurl'], "owner": item['owner'], "totaltracks": item['totaltracks']})


            '''--> return html'''
            return render_template("watchlist.html", 
                                    watchlistItems = gv_watchlistItems,
                                    artistList = gv_artistList, 
                                    playlistList = gv_playlistList,
                                    showArtistBtn = "", 
                                    showArtistTab = "", 
                                    showPlaylistBtn ="active" , 
                                    showPlaylistTab = "show active", 
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
                                    showArtistBtn = "", 
                                    showArtistTab = "", 
                                    showPlaylistBtn ="active" , 
                                    showPlaylistTab = "show active", 
                                    showUserBtn = "", 
                                    showUserTab = "")


    #--> ADD ARTIST TO WATCHLIST - BUTTON PRESSED #
    if request.method == "GET" and ("addArtist" in args) and not ("addPlaylist" in args) and not ("delItem" in args) and not ("offs" in args) and not ("lim" in args) and not ("searchTerm" in args) and not ("searchType" in args):
        try:
            '''--> artist details'''
            artistID        = args["addArtist"]
            logAction("msg - watchlist.py - watchlist_main19 --> add artist " + artistID + " to watchlist --> starting.") 
            artistResponse  = apiGetSpotify("artists/" + artistID)


            '''--> (re)load watchlist items'''
            gv_watchlistItems = []  #list empty, initialize it every reload
            loadWatchlistItems()


            '''--> check response before continuing'''
            if artistResponse == '':
                logAction("err - watchlist.py - watchlist_main20 --> empty api response for searching artist.")
                flash("Error when searching for artist " + gv_searchTerm + ", empty response.", category="error")
                return render_template("watchlist.html")


            '''--> db'''
            db = get_db_connection()
            cursor = db.cursor()


            '''--> artist in watchlist?'''        
            if cursor.execute('SELECT id FROM WatchList WHERE id = ?', (artistID,)).fetchone() == None:
                pass    #not in db yet
            else:
                logAction("msg - watchlist.py - watchlist_main21 --> artist " + artistResponse["name"] + " already in watchlist.")
                flash("Artist " + artistResponse["name"] + " already in watchlist.", category="error")


                '''--> return html'''
                return render_template('watchlist.html', 
                                        watchlistItems = gv_watchlistItems,
                                        artistList = gv_artistList,
                                        playlistList = gv_playlistList,
                                        showArtistBtn = "active", 
                                        showArtistTab = "show active", 
                                        showPlaylistBtn ="" , 
                                        showPlaylistTab = "", 
                                        showUserBtn = "", 
                                        showUserTab = "")


            '''-->artist's tracks'''
            artistTrackList       = getTracksFromArtist(artistID, False)
            logAction("msg - watchlist.py - watchlist_main20 --> grabbed artist " + artistID + "'s tracks: " + str(len(artistTrackList)))


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
                'INSERT INTO WatchList (id, _type, _name, last_time_checked, no_of_items_checked, href, list_of_current_items, imageURL, new_items_since_last_check) VALUES (?,?,?,?,?,?,?,?,?)', 
                (artistID, "artist", name, datetime.now(), len(artistTrackList), "", json.dumps(artistTrackList), imglink, 0)
            )
            db.commit()
            logAction("msg - watchlist.py - watchlist_main22 --> artist " + name + " added to watchlist.")
            flash("Artist " + name + " added to watchlist.", category="message")





            '''--> add artist's tracks to NewWatchListTracks'''
            for trck in artistTrackList:
                CREATE TABLE IF NOT EXISTS info (PRIMARY KEY id int, username text, password text)
                create function in common 'checkIfTableExists'?


            '''--> return html'''
            return render_template('watchlist.html', 
                        watchlistItems = gv_watchlistItems,
                        artistList = gv_artistList,
                        playlistList = gv_playlistList,
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


    #--> ADD PLAYLIST TO WATCHLIST - BUTTON PRESSED #
    if request.method == "GET" and not ("addArtist" in args) and ("addPlaylist" in args) and not ("delItem" in args) and not ("offs" in args) and not ("lim" in args) and not ("searchTerm" in args) and not ("searchType" in args):
        try:
            '''--> playlist details'''
            playlistID        = args["addPlaylist"]
            logAction("msg - watchlist.py - watchlist_main70 --> add playlist " + playlistID + " to watchlist --> starting.") 
            playlistResponse  = apiGetSpotify("playlists/" + playlistID)


            '''--> (re)load watchlist items'''
            gv_watchlistItems = []  #list empty, initialize it every reload
            loadWatchlistItems()


            '''--> check response before continuing'''
            if playlistResponse == '':
                logAction("err - watchlist.py - watchlist_main71 --> empty api response for searching playlist.")
                flash("Error when searching for playlist " + gv_searchTerm + ", empty response.", category="error")
                return render_template("watchlist.html")


            '''--> db'''
            db = get_db_connection()
            cursor = db.cursor()


            '''--> playlist in watchlist?'''        
            if cursor.execute('SELECT id FROM WatchList WHERE id = ?', (playlistID,)).fetchone() == None:
                pass    #not in db yet
            else:
                logAction("msg - watchlist.py - watchlist_main72 --> playlist " + playlistResponse["name"] + " already in watchlist.")
                flash("Playlist " + playlistResponse["name"] + " already in watchlist.", category="error")


                '''--> return html'''
                return render_template('watchlist.html', 
                                        watchlistItems = gv_watchlistItems,
                                        artistList = gv_artistList,
                                        playlistList = gv_playlistList,
                                        showArtistBtn = "active", 
                                        showArtistTab = "show active", 
                                        showPlaylistBtn ="" , 
                                        showPlaylistTab = "", 
                                        showUserBtn = "", 
                                        showUserTab = "")


            '''-->playlist's tracks'''
            trackList       = getTracksFromPlaylist(playlistID, False)
            logAction("msg - watchlist.py - watchlist_main73 --> grabbed playlist " + playlistID + "'s tracks: " + str(len(trackList)))


            '''--> check tracks and add to newWatchlistTracks db!'''



            '''--> check data'''
            if playlistResponse["name"]:
                name = playlistResponse["name"]
            else:
                name = ""

            if playlistResponse["images"]:
                imglink = playlistResponse["images"][0]["url"]
            else:
                imglink = ""


            '''--> add to db'''
            db.execute(
                'INSERT INTO WatchList (id, _type, _name, date_added, last_time_checked, no_of_items_checked, href, list_of_current_items, imageURL, new_items_since_last_check) VALUES (?,?,?,?,?,?,?,?,?,?)', 
                (playlistID, "playlist", name, datetime.now(), datetime.now(), len(trackList), playlistResponse["href"], json.dumps(trackList), imglink, 0)
            )
            db.commit()
            logAction("msg - watchlist.py - watchlist_main22 --> artist " + artistResponse["name"] + " added to watchlist.")
            flash("Artist " + artistResponse["name"] + " added to watchlist.", category="message")


            '''--> return html'''
            return render_template('watchlist.html', 
                        watchlistItems = gv_watchlistItems,
                        artistList = gv_artistList,
                        playlistList = gv_playlistList,
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
            db = get_db_connection()

  
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


            '''--> (re)load watchlist items'''
            gv_watchlistItems = []  #list empty, initialize it every reload
            loadWatchlistItems() 


            '''--> return html'''
            return render_template('watchlist.html', 
                                    watchlistItems = gv_watchlistItems,
                                    artistList = gv_artistList,
                                    playlistList = gv_playlistList,
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


########################################################################################
######################################## FUNCTIONS #####################################
########################################################################################
def loadWatchlistItems():
    '''--> fill global list with watchlist items from db'''
    '''--> db'''
    logAction("msg - watchlist.py - watchlist_main40 --> (re)loading watchlist items")
    db = get_db_connection()
    cursor = db.cursor()


    '''--> load items from db and fill gv list'''
    for item in cursor.execute('SELECT * FROM WATCHLIST').fetchall():
        print(item["imageURL"])
        gv_watchlistItems.append({"id": item['id'], 
                                "type": item['_type'], 
                                "name": item["_name"], 
                                "image": item["imageURL"], 
                                "dateAdded": item["date_added"], 
                                "dateLastCheck": item["last_time_checked"], 
                                "noOfNewItems": item["new_items_since_last_check"], 
                                "listOfNewItemsID": item["list_of_current_items"]})

########################################################################################


######################################## FUNCTIONS #####################################


########################################################################################


##################################### FLASK INTERFACE ##################################
########################################################################################

########################################################################################


########################################################################################





# get_db()
# if checkIfTrackInDB("7ghW6VFlZN7U86vaYrwlrS", "WatchList"):
#     print("TRUE")
# else:
#     print("FALSE")