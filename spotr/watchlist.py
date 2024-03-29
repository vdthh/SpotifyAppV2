########################################################################################
##################################### watchlist.py #####################################
############### Handles all functions related to the watchlist section #################
########################################################################################


########################################################################################
######################################### IMPORTS ######################################
########################################################################################
from asyncio import wait_for
import functools
from tabnanny import check
from tarfile import LENGTH_NAME
from flask import (Blueprint, flash, g, redirect, render_template, request, url_for)
from spotr.common import logAction
from spotr.db import get_db_connection
from datetime import datetime, timedelta
import json
import os
import binascii
import traceback
import sqlite3
from .common import addTracksToPlaylist, apiGetSpotify, changePlaylistDetails, checkIfTrackInDB, getTracksFromArtist, getTracksFromPlaylist, searchSpotify, returnSearchResults, getTrackInfo, createPlaylist, waitForGivenTimeIns
from flask import current_app
from spotr import app, globalvariables
from spotr.db import get_db_connection
from threading import Thread
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
    global gv_status

    '''--> read query parameters'''
    args=request.args      


    #--> PAGE LOAD #
    if request.method == "GET" and not ("addArtist" in args) and not ("addPlaylist" in args) and not ("delItem" in args) and not ("offs" in args) and not ("lim" in args) and not ("searchTerm" in args) and not ("searchType" in args):
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
                                    watchlistItems      = gv_watchlistItems,
                                    showArtistBtn       = "active", 
                                    showArtistTab       = "show active", 
                                    showPlaylistBtn     = "" , 
                                    showPlaylistTab     = "", 
                                    showUserBtn         = "", 
                                    showUserTab         = "",
                                    status_general      = globalvariables.general_status,
                                    show_spinner        = globalvariables.general_status_show_spinner)

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
                        showArtistBtn       = "active", 
                        showArtistTab       = "show active", 
                        showPlaylistBtn     = "" , 
                        showPlaylistTab     = "", 
                        showUserBtn         = "", 
                        showUserTab         = "",
                        status_general      = globalvariables.general_status,
                        show_spinner        = globalvariables.general_status_show_spinner)


            '''--> retrieve pagination'''
            total       = response[gv_searchType  + 's']['total']
            gv_limit    = response[gv_searchType  + 's']['limit']
            gv_offset   = response[gv_searchType  + 's']['offset']


            '''--> fill artistList'''
            for item in returnSearchResults(response, "artist"):  #{"artist": , "id": , "popularity": , "image": }
                gv_artistList.append({"artist": item["artist"], "id": item['id'], "popularity": item['popularity'], "image": item['imageurl']})


            '''--> return html'''
            return render_template("watchlist.html", 
                                    watchlistItems      = gv_watchlistItems,
                                    artistList          = gv_artistList, 
                                    playlistList        = gv_playlistList,
                                    showArtistBtn       = "active", 
                                    showArtistTab       = "show active", 
                                    showPlaylistBtn     = "" , 
                                    showPlaylistTab     = "", 
                                    showUserBtn         = "", 
                                    showUserTab         = "",
                                    tot                 = total,
                                    lim                 = gv_limit,
                                    offs                = gv_offset,
                                    searchType          = gv_searchType,
                                    searchTerm          = gv_searchTerm,
                                    status_general      = globalvariables.general_status,
                                    show_spinner        = globalvariables.general_status_show_spinner)

        except Exception as ex:
            flash("Error while searching for artist " + gv_searchTerm + ".", category="error")
            logAction("err - watchlist.py - watchlist_main5 --> error while loading page --> " + str(type(ex)) + " - " + str(ex.args) + " - " + str(ex))
            logAction("TRACEBACK --> " + traceback.format_exc())
            return render_template('watchlist.html', 
                                    artistList = gv_artistList,
                                    showArtistBtn       = "active", 
                                    showArtistTab       = "show active", 
                                    showPlaylistBtn     ="" , 
                                    showPlaylistTab     = "", 
                                    showUserBtn         = "", 
                                    showUserTab         = "",
                                    status_general      = globalvariables.general_status,
                                    show_spinner        = globalvariables.general_status_show_spinner)


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
                        showArtistBtn       = "", 
                        showArtistTab       = "", 
                        showPlaylistBtn     = "active" , 
                        showPlaylistTab     = "show active", 
                        showUserBtn         = "", 
                        showUserTab         = "",
                        status_general      = globalvariables.general_status,
                        show_spinner        = globalvariables.general_status_show_spinner)


            '''--> retrieve pagination'''
            total       = response[gv_searchType  + 's']['total']
            gv_limit    = response[gv_searchType  + 's']['limit']
            gv_offset   = response[gv_searchType  + 's']['offset']


            '''--> fill playlistList'''
            for item in returnSearchResults(response, "playlist"):  #{"name": , "id": , "description": , "image": , "owner": , "totaltracks": }
                gv_playlistList.append({"name": item["name"], "id": item['id'], "description": item['description'], "image": item['imageurl'], "owner": item['owner'], "totaltracks": item['totaltracks']})


            '''--> return html'''
            return render_template("watchlist.html", 
                                    watchlistItems      = gv_watchlistItems,
                                    artistList          = gv_artistList, 
                                    playlistList        = gv_playlistList,
                                    showArtistBtn       = "", 
                                    showArtistTab       = "", 
                                    showPlaylistBtn     = "active" , 
                                    showPlaylistTab     = "show active", 
                                    showUserBtn         = "", 
                                    showUserTab         = "",
                                    tot                 = total,
                                    lim                 = gv_limit,
                                    offs                = gv_offset,
                                    searchType          = gv_searchType,
                                    searchTerm          = gv_searchTerm,
                                    status_general      = globalvariables.general_status,
                                    show_spinner        = globalvariables.general_status_show_spinner)

        except Exception as ex:
            flash("Error while searching for artist " + gv_searchTerm + ".", category="error")
            logAction("err - watchlist.py - watchlist_main5 --> error while loading page --> " + str(type(ex)) + " - " + str(ex.args) + " - " + str(ex))
            logAction("TRACEBACK --> " + traceback.format_exc())
            return render_template('watchlist.html', 
                                    artistList = gv_artistList,
                                    showArtistBtn       = "", 
                                    showArtistTab       = "", 
                                    showPlaylistBtn     = "active", 
                                    showPlaylistTab     = "show active", 
                                    showUserBtn         = "", 
                                    showUserTab         = "",
                                    status_general      = globalvariables.general_status,
                                    show_spinner        = globalvariables.general_status_show_spinner)


    #--> ADD ARTIST OR PLAYLIST TO WATCHLIST - BUTTON PRESSED #
    if request.method == "GET"  and not ("delItem" in args) and not ("offs" in args) and not ("lim" in args) and not ("searchTerm" in args) and not ("searchType" in args):
        # globalvariables.general_status = "1 - tralalalala"
        thr = Thread(target=updateGeneralStatus, args=["1 - tralalalala"])
        thr.start()
       
        '''--> local variables'''
        lType       = ""
        lID         = ""
        lArtistBtn  = ""
        lArtistTab  = ""
        lPlstBtn    = ""
        lPlstTab    = ""
        lName       = ""


        '''--> artist or playlist?'''
        try:
            if ("addArtist" in args):
                lType = "artist"
                lName = args["artistName"]
            elif ("addPlaylist" in args):
                lType = "playlist"
                lName = args["playlistName"]
            else:
                lType = ""
                lName = ""


            '''--> get details'''
            if lType == "artist":
                lID         = args["addArtist"]
                lArtistBtn  = "active"
                lArtistTab  = "show active"
            elif lType == "playlist":
                lID         = args["addPlaylist"]
                lPlstBtn    = "active"
                lPlstTab    = "show active"  
            response = apiGetSpotify(lType + "s/" + lID)
            logAction("msg - watchlist.py - watchlist_main80 --> add " + lType + " " + lID + " to watchlist --> starting.") 
        

            '''--> (re)load watchlist items'''
            gv_watchlistItems = []  #list empty, initialize it every reload
            loadWatchlistItems()


            '''--> check response before continuing'''
            if response == '':
                logAction("err - watchlist.py - watchlist_main81 --> empty api response for searching " + lType + ".")
                flash("Error when searching for " + lType + " " + gv_searchTerm + ", empty response.", category="error")


                '''--> return html'''
                return render_template('watchlist.html', 
                                        watchlistItems      = gv_watchlistItems,
                                        artistList          = gv_artistList,
                                        playlistList        = gv_playlistList,
                                        showArtistBtn       = lArtistBtn, 
                                        showArtistTab       = lArtistTab, 
                                        showPlaylistBtn     = lPlstBtn , 
                                        showPlaylistTab     = lPlstTab, 
                                        showUserBtn         = "", 
                                        showUserTab         = "",
                                        status_general      = globalvariables.general_status,
                                        show_spinner        = globalvariables.general_status_show_spinner)


            '''--> db'''
            db = get_db_connection()
            cursor = db.cursor()

            # globalvariables.general_status = "2 - tralalalala"
            thr = Thread(target=updateGeneralStatus, args=["2 - tralalalala"])
            thr.start()


            '''--> artist/playlist/... in watchlist?'''        
            if cursor.execute('SELECT id FROM WatchList WHERE id = ?', (lID,)).fetchone() == None:
                pass    #not in db yet
            else:
                logAction("msg - watchlist.py - watchlist_main80.1 --> " + lType + " " + response["name"] + " already in watchlist.")
                flash(lType + " " + response["name"] + " already in watchlist.", category="error")


                '''--> return html'''
                return render_template('watchlist.html', 
                                        watchlistItems      = gv_watchlistItems,
                                        artistList          = gv_artistList,
                                        playlistList        = gv_playlistList,
                                        showArtistBtn       = lArtistBtn, 
                                        showArtistTab       = lArtistTab, 
                                        showPlaylistBtn     = lPlstBtn , 
                                        showPlaylistTab     = lPlstTab, 
                                        showUserBtn         = "", 
                                        showUserTab         = "",
                                        status_general      = globalvariables.general_status,
                                        show_spinner        = globalvariables.general_status_show_spinner)


            '''--> grab tracks'''
            if lType == "artist":
                tracklist       = getTracksFromArtist(lID, False)
            elif lType == "playlist":
                tracklist       = getTracksFromPlaylist(lID, False)
            logAction("msg - watchlist.py - watchlist_main82 --> grabbed " + lType + " " + lID + "'s tracks: " + str(len(tracklist)))

            # globalvariables.general_status = "3 - tralalalala"
            thr = Thread(target=updateGeneralStatus, args=["3 - tralalalala"])
            thr.start()


            '''--> check data'''
            if response["name"]:
                name = response["name"]
            else:
                name = ""

            if response["images"]:
                imglink = response["images"][0]["url"]
            else:
                imglink = ""


            '''--> check if entry in db table WatchListNewTracks exists, before adding tracks to it'''
            try:
                if cursor.execute('SELECT * FROM WatchListNewTracks').fetchone() == None:    #add first entry to db table
                    dummyList = []
                    db.execute('INSERT INTO WatchListNewTracks (id, trackList) VALUES (?,?)',("newTracks", json.dumps(dummyList)))
                    db.commit()
            except sqlite3.OperationalError:
                logAction("msg - watchlist.py - watchlist_main83 --> error while adding entry in db table WatchListNewTracks")


                '''--> return html'''
                return render_template('watchlist.html', 
                                        watchlistItems      = gv_watchlistItems,
                                        artistList          = gv_artistList,
                                        playlistList        = gv_playlistList,
                                        showArtistBtn       = lArtistBtn, 
                                        showArtistTab       = lArtistTab, 
                                        showPlaylistBtn     = lPlstBtn , 
                                        showPlaylistTab     = lPlstTab, 
                                        showUserBtn         = "", 
                                        showUserTab         = "",
                                        status_general      = globalvariables.general_status,
                                        show_spinner        = globalvariables.general_status_show_spinner)


            '''--> add artist/playlist/... to WatchList db'''
            db.execute(
                'INSERT INTO WatchList (id, _type, _name, last_time_checked, no_of_items_checked, href, list_of_current_items, imageURL, new_items_since_last_check) VALUES (?,?,?,?,?,?,?,?,?)', 
                (lID, lType, name, datetime.now(), len(tracklist), response["href"], json.dumps(tracklist), imglink, len(tracklist))
            )
            db.commit()
            logAction("msg - watchlist.py - watchlist_main84 --> " + lType + " " + name + " added to watchlist.")
            flash(lType + " " + name + " added to watchlist.", category="message")


            '''--> add artist/playlist/... tracks to WatchListNewTracks'''
            '''check tracks if in db'''
            data                = db.execute('SELECT * FROM WatchlistNewTracks WHERE id=?',("newTracks",)).fetchone()   #needed to get trackList length before stating to add tracks...
            currentTrackList    = json.loads(data[1])
            initLength          = len(currentTrackList)
            endLength           = 0


            # globalvariables.general_status = "4 - tralalalala"
            thr = Thread(target=updateGeneralStatus, args=["4 - tralalalala"])
            thr.start()


            for trck in tracklist:
                if not checkIfTrackInDB(trck, "ListenedTrack") and not checkIfTrackInDB(trck, "ToListenTrack") and not checkIfTrackInDB(trck, "WatchListNewTracks"):
                    #Not in db yet, update tracklist
                    data                = db.execute('SELECT * FROM WatchlistNewTracks WHERE id=?',("newTracks",)).fetchone() 
                    currentTrackList    = json.loads(data[1])           #data = first (and only) row of db table WatchListNewTracks, data[0] = id, data[1] = trackList
                    toAdd               = {"id": trck, "from_type": lType, "from_name": lName}  
                    currentTrackList    = currentTrackList + [toAdd]     #add track to existing tracklist
                    endLength           = len(currentTrackList) 
                    db.execute('UPDATE WatchListNewTracks SET trackList=? WHERE id=?',(json.dumps(currentTrackList), "newTracks"))
                    db.commit()
            logAction("msg - watchlist.py - watchlist_main85 --> Finished - tracks in tracklist before adding " + lType + " " + lID + ": " + str(initLength) + ", length after adding tracks: " + str(endLength) + ".")
            flash(str(endLength - initLength) + " tracks added to WatchListNewTracks (total of " +  str(endLength) + ").", category="message")                               


            '''--> (re)load watchlist items'''
            gv_watchlistItems = []  #list empty, initialize it every reload
            loadWatchlistItems()

            # globalvariables.general_status = "5s - tralalalala"
            thr = Thread(target=updateGeneralStatus, args=["5s - tralalalala"])
            thr.start()


            '''--> finished,  return html'''
            return render_template('watchlist.html', 
                                    watchlistItems      = gv_watchlistItems,
                                    artistList          = gv_artistList,
                                    playlistList        = gv_playlistList,
                                    showArtistBtn       = lArtistBtn, 
                                    showArtistTab       = lArtistTab, 
                                    showPlaylistBtn     = lPlstBtn, 
                                    showPlaylistTab     = lPlstTab, 
                                    showUserBtn         = "", 
                                    showUserTab         = "", 
                                    offs                = gv_offset, 
                                    lim                 = gv_limit, 
                                    tot                 = gv_total, 
                                    searchTerm          = gv_searchTerm, 
                                    searchType          = gv_searchType,
                                    status_general      = globalvariables.general_status,
                                    show_spinner        = globalvariables.general_status_show_spinner)


        except Exception as ex:
            flash("Error ...", category="error")
            logAction("err - watchlist.py - watchlist_main76 --> ... --> " + str(type(ex)) + " - " + str(ex.args) + " - " + str(ex))
            logAction("TRACEBACK --> " + traceback.format_exc())
            return render_template('watchlist.html', 
                                    watchlistItems      = gv_watchlistItems,
                                    artistList          = gv_artistList,
                                    playlistList        = gv_playlistList,
                                    showArtistBtn       = "", 
                                    showArtistTab       = "", 
                                    showPlaylistBtn     = "active" , 
                                    showPlaylistTab     = "show active", 
                                    showUserBtn         = "", 
                                    showUserTab         = "",
                                    offs                = gv_offset, 
                                    lim                 = gv_limit, 
                                    tot                 = gv_total, 
                                    searchTerm          = gv_searchTerm, 
                                    searchType          = gv_searchType,
                                    status_general      = globalvariables.general_status,
                                    show_spinner        = globalvariables.general_status_show_spinner)





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
                                    watchlistItems      = gv_watchlistItems,
                                    artistList          = gv_artistList,
                                    playlistList        = gv_playlistList,
                                    showArtistBtn       = "active", 
                                    showArtistTab       = "show active", 
                                    showPlaylistBtn     = "", 
                                    showPlaylistTab     = "", 
                                    showUserBtn         = "", 
                                    showUserTab         = "", 
                                    offs                = gv_offset, 
                                    lim                 = gv_limit, 
                                    tot                 = gv_total, 
                                    searchTerm          = gv_searchTerm, 
                                    searchType          = gv_searchType,
                                    status_general      = globalvariables.general_status,
                                    show_spinner        = globalvariables.general_status_show_spinner)


        except Exception as ex:
            flash("Error deleting item " + toDelID + " from watchlist!", category="error")
            logAction("err - watchlist.py - watchlist_main33 --> Error deleting item " + toDelID + " --> " + str(type(ex)) + " - " + str(ex.args) + " - " + str(ex))
            logAction("TRACEBACK --> " + traceback.format_exc())
            return render_template('watchlist.html', 
                                    artistList = gv_artistList,
                                    showArtistBtn       = "active", 
                                    showArtistTab       = "show active", 
                                    showPlaylistBtn     = "" , 
                                    showPlaylistTab     = "", 
                                    showUserBtn         = "", 
                                    showUserTab         = "",
                                    status_general      = globalvariables.general_status,
                                    show_spinner        = globalvariables.general_status_show_spinner)

  
