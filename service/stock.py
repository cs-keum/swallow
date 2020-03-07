import json

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import exists

from flask import jsonify, render_template
from orm import model
from sqlalchemy import Column, String
from flask import make_response

from logic import common
from logic import finder
from logic import inspector
from utils import encoder

from logic import collector

from hts import kiwoom


def configure(app):
    @app.route('/stock/recommend')
    def recommend_stocks(db: SQLAlchemy):
        stocks = finder.recommend_stocks(db)
        for stock in stocks:
            print(stock.as_dict())

        return render_template('index.html')

    @app.route('/stock/analyze/value/<code>')
    def analyze_stock(code, db: SQLAlchemy):
        stock = finder.analyze_stock(db, code)
        # print(stock.as_dict())
        response = make_response(json.dumps(stock, indent=4, cls=encoder.JSONEncoder, ensure_ascii=False))
        inspector.status = '200'
        return response

    @app.route('/stock/analyze/risk/<code>')
    def analyze_risk(code, db: SQLAlchemy):
        inspection = inspector.analyze_risk(db, code)
        response = make_response(json.dumps(inspection, indent=4, cls=encoder.JSONEncoder, ensure_ascii=False))
        response.status = '200'
        return response

        # result = common.stock_codes(db)
        # for item in result:
        #     if item.corp_cls == 'N':
        #         continue
        #     code = item.stock_code
        #
        #     # risk_results = filter.analyze_revenue_risk(db, code)
        #     # risk_results = filter.analyze_business_loss_risk(db, code)
        #     # risk_results = filter.analyze_operating_loss_risk(db, code)
        #     risk_results = filter.analyze_capital_impairment_risk(db, code)
        #
        #     for result in risk_results:
        #         if result.is_normal is not None and not result.is_normal:
        #             print(result.company.stock_code, result.company.stock_name, result.risk_type, result.year,
        #                   result.is_normal, result.evidence)
        #
        #         # if result.is_normal is None:
        #         #     if db.session.query(exists().where(model.FinancialData.corp_code == item.corp_code).where(
        #         #             model.FinancialData.reprt_code == '11011')).scalar():
        #         #         print(result.company.stock_code, result.company.stock_name, result.risk_type, result.year,
        #         #               result.is_normal, result.evidence)

        # response = jsonify(status='OK')
        # response.status = '201 CREATED'
        # return response

    @app.route('/index')
    def index():
        return render_template('index.html')
