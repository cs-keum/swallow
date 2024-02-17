# -*- coding: utf-8 -*-
import logging
import logging.handlers
from logging.handlers import RotatingFileHandler
import sys
import os
import configparser

from injector import Module, Injector, inject, singleton
from flask import Flask, Request, jsonify, render_template
from flask_injector import FlaskInjector
from flask_sqlalchemy import SQLAlchemy

from apscheduler.schedulers.background import BackgroundScheduler

# from hts import kiwoom

from logic import collector

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
    app = Flask(__name__,
                static_url_path='',
                static_folder='static',
                template_folder='templates')

    config_path = os.path.join(definitions.ROOT_DIR, 'config/config.ini')

    config = configparser.ConfigParser()
    config.read(config_path)

    dialect = config['DB']['DIALECT']
    driver = config['DB']['DRIVER']
    user = config['DB']['USER']
    password = config['DB']['PASSWORD']
    host = config['DB']['HOST']
    dbname = config['DB']['DBNAME']

    app.config.update(
        SQLALCHEMY_DATABASE_URI=dialect + "+" + driver + "://" + user + ":" + password + "@" + host + "/" + dbname)
    app.debug = False

    injector = Injector([AppModule(app)])
    crawler.configure(app=app)
    stock.configure(app=app)

    FlaskInjector(app=app, injector=injector)

    bind_db = injector.binder.get_binding(SQLAlchemy)
    args_list = [bind_db[0].provider.get(injector)]

    # DART에 등록되어있는 공시대상회사의 고유번호,회사명,종목코드, 최근변경일자를 파일로 제공합니다

    collector.krx_market_condition(args_list[0])
    collector.dart_all_company(args_list[0])
    collector.krx_invest_reference(args_list[0])
    # collector.krx_foreign_holding(args_list[0])

    scheduler = BackgroundScheduler()
    scheduler.add_job(func=collector.krx_market_condition, trigger='interval', args=args_list, seconds=20 * 60)
    scheduler.start()

    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(port=9090)
    # client = app.test_client()

    # response = client.get('/crawling/nfinance/companyperformance')
    # response = client.get('/crawling/dart/financialdata')
    # response = client.get('/crawling/krx/investratio')
    # response = client.get('/crawling/krx/marketcondition')

    # response = client.get('/stock/recommend')
    # response = client.get('/stock/analyze/risk')
    # response = client.get('/stock/analyze/value/029460')
    # response = client.get('/stock/analyze/risk/950130')


# response = client.get('/company/updatesector')


if __name__ == '__main__':
    main()
