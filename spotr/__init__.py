########################################################################################
###################################### __init__.py #####################################
##### The __init__.py serves double duty: it will contain the application factory, #####
##### and it tells Python that the flaskr directory should be treated as a package #####
########################################################################################


########################################################################################
######################################### IMPORTS ######################################
########################################################################################
import os
from flask import Flask
from . import db, globalvariables
import sqlite3

#Removes request warnings from console
from urllib3 import logging
########################################################################################


########################################################################################
####################################### FLASK APP ######################################
############# https://flask.palletsprojects.com/en/2.1.x/tutorial/factory/ #############
#################### https://www.digitalocean.com/community/tutorials/ #################
################# how-to-use-an-sqlite-database-in-a-flask-application #################
########################################################################################
'''--> create and configure spotify app'''
 #disable insecurewarnings in terminal when performing api requests without certificate: https://urllib3.readthedocs.io/en/latest/advanced-usage.html#ssl-warnings
logging.captureWarnings(True)

app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
                SECRET_KEY='dev', 
                DATABASE=os.path.join(app.instance_path, 
                'spotr.sqlite'))

app.config.from_pyfile('config.py', silent=True)


'''--> does instance folder exists'''
try:
    os.makedirs(app.instance_path)
except OSError:
    pass


'''--> register init_db_command function with the app - before returning app'''
db.add_init_app_command(app)


'''--> register blueprint(s)'''
'''--> imports need to happen AFTER app = Flask is called! Otherwise circular import'''
from . import watchlist, home, database   #blueprints
app.register_blueprint(watchlist.bp_watchlist)
app.register_blueprint(home.bp_home)
app.register_blueprint(database.bp_database)



'''--> initialize global variables'''
globalvariables.init()
########################################################################################

#To run app from terminal, first set FLASK_APP via command: $env:FLASK_APP = "spotr"