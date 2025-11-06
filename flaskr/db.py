import sqlite3
from datetime import date, datetime

import click
from flask import current_app, g

"""
g: a special object that is unique for each request.
current_app: is another special object that points to the Flask application handling the request.
sqlite3.connect(): establishes a connection to the file pointed at by the DATABASE configuration key.
sqlite3.Row: tells the connection to return rows that behave like dicts.
close_db(): checks if a connection was created by checking if g.db was set.
open_resource(): opens a file relative to the flaskr package, which is useful since you won't necessarily know where that location is when deploying the application later.
click.command(): defines a command line command called init-db that calls the init_db() and shows a message to the user.
sqlite3.register_converter(): tells Python how to interpret timestamp values in the database. We convert the value to a datetime.datetime.
app.teardown_appcontext(): tells Flask to call the function when cleaning up after returning the response.
app.cli.add_command(): adds a new command that can be called with the flask command.
"""

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables"""
    init_db()
    click.echo('Initialized the database.')


sqlite3.register_converter(
    "timestamp", lambda v: datetime.fromisoformat(v.decode())
)


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)