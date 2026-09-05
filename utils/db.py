

from flask import g, current_app
from flask_mysqldb import MySQL

mysql = MySQL()


def get_db():
    if 'db_cursor' not in g:
        g.db_cursor = mysql.connection.cursor()
    return g.db_cursor


def query_db(query, args=(), one=False):
    cur = get_db()
    cur.execute(query, args)
    rv = cur.fetchall()
    if one:
        return rv[0] if rv else None
    return rv


def execute_db(query, args=()):
    cur = get_db()
    cur.execute(query, args)
    mysql.connection.commit()
    return cur.lastrowid


def close_db(e=None):
    cursor = g.pop('db_cursor', None)
    if cursor is not None:
        cursor.close()


def init_db(app):
    mysql.init_app(app)
    app.teardown_appcontext(close_db)
