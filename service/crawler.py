from flask_sqlalchemy import SQLAlchemy

from flask import Flask, Request, jsonify, render_template

from logic import collector


def configure(app):

    @app.route('/crawling/nfinance/companyperformance')
    def nfinance_company_performance(db: SQLAlchemy):

        result = collector.nfinance_company_performance(db)

        response = jsonify(status='OK')
        response.status = '201 CREATED'
        return response

    @app.route('/crawling/krx/investratio')
    def krx_invest_ratio(db: SQLAlchemy):

        result = collector.krx_invest_ratio(db)

        response = jsonify(status='OK')
        response.status = '201 CREATED'
        return response

    @app.route('/crawling/krx/indestrytype')
    def krx_industry_type(db: SQLAlchemy):

        result = collector.krx_industry_type(db)

        response = jsonify(status='OK')
        response.status = '201 CREATED'
        return response

    @app.route('/crawling/dart/financialdata')
    def dart_financial_data(db: SQLAlchemy):

        result = collector.dart_financial_data(db)

        response = jsonify(status='OK')
        response.status = '201 CREATED'
        return response

    @app.route('/test2')
    def test2():

        return render_template('index.html')