########################################################################################
@bp_watchlist.route('/checkForNewTracks', methods=['GET', 'POST'])
def watchlist_checkForNewTracks():
    '''--> Check watchlist items for new track initiated from html page - button press'''
    logAction("msg - watchlist.py - watchlist_checkForNewTracks() --> started via button press.") 

    if not checkWatchlistItems():
        logAction("err - watchlist.py - watchlist_checkForNewTracks2() --> failed! --> false returned.") 
        flash("checkForNewTracks - manually initiated - failed!", category="error")
    else:
        logAction("msg - watchlist.py - watchlist_checkForNewTracks3() --> finished succefully.") 
        flash("checkForNewTracks - manually initiated - finished!", category="success")


    '''--> (re)load watchlist items'''
    loadWatchlistItems()

    '''--> return html'''
    return render_template('watchlist.html', 
                            watchlistItems = gv_watchlistItems,
                            artistList = gv_artistList,
                            playlistList = gv_playlistList,
                            showArtistBtn       = "active", 
                            showArtistTab       = "show active", 
                            showPlaylistBtn     = "" , 
                            showPlaylistTab     = "", 
                            showUserBtn         = "", 
                            showUserTab         = "", 
                            offs                = gv_offset, 
                            lim                 = gv_limit, 
                            tot                 = gv_total, 
                            searchTerm          = gv_searchTerm, 
                            searchType          = gv_searchType,
                            status_general      = globalvariables.general_status,
                            show_spinner        = globalvariables.general_status_show_spinner)

