import os

from flask import Flask, render_template, request
# from flask_mysqldb import MySQL

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config['SECRET_KEY'] = 'dev'
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'testuser'
    app.config['MYSQL_PASSWORD'] = 'test623'
    app.config['MYSQL_DB'] = 'testdb'
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

    # mysql = MySQL(current_app)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import auth
    app.register_blueprint(auth.bp)
    
    from . import feed
    app.register_blueprint(feed.bp)

    from . import progress
    app.register_blueprint(progress.bp)

    app.add_url_rule('/', endpoint='index') # Send requests with '/' to feed (routes to index)
    return app

if __name__=="main":
    app = create_app()