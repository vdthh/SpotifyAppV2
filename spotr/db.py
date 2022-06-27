########################################################################################
######################################### db.py ########################################
######################### db-related functions and procedures ##########################
########################################################################################


########################################################################################
######################################### IMPORTS ######################################
############# https://flask.palletsprojects.com/en/2.1.x/tutorial/factory/ #############
#################### https://www.digitalocean.com/community/tutorials/ #################
################# how-to-use-an-sqlite-database-in-a-flask-application #################
########################################################################################
import sqlite3
import click
from flask import current_app
from flask.cli import with_appcontext
########################################################################################


########################################################################################
######################################## DATABASE #####################################
########################################################################################
def init_db():
    '''--> Calling this will delete all current data stored in database.db!!!'''
    connection = sqlite3.connect('database.db')

    with current_app.open_resource('schema.sql') as f:
        connection.executescript(f.read().decode('utf-8'))

    connection.close()



'''--> make init_db() callable via cli'''
@click.command('init-db')   #command line command
@with_appcontext
def init_db_command():
    #clears existing data and creates new tables
    init_db()
    click.echo('Initialized the database!')

def add_init_app_command(app):
    app.cli.add_command(init_db_command)    #make init_db_command() accessible from the command line via command 'init-db'

def get_db_connection():
    conn = sqlite3.connect('database.py')
    conn.row_factory = sqlite3.Row
    return conn 
########################################################################################