########################################################################################
@bp_watchlist.route('/update_status', methods=['GET'])
def updateGeneralStatus(message):
    '''--> to be called in fixed intervals by javascript in html code'''
    globalvariables.general_status = message
    print(globalvariables.general_status)
    return globalvariables.general_status

########################################################################################

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
def checkWatchlistItems():
    '''--> check every watchlist item for new tracks <--'''
    '''Add new tracks to table WatchListNewTracks - trackList'''
    '''Create playlists of these tracks of 50 tracks each'''
    '''RETURN FALSE IN CASE OF ERROR'''

    logAction("msg - watchlist.py - checkWatchListItems --> starting.") 
    try:
        '''--> db'''
        with app.app_context():
            db = get_db_connection()
            cursor = db.cursor()


    except Exception as ex:
        logAction("err - watchlist.py - checkWatchListItems2 --> error setting up db connection --> " + str(type(ex)) + " - " + str(ex.args) + " - " + str(ex))
        logAction("TRACEBACK --> " + traceback.format_exc())
        return False


    '''--> check if entry in db table WatchListNewTracks exists, before adding tracks to it'''
    try:
        if cursor.execute('SELECT * FROM WatchListNewTracks').fetchone() == None:    #add first entry to db table
            dummyList = []
            db.execute('INSERT INTO WatchListNewTracks (id, trackList) VALUES (?,?)',("newTracks", json.dumps(dummyList)))
            db.commit()
            logAction("msg - watchlist.py - checkWatchListItems3 --> Initial entry in table WatchListNewTracks created")


    except sqlite3.OperationalError:
        logAction("msg - watchlist.py - checkWatchListItems4 --> error while adding entry in db table WatchListNewTracks")
        return False


    '''--> check watchlist items for new tracks'''
    try:
        for wl_item in cursor.execute('SELECT * FROM WatchList').fetchall():
            actTracks = []  #track ids on spotify
            dbTracks  = []  #track ids in db

            if wl_item["_type"] == "artist":
                actTracks   = getTracksFromArtist(wl_item["id"], False)
            elif wl_item["_type"] == "playlist":
                actTracks   = getTracksFromPlaylist(wl_item["id"], False)
            dbTracks = json.loads(wl_item["list_of_current_items"])     #saved as string (json.dumps), converted to list with json.loads


            '''--> use crc to check for changes'''
            crcactTracks    = binascii.crc32(json.dumps(actTracks).encode('utf8'))
            crcdbTracks     = binascii.crc32(json.dumps(dbTracks).encode('utf8'))


            '''--> set new_items_since_last_check'''
            db.execute('UPDATE WatchList SET no_of_items_checked=? WHERE id=?',(len(actTracks) - len(dbTracks), wl_item["id"]))
            db.commit()

            if crcactTracks != crcdbTracks:
                '''--> new track(s) found, update db tracklist'''
                db.execute('UPDATE WatchList SET list_of_current_items=? WHERE id=?',(json.dumps(actTracks), wl_item["id"]))
                db.commit()
                db.execute('UPDATE WatchList SET no_of_items_checked=? WHERE id=?',(len(actTracks), wl_item["id"]))
                db.commit()


                '''--> check act tracks and add to WatchlistNewTracks'''
                for actTrck in actTracks:
                    if not checkIfTrackInDB(actTrck,"ListenedTrack") and not checkIfTrackInDB(actTrck, "ToListenTrack") and not checkIfTrackInDB(actTrck, "WatchListNewTracks"):
                        #Not in db yet, update tracklist
                        data                = db.execute('SELECT * FROM WatchlistNewTracks WHERE id=?',("newTracks",)).fetchone() 
                        currentTrackList    = json.loads(data[1])           #data = first (and only) row of db table WatchListNewTracks, data[0] = id, data[1] = trackList
                        toAdd               = {"id": actTrck, "from_type": wl_item["_type"], "from_name": wl_item["_name"]}  
                        currentTrackList    = currentTrackList + [toAdd]     #add track to existing tracklist
                        db.execute('UPDATE WatchListNewTracks SET trackList=? WHERE id=?',(json.dumps(currentTrackList), "newTracks"))
                        db.commit()


                '''--> Set noOfNewItems (new tracks since last 8h)'''
                date_limit = datetime.strptime(str(wl_item["last_time_checked"]),'%Y-%m-%d %H:%M:%S.%f')  + timedelta(hours=8)
                if datetime.now() > date_limit:
                    #more than 8 hours passed since a new item has been added, set noOfNewItems back to 0.
                    db.execute('UPDATE WatchList SET new_items_since_last_check=? WHERE id=?',(0, wl_item["id"]))
                    db.commit()
                    logAction("msg - watchlist.py - checkWatchListItems5 --> Set new_items_since_last_check for " + wl_item["id"] + " to 0 after 8h.") 


        '''--> Check if enough tracks in table WatchlistNewTracks for creating new playlist'''
        if checkToCreatePlaylist() != False:
            logAction("msg - watchlist.py - checkWatchListItems5.1 --> Succesfully created new playlist(s) of watchlist items.") 
        else:
            logAction("err - watchlist.py - checkWatchListItems5.2 --> error checkToCreatePlaylist()")
            return False


        '''--> finished succesfully'''
        return True        


    except Exception as ex:
        logAction("err - watchlist.py - checkWatchListItems6 --> error checking watchlist items for new tracks --> " + str(type(ex)) + " - " + str(ex.args) + " - " + str(ex))
        logAction("TRACEBACK --> " + traceback.format_exc())
        return False
    

