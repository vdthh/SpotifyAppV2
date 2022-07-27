#######################################################################################
##################################### database.py #####################################
########################## Show (and edit) database items #############################
#######################################################################################


########################################################################################
######################################### IMPORTS ######################################
########################################################################################
from __future__ import absolute_import
from typing import ItemsView
from flask import Blueprint, render_template, request, redirect, url_for, flash
from spotr.db import get_db_connection
from .common import getTrackInfo, logAction
import traceback
from flask import current_app
from spotr import app
import json
########################################################################################


########################################################################################
######################################## FLASK INIT ####################################
########################################################################################
bp_database = Blueprint('database', __name__, url_prefix="/database")
########################################################################################


########################################################################################
######################################## VARIABLES #####################################
########################################################################################
gv_listened_list            = []  
gv_displayedDB              = ""    #stores the currently displayed DB
gv_displayedDB_prev         = ""
gv_display_total            = 0
gv_display_offset           = 0
gv_display_limit            = 100   #100 items per page
########################################################################################


########################################################################################
##################################### FLASK INTERFACE ##################################
########################################################################################
# HTML ROUTING #
@bp_database.route("/", methods=['GET', 'POST'])
def database_main():
    '''--> main routine'''
    '''--> initialize gloval variables'''
    global gv_items_list
    global gv_displayedDB 
    global gv_display_total
    global gv_display_offset
    global gv_display_limit
    global gv_displayedDB_prev   


    '''--> read query parameters'''
    args=request.args


    #-->  PAGE LOAD#
    if request.method == "GET":


        #--> DATABASE SELECTED IN DROPDOWN MENU OR PAGINATION CLICKED #
        if not ("toDelID" in args) and ("showdb" in args):


            #--> PAGINATION CLICKED #
            if ("offs" in args) and ("lim" in args):
                '''--> update global variables'''
                gv_display_offset   = int(args["offs"])
                gv_display_limit    = int(args["lim"])


            #--> SHOW REQUESTED DB #
            if args["showdb"] == 'favorite':
                try:
                    '''--> show tracks from FavoriteTrack-table'''
                    '''--> update global variables'''
                    gv_displayedDB = 'favorite'
                    if gv_displayedDB_prev != gv_displayedDB:
                        gv_displayedDB_prev = gv_displayedDB
                        gv_display_offset = 0


                    '''--> db'''
                    db      = get_db_connection()
                    cursor  = db.cursor()


                    '''--> show tracks'''
                    updateItemList("FavoriteTrack", gv_display_limit, gv_display_offset)


                    '''--> update display variable'''
                    gv_display_total = len(cursor.execute('SELECT * FROM FavoriteTrack').fetchall())


                    '''--> return html response'''
                    return render_template("database.html", 
                                            itemList    = gv_items_list, 
                                            showdb      = "favorite", 
                                            offs        = gv_display_offset, 
                                            lim         = gv_display_limit, 
                                            tot         = gv_display_total)

                except Exception as ex:
                    flash("Error displaying items in FavoriteTrack table.", category="error")
                    logAction("err - database.py - database_main41 --> error while displaying items in FavoriteTrack table --> " + str(type(ex)) + " - " + str(ex.args) + " - " + str(ex))
                    logAction("TRACEBACK --> " + traceback.format_exc())
                        

            elif args["showdb"] == "tolisten":
                try:
                    '''--> show tracks from ToListenTrack-table'''
                    '''--> update global variables'''
                    gv_displayedDB = 'tolisten'
                    if gv_displayedDB_prev != gv_displayedDB:
                        gv_displayedDB_prev = gv_displayedDB
                        gv_display_offset = 0


                    '''--> db'''
                    db      = get_db_connection()
                    cursor  = db.cursor()


                    '''--> show tracks'''
                    updateItemList("ToListenTrack", gv_display_limit, gv_display_offset)


                    '''--> update display variable'''
                    gv_display_total = len(cursor.execute('SELECT * FROM ToListenTrack').fetchall())


                    '''--> return html response'''
                    return render_template("database.html", 
                                            itemList    = gv_items_list, 
                                            showdb      = "tolisten", 
                                            offs        = gv_display_offset, 
                                            lim         = gv_display_limit, 
                                            tot         = gv_display_total)

                except Exception as ex:
                    flash("Error displaying items in ToListenTrack table.", category="error")
                    logAction("err - database.py - database_main45 --> error while displaying items in ToListenTrack table --> " + str(type(ex)) + " - " + str(ex.args) + " - " + str(ex))
                    logAction("TRACEBACK --> " + traceback.format_exc())

            elif args["showdb"] == "listened":
                try:
                    '''--> show tracks from ListenedTrack-table'''
                    '''--> update global variables'''
                    gv_displayedDB = 'listened'
                    if gv_displayedDB_prev != gv_displayedDB:
                        gv_displayedDB_prev = gv_displayedDB
                        gv_display_offset = 0


                    '''--> db'''
                    db      = get_db_connection()
                    cursor  = db.cursor()


                    '''--> show tracks'''
                    # gv_items_list = cursor.execute('SELECT * FROM ListenedTrack LIMIT ' + str(gv_display_limit) + ' OFFSET ' + str(gv_display_offset)).fetchall()
                    updateItemList("ListenedTrack", gv_display_limit, gv_display_offset)


                    '''--> update display variable'''
                    gv_display_total = len(cursor.execute('SELECT * FROM ListenedTrack').fetchall())


                    '''--> return html response'''
                    return render_template("database.html", 
                                            itemList    = gv_items_list, 
                                            showdb      = "listened", 
                                            offs        = gv_display_offset, 
                                            lim         = gv_display_limit, 
                                            tot         = gv_display_total)

                except Exception as ex:
                    flash("Error displaying items in ListenedTrack table.", category="error")
                    logAction("err - database.py - database_main50 --> error while displaying items in ListenedTrack table --> " + str(type(ex)) + " - " + str(ex.args) + " - " + str(ex))
                    logAction("TRACEBACK --> " + traceback.format_exc())


            elif args["showdb"] == "playlisttracks":
                pass
                #TODO


            elif args["showdb"] == "newtrackswatchlist":
                try:
                    '''--> show tracks from WatchListNewTracks-trackList'''
                    '''--> update global variables'''
                    gv_displayedDB = 'newtrackswatchlist'
                    if gv_displayedDB_prev != gv_displayedDB:
                        gv_displayedDB_prev  = gv_displayedDB
                        gv_display_offset    = 0


                    '''--> db'''
                    db      = get_db_connection()
                    cursor  = db.cursor()


                    '''--> get data'''
                    data                    = db.execute('SELECT * FROM WatchlistNewTracks WHERE id=?',("newTracks",)).fetchone()
                    if data: 
                        currentTrackList    = json.loads(data[1])           #data = first (and only) row of db table WatchListNewTracks, data[0] = id, data[1] = trackList
                        gv_display_total    = len(currentTrackList)              
                        currentTrackList    = currentTrackList[gv_display_offset:(gv_display_offset + gv_display_limit)]
                    else:
                        currentTrackList    = []   #no data in table, empty list


                    '''--> grab trackinfo for each track'''
                    '''First create list of track IDs in WatchlistNewTracks table'''
                    id_list = []
                    for item in currentTrackList:
                        id_list.append(item["id"])

                    gv_items_list   = []
                    for trackID in id_list:
                        track                      = getTrackInfo(trackID, True)
                        itemToAdd       = {}
                        itemToAdd["artists"]       = ' '.join(track["artists"])
                        itemToAdd["title"]         = track["title"]
                        itemToAdd["spotify_id"]    = trackID
                        itemToAdd["album"]         = track["album"]
                        itemToAdd["date_added"]    = ""
                        gv_items_list.append(itemToAdd)


                    '''--> return html response'''
                    return render_template("database.html", 
                                            itemList    = gv_items_list, 
                                            showdb      = "newtrackswatchlist", 
                                            offs        = gv_display_offset, 
                                            lim         = gv_display_limit, 
                                            tot         = gv_display_total)

                except Exception as ex:
                    flash("Error displaying items in WatchlistNewTracks table.", category="error")
                    logAction("err - database.py - database_main65 --> error while displaying items in WatchlistNewTracks table --> " + str(type(ex)) + " - " + str(ex.args) + " - " + str(ex))
                    logAction("TRACEBACK --> " + traceback.format_exc())


            '''--> display purposes, only reset gv_offset when a new db needs to be showed'''
            gv_displayedDB_prev = args["showdb"]

        #--> DELETE ITEM #
        elif ("toDelID" in args) and ("showdb" in args):
            print("DELETING")
            '''--> delete item from table'''
            '''--> db'''
            db      = get_db_connection()
            cursor  = db.cursor()

            '''--> which table/track'''
            dbToShow = ""
            if args["showdb"] == "favorite":
                dbToShow = "FavoriteTrack"
                cursor.execute('DELETE FROM FavoriteTrack WHERE id=?', (args["toDelID"],))
                db.commit()         
            elif args["showdb"] == "tolisten":
                dbToShow = "ToListenTrack"
                cursor.execute('DELETE FROM ToListeTrack WHERE id=?', (args["toDelID"],))
                db.commit() 
            elif args["showdb"] == "listened":
                dbToShow = "ListenedTrack"
                cursor.execute('DELETE FROM ListenedTrack WHERE id=?', (args["toDelID"],))
                db.commit()
            elif args["showdb"] == "playlisttracks":
                dbToShow = ""
                pass
            elif args["showdb"] == "newtrackswatchlist":
                dbToShow = "WatchListNewTracks"
                data                = db.execute('SELECT * FROM WatchlistNewTracks WHERE id=?',("newTracks",)).fetchone() 
                currentTrackList    = json.loads(data[1])           #data = first (and only) row of db table WatchListNewTracks, data[0] = id, data[1] = trackList
                print("LIST LENGTH BEFORE: " + str(len(currentTrackList)))
                currentTrackList.remove(args["toDelID"])
                print("LIST LENGTH AFTER: " + str(len(currentTrackList)))
                db.execute('UPDATE WatchlistNewTracks SET trackList=? WHERE id=?',(currentTrackList, "newTracks"))
                db.commit()            

            '''--> reload tracks'''
            updateItemList(dbToShow, gv_display_limit, gv_display_offset)
            # gv_items_list = cursor.execute('SELECT * FROM ListenedTrack LIMIT ' + str(gv_display_limit) + ' OFFSET ' + str(gv_display_offset)).fetchall()


            '''--> feedback'''
            flash("Deleted track " + args["toDelID"] + " from table " + args["showdb"], category="success")
            logAction("msg - database.py - database_main80 --> Deleted track " + args["toDelID"] + " from table " + args["showdb"])


            '''--> return html response'''
            return render_template("database.html", 
                                    itemList    = gv_items_list, 
                                    showdb      = "listened", 
                                    offs        = gv_display_offset, 
                                    lim         = gv_display_limit, 
                                    tot         = gv_display_total)

