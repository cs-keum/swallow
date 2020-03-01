# -*- coding: utf-8 -*-
import logging
import logging.handlers
from logging.handlers import RotatingFileHandler
import os
import configparser

from injector import Module, Injector, inject, singleton
from flask import Flask, Request, jsonify, render_template
from flask_injector import FlaskInjector
from flask_sqlalchemy import SQLAlchemy

from service import stock
from service import crawler

import definitions
from orm import model

configPath = os.environ.get('CONFIG_PATH', None)
if configPath is None:
    configPath = '../config.ini'


class AppModule(Module):
    def __init__(self, app):
        self.app = app

    """Configure the application."""

    def configure(self, binder):
        # app = binder.injector.get(Flask)
        # We configure the DB here, explicitly, as Flask-SQLAlchemy requires
        # the DB to be configured before request handlers are called.

        db = self.configure_db(self.app)
        binder.bind(SQLAlchemy, to=db, scope=singleton)

        # self.configure_log(self.app)

    def configure_db(self, app):
        db = SQLAlchemy(app)
        model.Base.metadata.create_all(db.engine)
        return db

    # def configure_log(self, app):
    #     stream_handler = logging.StreamHandler()
    #     stream_handler.setLevel(logging.DEBUG)
    #     app.logger.addHandler(stream_handler)
    #     return


def main():
    app = Flask(__name__)

    config_path = os.path.join(definitions.ROOT_DIR, 'config/config.ini')

    config = configparser.ConfigParser()
    config.read(config_path)

    dialect = config['DB']['DIALECT']
    driver = config['DB']['DRIVER']
    user = config['DB']['USER']
    password = config['DB']['PASSWORD']
    host = config['DB']['HOST']
    dbname = config['DB']['DBNAME']

    app.config.update(SQLALCHEMY_DATABASE_URI=dialect + "+" + driver + "://" + user + ":" + password + "@" + host + "/" + dbname)
    app.debug = False

    injector = Injector([AppModule(app)])
    crawler.configure(app=app)
    stock.configure(app=app)

    FlaskInjector(app=app, injector=injector)

    app.run(port=9090, debug=True)

    # client = app.test_client()

    # response = client.get('/crawling/krx/investratio')
    # response = client.get('/stock/recommend')
    # response = client.get('/stock/analyze/029460')

    # response = client.get('/crawling/nfinance/companyperformance')

    # response = client.get('/company/updatesector')


if __name__ == '__main__':
    main()