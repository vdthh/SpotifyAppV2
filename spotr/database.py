#######################################################################################
##################################### database.py #####################################
########################## Show (and edit) database items #############################
#######################################################################################


########################################################################################
######################################### IMPORTS ######################################
########################################################################################
from typing import ItemsView
from flask import Blueprint, render_template, request, redirect, url_for, flash
from spotr.db import get_db_connection
from .common import getTrackInfo, logAction
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
    global gv_listened_list
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
        if not ("itemid" in args) and ("showdb" in args):


            #--> PAGINATION CLICKED #
            if ("offs" in args) and ("lim" in args):
                '''--> update global variables'''
                gv_display_offset   = int(args["offs"])
                gv_display_limit    = int(args["lim"])


            #--> SHOW REQUESTED DB #
            if args["showdb"] == 'favorite':
                pass

            elif args["showdb"] == "tolisten":
                pass

            elif args["showdb"] == "listened":
                '''--> show tracks from ListenedTrack-table'''
                '''--> update global variables'''
                gv_displayedDB = 'listened'
                if gv_displayedDB_prev != gv_displayedDB:
                    gv_displayedDB_prev = gv_displayedDB
                    gv_display_offset = 0


                '''--> db'''
                db = get_db_connection()
                cursor = db.cursor()


                '''--> show tracks'''
                gv_listened_list = cursor.execute('SELECT * FROM ListenedTrack LIMIT ' + str(gv_display_limit) + ' OFFSET ' + str(gv_display_offset)).fetchall()

                print("LENGTH GV_LISTENED_LIST: " + str(len(gv_listened_list)))

                #update display variable
                gv_display_total = len(cursor.execute('SELECT * FROM ListenedTrack').fetchall())
                print("GV_DISPLAYED_TOTAL: " + str(gv_display_total))
                return render_template("database.html", itemList = gv_listened_list, showdb="listened", offs=gv_display_offset, lim=gv_display_limit, tot=gv_display_total)



            elif args["showdb"] == "playlisttracks":
                pass


            elif args["showdb"] == "newtrackswatchlist":
                pass


        #--> DELETE ITEM #
        elif ("itemid" in args) and ("showdb" in args):
            pass