########################################################################################


########################################################################################
######################################## FUNCTIONS #####################################
########################################################################################
def updateItemList(dbName, lim, offs):
    '''--> update gv_items_list'''
    '''--> global variables'''
    global gv_items_list
    global gv_display_total

    try:
        '''--> call db outside of request-object'''
        with app.app_context():
            db = get_db_connection()
            cursor = db.cursor()


        '''--> grab tracks'''
        if dbName == "ListenedTrack" or dbName == "ToListenTrack" or dbName == "WatchList" or dbName == "FavoriteTrack" or dbName == "LikedTrack":
            gv_display_total = len(cursor.execute('SELECT * FROM ' + dbName).fetchall())
            if lim == 0 and offs == 0:
                #request without limit or offset 
                gv_items_list = cursor.execute('SELECT * FROM ' + dbName).fetchall()
            else:
                #request with limit and offset
                gv_items_list = cursor.execute('SELECT * FROM ' + dbName + ' LIMIT ' + str(lim) + ' OFFSET ' + str(offs)).fetchall()      
        elif dbName == "WatchListNewTracks":
            data                = db.execute('SELECT * FROM WatchlistNewTracks WHERE id=?',("newTracks",)).fetchone()   #get total tracks, purely for display purposes
            currentTrackList    = json.loads(data[1])           
            gv_display_total    = len(currentTrackList) 
            if lim == 0 and offs == 0:
                #request without limit or offset 
                data            = cursor.execute('SELECT * FROM ' + dbName + ' WHERE id=?',("newTracks",)).fetchone()
                gv_items_list   = json.loads(data[1])
            else:
                #request with limit and offset
                data               = cursor.execute('SELECT * FROM ' + dbName + ' WHERE id=?',("newTracks",)).fetchone()
                currentTrackList   = json.loads(data[1])
                gv_items_list      = currentTrackList[offs:lim]

    except Exception as ex:
        flash("Error in updateItemList() for dbName " + dbName + ", lim " + str(lim) + " and offs " + str(offs), category="error")
        logAction("err - database.py - database_main80 --> Error in updateItemList() for dbName " + dbName + ", lim " + str(lim) + " and offs " + str(offs) + "--> " + str(type(ex)) + " - " + str(ex.args) + " - " + str(ex))
        logAction("TRACEBACK --> " + traceback.format_exc())

########################################################################################