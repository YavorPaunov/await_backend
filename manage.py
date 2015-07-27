#!/usr/bin/python

from flask.ext.script import Manager
from await import app, create_app

manager = Manager(app)


@manager.command
def create():
    create_app()


@manager.command
def run():
    app.run()


@manager.command
def debug(
        user='await_user',
        password='await_pass',
        host='localhost',
        database='await_db'):

    sql_config = "postgresql://{0}:{1}@{2}/{3}".format(
        user, password, host, database)
    app.config['SQLALCHEMY_DATABASE_URI'] = sql_config
    app.debug = True
    app.run()

if __name__ == '__main__':
    manager.run()
