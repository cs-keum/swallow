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
    trade_date = datetime.today()
    while True:
        df = krx.stock_market_condition(trade_date.strftime("%Y%m%d"))
        if df.size != 0:
            db.session.query(model.MarketCondition).delete()
            db.session.bulk_insert_mappings(model.MarketCondition, df.to_dict(orient="records"))
            db.session.commit()
            print("Success to get market condition data", trade_date)
            break
        else:
            trade_date = trade_date + timedelta(days=-1)
    return


def krx_invest_reference(db: SQLAlchemy):
    trade_date = datetime.today()
    while True:
        df = krx.invest_reference(trade_date.strftime("%Y%m%d"))
        if df.size != 0:
            db.session.query(model.InvestReference).delete()
            db.session.bulk_insert_mappings(model.InvestReference, df.to_dict(orient="records"))
            db.session.commit()
            print("Success to get invest reference data", trade_date)
            break
        else:
            trade_date = trade_date + timedelta(days=-1)
    return


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


def krx_foreign_holding(db: SQLAlchemy):
    trade_date = datetime.today()
    while True:
        df = krx.foreign_holding(trade_date.strftime("%Y%m%d"))
        if df.size != 0:
            db.session.query(model.ForeignHolding).delete()
            db.session.bulk_insert_mappings(model.ForeignHolding, df.to_dict(orient="records"))
            db.session.commit()
            print("Success to get foreign holding data", trade_date)
            break
        else:
            trade_date = trade_date + timedelta(days=-1)
    return


def dart_financial_data(db: SQLAlchemy, initial):
    result = common.stock_codes(db)

    for item in result:
        if not initial and not db.session.query(
                exists().where(model.FinancialData.corp_code == item.corp_code)).scalar():
            continue

        if request_dart_annual_financial_data(db, item):
            request_dart_quarter_financial_data(db, item, None, None)

    return


def dart_decided_period_financial_data(db: SQLAlchemy, initial, decided_year, decided_reprt_code):
    result = common.stock_codes(db)

    for item in result:

        if not initial and not db.session.query(
                exists().where(model.FinancialData.corp_code == item.corp_code)).scalar():
            continue

        request_dart_quarter_financial_data(db, item, decided_year=decided_year, decided_reprt_code=decided_reprt_code)

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
            # company_item = db.session.query(model.Company).filter(model.Company.stock_code == item.stock_code).one()
            update_latest_report(db, item, year, reprt_code)
            # if item.bsns_year_updated is not None and item.bsns_year_updated < year:
            #     item.bsns_year_updated = year
            # reprt_codes_dic = {'11011': 1, '11014': 2, '11012': 3, '11013': 4}
            # if item.reprt_code_updated is not None and reprt_codes_dic[item.reprt_code_updated] >= reprt_codes_dic[
            #     reprt_code]:
            #     item.reprt_code_updated = reprt_code
            # db.session.commit()

            years_period += 1
            continue

        df = dart.financial_data(item.corp_code, year, reprt_code, 'CFS')
        if df is None:
            df = dart.financial_data(item.corp_code, year, reprt_code, 'OFS')

        if df is not None:
            db.session.bulk_insert_mappings(model.FinancialData, df.to_dict(orient="records"))
            db.session.commit()
            print("Success to get data", item.stock_code, item.stock_name, year)
            update_latest_report(db, item, year, reprt_code)
            exists_annual_data = True

        years_period += 1

    return exists_annual_data


def request_dart_quarter_financial_data(db: SQLAlchemy, item: model.Company, decided_year, decided_reprt_code):
    bsns_year = datetime.today().year

    # 최근 분기보고서
    if datetime.today().month < 4:
        years_period = 1
    else:
        years_period = 0

    data_exists = False
    while years_period <= 5:

        year = bsns_year - years_period

        if decided_year and decided_year != str(year):
            years_period += 1
            continue

        reprt_code_list = ['11014', '11012', '11013']
        for reprt_code in reprt_code_list:

            if decided_reprt_code and decided_reprt_code != reprt_code:
                continue

            exist_data = db.session.query(exists().where(model.FinancialData.corp_code == item.corp_code).where(
                model.FinancialData.bsns_year == year).where(model.FinancialData.reprt_code == reprt_code)).scalar()

            if exist_data:
                update_latest_report(db, item, year, reprt_code)
                data_exists = True
                break

            df = dart.financial_data(item.corp_code, year, reprt_code, 'CFS')
            if df is None:
                df = dart.financial_data(item.corp_code, year, reprt_code, 'OFS')

            if df is not None:
                db.session.bulk_insert_mappings(model.FinancialData, df.to_dict(orient="records"))
                db.session.commit()
                print("Success to get data", item.stock_code, item.stock_name, year, reprt_code)
                update_latest_report(db, item, year, reprt_code)
                data_exists = True
                break

        if data_exists:
            break;

        years_period += 1

    return


def update_latest_report(db, item, year, reprt_code):
    if item.bsns_year_updated is None or item.bsns_year_updated < year:
        item.bsns_year_updated = year
    reprt_codes_dic = {'11011': 1, '11014': 2, '11012': 3, '11013': 4}
    if item.reprt_code_updated is None or reprt_codes_dic[item.reprt_code_updated] >= reprt_codes_dic[
        reprt_code]:
        item.reprt_code_updated = reprt_code
    db.session.commit()
