from flask_sqlalchemy import SQLAlchemy

from flask import Flask, request, jsonify, render_template

from logic import collector


def configure(app):

    @app.route('/crawling/nfinance/companyperformance')
    def nfinance_company_performance(db: SQLAlchemy):

        result = collector.nfinance_company_performance(db)

        response = jsonify(status='OK')
        response.status = '201 CREATED'
        return response

    @app.route('/crawling/krx/marketcondition')
    def krx_market_condition(db: SQLAlchemy):

        result = collector.krx_market_condition(db)

        response = jsonify(status='OK')
        response.status = '201 CREATED'
        return response

    @app.route('/crawling/krx/investreference')
    def krx_invest_reference(db: SQLAlchemy):

        result = collector.krx_invest_reference(db)

        response = jsonify(status='OK')
        response.status = '201 CREATED'
        return response

    @app.route('/crawling/krx/indestrytype')
    def krx_industry_type(db: SQLAlchemy):

        result = collector.krx_industry_type(db)

        response = jsonify(status='OK')
        response.status = '201 CREATED'
        return response

    @app.route('/crawling/krx/foreignholding')
    def krx_foreign_holding(db: SQLAlchemy):

        result = collector.krx_foreign_holding(db)

        response = jsonify(status='OK')
        response.status = '201 CREATED'
        return response

    @app.route('/crawling/dart/financialdata')
    def dart_financial_data(db: SQLAlchemy):

        initial = request.args.get('initial')
        if initial is None:
            initial = False
        else:
            initial = True

        decided_year = request.args.get('decided_year')
        decided_reprt_code = request.args.get('decided_reprt_code')
        if decided_year is not None and decided_reprt_code is not None:
            result = collector.dart_decided_period_financial_data(db, initial, decided_year, decided_reprt_code)
        else:
            result = collector.dart_financial_data(db, initial)

        response = jsonify(status='OK')
        response.status = '201 CREATED'
        return response

    @app.route('/test2')
    def test2():

        return render_template('index.html')