########################################################################################
def checkToCreatePlaylist():
    '''--> check WatchListNewTracks --> trackList for enough entries'''
    '''--> if so, create a playlist of tracks from this trackList'''
    '''--> add tracks to ListenedTrack table'''
    '''--> checking if tracks are in ListenedTable has happened already before and is not re-done here'''
    '''--> return false in case of error'''
    logAction("msg - watchlist.py - checkToCreatePlaylist0 --> starting checkToCreatePlaylist()")


    '''--> call db outside of request-object'''
    with app.app_context():
        db = get_db_connection()
        cursor = db.cursor()


    try:
        '''--> Get trackList from WatchListNewTracks'''
        data                = db.execute('SELECT * FROM WatchlistNewTracks WHERE id=?',("newTracks",)).fetchone() 
        currentTrackList    = json.loads(data[1])           #data = first (and only) row of db table WatchListNewTracks, data[0] = id, data[1] = trackList
        toCreateList        = []
        loopCnt             = 0
        while len(currentTrackList) >= 50:
            loopCnt      = loopCnt + 1
            toCreateList = currentTrackList[:50]    #grab first 50 items --> https://stackoverflow.com/questions/10897339/python-fetch-first-10-results-from-a-list
            

            '''--> create new playist of these 50 tracks'''
            plstName = "gnplst_watchlistItems_" + str(datetime.now().year).zfill(4) + str(datetime.now().month).zfill(2) + str(datetime.now().day).zfill(2) + "_" + str(datetime.now().hour).zfill(2) + "h" + str(datetime.now().minute).zfill(2)
            resultCreate = createPlaylist(plstName, "Generated by Spotr. No further description for now.")
            if resultCreate != "":


                '''--> check response'''
                if "id" in resultCreate.keys() and "name" in resultCreate.keys():
                    pass# logAction("msg - watchlist.py - checkToCreatePlaylist1 --> succesfully created new empty playlist \"" + resultCreate["name"] + "\"")
                else:
                    logAction("err - watchlist.py - checkToCreatePlaylist3 --> error creating playlist \"" + plstName + "\"")
                    return False


                '''--> grab ID of newly created playlist'''
                id = resultCreate["id"]   


                '''--> wait for given time'''
                waitForGivenTimeIns(1, 2)   #Experience learns it can take a few moments for a newly created playlist to become available within spotify (api)


                '''--> add grabbed tracks to new playlist'''
                '''First create list of track IDs in WatchlistNewTracks table'''
                '''playlist_description_list is used to add to playlist description'''
                id_list                     = []
                playlist_description_list   = [[],[]]   #[0] --> from_type, [1] --> from_name
                for item in toCreateList:
                    id_list.append(item["id"])
                    playlist_description_list[0].append(item["from_type"])
                    playlist_description_list[1].append(item["from_name"])
                resultAdd = addTracksToPlaylist(id,id_list)


                '''--> check response'''
                if "snapshot_id" in resultAdd.keys():
                    pass# logAction("msg - watchlist.py - checkToCreatePlaylist5 --> Added " + str(len(toCreateList)) + " tracks to new playlist " + id)
                else:
                    logAction("err - watchlist.py - checkToCreatePlaylist7 --> failed to add tracks to new playlist " + id)
                    return False


                '''--> add tracks to ListenedTrack table'''
                for item in toCreateList:                       
                    if cursor.execute('SELECT * FROM ListenedTrack WHERE id=?',(item["id"],)).fetchone() == None: 
                        trck_info = getTrackInfo(item["id"], True)
                        db.execute('INSERT INTO ListenedTrack (id, spotify_id, album, artists, title, href, popularity, from_playlist, how_many_times_double) VALUES (?,?,?,?,?,?,?,?,?)',(item["id"], item["id"], trck_info["album"], ' '.join(trck_info["artists"]), trck_info["title"], trck_info["href"], trck_info["popularity"], "", 0))
                        db.commit()


                '''--> delete tracks in source and update'''
                del currentTrackList[:50]      
                db.execute('UPDATE WatchListNewTracks SET trackList=? WHERE id=?',(json.dumps(currentTrackList), "newTracks"))
                db.commit()
                logAction("msg - watchlist.py - checkToCreatePlaylist8 --> Tracks left in table WatchListNewTracks: " + str(len(currentTrackList)))


                '''--> TEST TEST TEST TEST'''
                
                changePlaylistDetails(id, "", createPlaylistDescription(playlist_description_list))


            else:
                logAction("err - watchlist.py - checkToCreatePlaylist9 --> Error feedback from CreatePlaylist().")


        else:
            '''--> finished'''
            logAction("msg - watchlist.py - checkToCreatePlaylist9 --> ended --> total of " + str(loopCnt) + " playlists created.")
            return resultAdd


    except Exception as ex:
        logAction("err - watchlist.py - checkToCreatePlaylist13 --> error general --> " + str(type(ex)) + " - " + str(ex.args) + " - " + str(ex))
        logAction("TRACEBACK --> " + traceback.format_exc())
        return False


