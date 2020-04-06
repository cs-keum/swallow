import pandas as pd
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import exists
import time
from orm import model

from data import dart
from data import krx
from data import nfinance

from logic import common


def nfinance_company_performance(db: SQLAlchemy):
    result = common.stock_codes(db)
    for item in result:
        exist_data = db.session.query(exists().where(model.CompanyPerformance.stock_code == item.stock_code).where(
            model.CompanyPerformance.creation_date == datetime.today().date())).scalar()
        if not exist_data:
            time.sleep(1.0)
            df = nfinance.company_performance(item.stock_code)
            if df.size <= 0:
                company_performance_item = model.CompanyPerformance(stock_code=item.stock_code,
                                                                    period_division='invalid',
                                                                    creation_date=datetime.today().date())
                db.session.add(company_performance_item)
                db.session.commit()
            else:
                db.session.bulk_insert_mappings(model.CompanyPerformance, df.to_dict(orient="records"))
                db.session.commit()
                print("success to get [" + item.stock_code + "] company performance data")
        else:
            print("exist [" + item.stock_code + "] company performance data")

        company_item = db.session.query(model.Company).filter(model.Company.stock_code == item.stock_code).one()
        company_item.performance_updated = datetime.today().date()
        db.session.commit()
    return


def krx_market_condition(db: SQLAlchemy):

    trade_date = datetime.today().strftime("%Y%m%d")

    df = krx.stock_market_condition(trade_date)

    db.session.query(model.MarketCondition).delete()
    db.session.bulk_insert_mappings(model.MarketCondition, df.to_dict(orient="records"))
    db.session.commit()

    return


# def krx_invest_ratio(db: SQLAlchemy):
#     latest_trade_date = db.session.query(model.InvestRatio).order_by(model.InvestRatio.id.desc()).first().tdate
#
#     from_datetime = datetime(2015, 1, 1)
#     if latest_trade_date is not None:
#         from_datetime = latest_trade_date + timedelta(days=1)
#     to_datetime = datetime.today() + timedelta(days=-1)
#
#     date_range = pd.date_range(from_datetime, to_datetime)
#     for single_date in date_range:
#         trade_date = single_date.strftime("%Y%m%d")
#
#         df = krx.invest_ratio(trade_date)
#
#         db.session.bulk_insert_mappings(model.InvestRatio, df.to_dict(orient="records"))
#         db.session.commit()
#
#     return


def krx_industry_type(db: SQLAlchemy):
    df = krx.industry_type()

    for index, row in df.iterrows():
        stock_code = row['code']
        sector = row['sector']
        try:
            company_item = db.session.query(model.Company).filter(model.Company.stock_code == stock_code).one()
            company_item.sector = sector
            db.session.commit()
        except:
            pass

    return


def dart_financial_data(db: SQLAlchemy, initial):
    result = common.stock_codes(db)

    for item in result:

        if not initial and not db.session.query(
                exists().where(model.FinancialData.corp_code == item.corp_code)).scalar():
            continue

        request_dart_annual_financial_data(db, item)

    return


def request_dart_annual_financial_data(db: SQLAlchemy, item: model.Company):
    bsns_year = datetime.today().year - 1

    # 사업보고서
    years_period = 0

    exists_annual_data = False
    while years_period <= 2:
        year = bsns_year - years_period

        reprt_code = '11011'
        exist_data = db.session.query(exists().where(model.FinancialData.corp_code == item.corp_code).where(
            model.FinancialData.bsns_year == year).where(model.FinancialData.reprt_code == reprt_code)).scalar()

        if exist_data:
            years_period += 1
            continue

        df = dart.financial_data(item.corp_code, year, reprt_code, 'CFS')
        if df is None:
            df = dart.financial_data(item.corp_code, year, reprt_code, 'OFS')

        if df is not None:
            db.session.bulk_insert_mappings(model.FinancialData, df.to_dict(orient="records"))
            db.session.commit()
            print("Success to get data", item.stock_code, item.stock_name, year)
            exists_annual_data = True

        years_period += 1

    return exists_annual_data


def request_dart_quarter_financial_data(db: SQLAlchemy, item: model.Company):
    bsns_year = datetime.today().year

    # 최근 분기보고서
    if datetime.today().month < 4:
        years_period = 1
    else:
        years_period = 0

    data_exists = False
    while years_period <= 5:
        year = bsns_year - years_period

        reprt_code_list = ['11014', '11012', '11013']
        for reprt_code in reprt_code_list:
            exist_data = db.session.query(exists().where(model.FinancialData.corp_code == item.corp_code).where(
                model.FinancialData.bsns_year == year).where(model.FinancialData.reprt_code == reprt_code)).scalar()

            if exist_data:
                data_exists = True
                break

            df = dart.financial_data(item.corp_code, year, reprt_code, 'CFS')
            if df is None:
                df = dart.financial_data(item.corp_code, year, reprt_code, 'OFS')

            if df is not None:
                db.session.bulk_insert_mappings(model.FinancialData, df.to_dict(orient="records"))
                db.session.commit()
                print("Success to get data", item.stock_code, item.stock_name, year, reprt_code)
                data_exists = True
                break

        if data_exists:
            break;

        years_period += 1

    return
