from flask_mysqldb import MySQL
from flask import current_app, g
import MySQLdb

def connect_db():
    if 'db' not in g:
        g.db=MySQLdb.connect(current_app.config['MYSQL_HOST'], current_app.config['MYSQL_USER'], current_app.config['MYSQL_PASSWORD'], current_app.config['MYSQL_DB'],cursorclass=MySQLdb.cursors.DictCursor)
        print("Connected")
    return g.db

def close_cur(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()