########################################################################################
def createPlaylistDescription(input_list):
    '''--> Create playlist description as following:'''
    '''for each artist/playlist/... from which tracks are added to playlist'''
    '''add number & type in description'''
    '''for example: playlist Daily Mix 1: 5 tracks, playlist Daily Mix 3: 2 tracks, artist Jefke: 1 track, ...'''
    '''input_list contains 2 lists: [[from_type],[from_name]]'''
    resultString = ""
    tempList = [[],[],[]]   #from_type, from_name, sum of appearance
    print("STARTINGGGGGGGGGGGGGGGG")
    print("LIST LENGTH: " + str(len(input_list[0])))
    for i in range(len(input_list[0])):    
        if not input_list[1][i] in tempList[1]:
            print("NEW NAME FOR " + str(input_list[1][i]))
            #new name
            tempList[0].append(input_list[0][i])        #from_type
            tempList[1].append(input_list[1][i])        #from_name
            tempList[2].append(1)                       #sum of appearance
        else:
            #only increase counter
            print("INCREASE COUNTER FOR " + str(input_list[1][i]))
            position = tempList[1].index(input_list[1][i])
            tempList[2][position] = tempList[2][position] + 1      #sum of appearance

    print("LENGTH TEMPLIST: " + str(len(tempList)) + ", LENGTH TEMPLIST[0]: " + str(len(tempList[0])))

    '''--> create result string'''
    for i in range(len(tempList[0])):
        if i == 0:
            resultString = str(tempList[2][i]) + " tracks from " + tempList[0][i] + " " + tempList[1][i]
        else:
            resultString = resultString + ", " + str(tempList[2][i]) + " tracks from " + tempList[0][i] + " " + tempList[1][i]

    print("RESULTSTRING: " + resultString)
    return resultString

