import json

from flask_sqlalchemy import SQLAlchemy

from flask import jsonify, render_template
from orm import model
from sqlalchemy import Column, String
from flask import make_response

from logic import common
from logic import finder
from logic import filter

from hts import kiwoom


def configure(app):
    @app.route('/stock/recommend')
    def recommend_stocks(db: SQLAlchemy, hts: kiwoom.Kiwoom):
        stocks = finder.recommend_stocks(db)
        for stock in stocks:
            print(stock.as_dict())

        return render_template('index.html')

    @app.route('/stock/analyze/value/<code>')
    def analyze_stock(code, db: SQLAlchemy):
        stock = finder.analyze_stock(db, code)
        print(stock.as_dict())
        resp = make_response(json.dumps(stock.as_dict()))
        return resp

    @app.route('/stock/analyze/risk/<code>')
    def analyze_risk(code, db: SQLAlchemy):
        result = common.stock_codes(db)
        for item in result:
            if item.corp_cls == 'N':
                continue
            code = item.stock_code
            revenue_risk_result = filter.analyze_revenue_risk(db, code)
            business_ross_risk_result = filter.analyze_business_ross_risk(db, code)
            print("code : ", code, revenue_risk_result, business_ross_risk_result)

        response = jsonify(status='OK')
        response.status = '201 CREATED'
        return response

    @app.route('/index')
    def index():
        return render_template('index.html')
