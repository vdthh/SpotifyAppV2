import functools
from flask import (Blueprint, flash, g, redirect, render_template, request, url_for)
from spotr.common import logAction
from spotr.db import get_db
from datetime import datetime
import json
import os

bp = Blueprint('watchlist', __name__, url_prefix="/watchlist")

@bp.route("/", methods=["GET","POST"])
def watchlist_main():
    if request.method == 'GET':
        print("- - - - GET")

        #fetch rows from db, if any
        db = get_db()
        data = db.execute('SELECT * FROM NewWatchListTracks').fetchall()    #returns list of dicts https://docs.python.org/3/library/sqlite3.html

        # print("1 - " + data[0]["id"])
        # print(data[0].keys())

        if data is None:
            error = 'no entries in db!'
        else:
            for row in data:
                #json.dumps() function converts a Python object into a json string.
                # data_encoded = json.dumps(row["trackList"])
                # print("artist: " + row["artist"])
                print("album: " + row["id"])

        return render_template('watchlist.html')

    elif request.method == 'POST':
        print("- - - - POST")
        db = get_db()
        error = None

        tempVar = {"id": "id12" + str(datetime.now()), "album": "homework", "artist": "daft punk", "date_added": str(datetime.now())}
        # json.dumps() function converts a Python object into a json string
        tempVar_Serialized = json.dumps(tempVar)
        #convert to json string before storing in db
        #https://stackoverflow.com/questions/20444155/python-proper-way-to-store-list-of-strings-in-sqlite3-or-mysql
        try:
            date_ = str(datetime.now())
            db.execute(
                'INSERT INTO NewWatchListTracks (id, trackList) VALUES (?,?)', (date_ + "id", tempVar_Serialized)
            )
            # db.execute(
            #     "INSERT INTO NewWatchListTracks (id, trackList) VALUES (?, ?)",
            #     (id, toStore),
            # )
            db.commit()
            print("added entry to DB!" )
        except db.IntegrityError:
            print("failed to add entry to DB!" )
            error = f"Id {id} is already registered."

        #show data
        data = db.execute('SELECT * FROM NewWatchListTracks').fetchall()
        print(data[0]["trackList"])
        print(data[0].keys())

        #convert list of JSON strings to list of dicts
        data_parsed= []
        for row in data:
            # print("type: " + str(type(row)))
            print(str(row))
            parsed = json.loads(row[1])
            print(row[1])
            print(parsed["album"])
            data_parsed.append(parsed)
            # data_parsed.append(json.loads(row))

        # print("parsed: " + data_parsed[9]["trackList"]["album"])
        ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) #result --> E:\docs\phyton projects\SpotifyWebAppV2.0\spotr
        print("ROOT_DIR: " + str(ROOT_DIR))
        CONFIG_PATH= os.path.join(ROOT_DIR, 'watchlist.py') #result --> E:\docs\phyton projects\SpotifyWebAppV2.0\spotr\watchlist.py
        print('CONFIG_PATH: ' + str(CONFIG_PATH))
        logAction("TESTTEST")

        flash(error)
        return render_template('watchlist.html', data = data_parsed)



