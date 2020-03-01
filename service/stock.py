import time
import requests
import pandas as pd
from io import BytesIO

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base

from flask import Request, jsonify, render_template
from orm import model
from sqlalchemy import Column, String

from logic import finder


def configure(app):

    @app.route('/stock/recommend')
    def recommend_stocks(db: SQLAlchemy):

        stocks = finder.recommend_stocks(db)
        print(stocks)

        return render_template('index.html')

    @app.route('/stock/analyze/<code>')
    def analyze_stock(code, db: SQLAlchemy):

        stock = finder.analyze_stock(db, code)
        print(stock.as_dict())

        return stock.as_dict()

    @app.route('/index')
    def index():

        return render_template('index.html')
