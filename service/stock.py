import json

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import exists
from flask import request

from flask import jsonify, render_template
from orm import model
from sqlalchemy import Column, String
from flask import make_response

from logic import common
from logic import finder
from logic import inspector
from utils import encoder

from hts import kiwoom


def configure(app):
    @app.route('/stock/recommend')
    def recommend_stocks(db: SQLAlchemy):

        volatility = request.args.get('volatility')
        if volatility is not None:
            steady_roe = True
        else:
            steady_roe = False
            volatility = 0

        yield_rate = request.args.get('yield_rate')
        if yield_rate is None:
            yield_rate = 8

        stocks = finder.recommend_stocks(db, steady_roe, int(volatility), float(yield_rate))
        return render_template('recommend.html',
                               stocks_recommended=json.dumps(stocks, indent=4, cls=encoder.JSONEncoder,
                                                             ensure_ascii=False))

    @app.route('/stock/analyze/value/<code>')
    def analyze_stock(code, db: SQLAlchemy):
        stocks = []

        volatility = request.args.get('volatility')
        if volatility is None:
            volatility = 0

        yield_rate = request.args.get('yield_rate')
        if yield_rate is None:
            yield_rate = 8

        stock = finder.analyze_stock(db, code, int(volatility), float(yield_rate))
        stocks.append(stock)
        return render_template('recommend.html',
                               stocks_recommended=json.dumps(stocks, indent=4, cls=encoder.JSONEncoder,
                                                             ensure_ascii=False))

    @app.route('/stock/analyze/risk')
    def analyze_risk_all(db: SQLAlchemy):

        result = common.stock_codes(db)
        for item in result:
            if item.corp_cls == 'N':
                continue
            code = item.stock_code
            inspection = inspector.analyze_risk(db, code)
            msg = []
            for risk_result in inspection.risk_results:
                msg.append(
                    str(risk_result.risk_type.value) + " " + str(risk_result.year) + " " + str(risk_result.is_normal))
            print(inspection.company.stock_name, inspection.company.stock_code, inspection.company.corp_cls, msg)

        response = jsonify(status='OK')
        response.status = '201 CREATED'
        return response

    @app.route('/stock/analyze/risk/<code>')
    def analyze_risk(code, db: SQLAlchemy):
        inspection = inspector.analyze_risk(db, code)
        response = make_response(json.dumps(inspection, indent=4, cls=encoder.JSONEncoder, ensure_ascii=False))
        response.status = '200'
        return response

    @app.route('/index')
    def index():
        return render_template('index.html')
