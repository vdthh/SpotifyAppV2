import os
from flask import Flask

def create_app(test_config=None):
    #create and configure spotify app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(SECRET_KEY='dev', DATABASE=os.path.join(app.instance_path, 'spotr.sqlite'))

    if test_config is None:
        #load instance config when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        #load the test config
        app.config.from_mapping(test_config)

    #does instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    return app

#To run app from terminal, first set FLASK_APP via command: $env:FLASK_APP = "spotr"