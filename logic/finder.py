from builtins import print

import pandas as pd

from sqlalchemy import create_engine
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
import operator
from logic import common
from orm import model

# earning_rate = 8.0
table = pd.read_excel('./excel/compound_ten_years.xlsx', index_col=0)
conn = create_engine("mysql+pymysql://root:" + "root" + "@127.0.0.1:3306/marketdata?charset=utf8",
                     encoding='utf-8').connect()


def current_stock(db, code):
    item = db.session.query(model.MarketCondition).filter(
        model.MarketCondition.stock_code == code).order_by(
        model.MarketCondition.id.desc()).first()
    return item


def foreign_holding_item(db, code):
    item = db.session.query(model.ForeignHolding).filter(model.ForeignHolding.stock_code == code).first()
    return item


def invest_reference_item(db, code):
    item = db.session.query(model.InvestReference).filter(model.InvestReference.stock_code == code).first()
    return item


def find_compound_power(roe):
    a = int(roe)
    b = round((roe - a) / 100, 4)
    return round(table.iloc[a - 1][b], 2)


def find_profit_rate(compound_power):
    roe_candidate = 0.0
    for i in range(1, 51):
        for j in range(0, 10):
            roe = i + j / 10
            candidate = find_compound_power(roe)
            if candidate <= compound_power:
                roe_candidate = roe
            else:
                return roe_candidate


def quarter_roe(standard_year, db: SQLAlchemy, stock_code, performance_updated, filter_recommend, steady_roe,
                volatility, yield_rate):
    assumedRoe = 0
    quarter_roe_dic = {}

    result = db.session.query(model.CompanyPerformance.settlement_date, model.CompanyPerformance.roe,
                              model.CompanyPerformance.is_consensus).filter(
        model.CompanyPerformance.stock_code == stock_code).filter(
        model.CompanyPerformance.creation_date == performance_updated).filter(
        model.CompanyPerformance.period_division == 'quarter')

    for item in result:
        # if item.roe == 0 and not item.is_consensus:
        #     return assumedRoe, False

        if item.settlement_date.year >= standard_year.year:
            if item.roe != 0:
                quarter_roe_dic[item.settlement_date] = item.roe

    _aligned_roe_dic = aligned_roe_dic(quarter_roe_dic)
    trend = roe_trend(_aligned_roe_dic, filter_recommend, steady_roe, volatility, yield_rate)
    if trend < 0:
        return assumedRoe, False

    assumedRoe = define_roe(trend, _aligned_roe_dic, True)
    return assumedRoe, True


def annual_roe(db: SQLAlchemy, stock_code, performance_updated):
    roe_dic = {}

    result = db.session.query(model.CompanyPerformance.settlement_date, model.CompanyPerformance.roe,
                              model.CompanyPerformance.is_consensus).filter(
        model.CompanyPerformance.stock_code == stock_code).filter(
        model.CompanyPerformance.creation_date == performance_updated).filter(
        model.CompanyPerformance.period_division == 'annual')

    for item in result:
        if item.roe != 0 or item.roe == 0 and item.is_consensus:
            roe_dic[item.settlement_date] = item.roe

    return roe_dic, True


def roe_trend(roe_dic, filter_recommend, steady_roe, volatility, yield_rate):
    before_roe = -1
    trend = -1

    if len(roe_dic) <= 0:
        return -1

    if len(roe_dic) == 1:
        return 0

    for key in roe_dic.keys():
        cur_roe = roe_dic.get(key)

        if cur_roe is None:
            return -1

        if filter_recommend:
            if cur_roe < yield_rate:
                return -1

        # if before_roe > 0:
        if steady_roe:
            up_volatility = 1 + (volatility / 100)
            down_volatility = 1 - (volatility / 100)
            if before_roe > cur_roe * up_volatility or before_roe < cur_roe * down_volatility:
                return -1

        if cur_roe < before_roe:
            if trend < 0:
                trend = 0
            elif trend == 0:
                trend = 0
            elif trend == 1:
                trend = 2
            elif trend == 2:
                trend = 2

        elif cur_roe > before_roe:
            if trend < 0:
                trend = 1
            elif trend == 0:
                trend = 2
            elif trend == 1:
                trend = 1
            elif trend == 2:
                trend = 2

        before_roe = cur_roe

    return trend


def define_roe(trend, roe_dic, follow_trend):
    # trend = 0 : increase trend
    # trend = 1 : decrease trend
    if follow_trend:
        if trend == 0 or trend == 1:
            return roe_dic.get(0)

    # trend = 2 : mixed trend
    roe_sum = 0
    divide_var = 0
    for key in roe_dic.keys():
        weight_roe = roe_dic.get(key) * (len(roe_dic) - key)
        roe_sum += weight_roe
        divide_var += (len(roe_dic) - key)
    if divide_var == 0:
        return -1
    return round(roe_sum / divide_var, 3)


# def xbrl_capital_value(code):
#     sql = "SELECT equityattributabletoownersofparent FROM xbrl WHERE xbrl.stock_code='" + code + "' AND xbrl.equityattributabletoownersofparent IS NOT NULL ORDER BY xbrl.rcept_dt DESC LIMIT 1;"
#     df = pd.read_sql_query(sql, conn)
#
#     if df.size == 0:
#         return -1
#
#     value = int(df.iloc[0][0].replace(',', ''))
#
#     return value


# def listed_stocks(code):
#     sql = "SELECT listed_stocks FROM stock_info WHERE stock_info.code = '" + code + "' ORDER BY id DESC LIMIT 1;"
#     df = pd.read_sql_query(sql, conn)
#     value = int(df.iloc[0][0])
#
#     return value


def define_value(db, code, stock_company, _roe, roe_dic, yield_rate):
    item = current_stock(db, code)
    try:
        price = item.current_price
        name = item.stock_name
        listedStocks = item.listed_stocks
        trading_volume = item.trading_volume
        total_market_price = item.total_market_price
    except:
        return None

    # capitalValue = xbrl_capital_value(code)

    bsns_year = datetime.today().year
    company_item = common.company(db, code)
    reprt_codes = ['11011', '11014', '11012', '11013']

    capitalValue = None
    while bsns_year >= datetime.today().year - 1:

        for reprt_code in reprt_codes:
            capitalValue = common.equity_owners_value(db, company_item, bsns_year, reprt_code)
            if capitalValue is not None:
                break

        if capitalValue is not None:
            break

        bsns_year -= 1

    if capitalValue is None:
        return None

    gap_roe = _roe - yield_rate
    excessProfit = (capitalValue * gap_roe / 100)

    std_discount_rate = yield_rate / 100

    # excessStockValue
    excessProfitValue = excessProfit * 1 / std_discount_rate
    excessShareholderValue = capitalValue + excessProfitValue
    excessStockValue = round(excessShareholderValue / listedStocks, 0)

    # adequateStockValue
    adequateProfitValue = excessProfit * 0.9 / (1 + std_discount_rate - 0.9)
    adequateShareholderValue = capitalValue + adequateProfitValue
    adequateStockValue = round(adequateShareholderValue / listedStocks, 0)

    # buyingStockValue
    buyingProfitValue = excessProfit * 0.8 / (1 + std_discount_rate - 0.8)
    buyingShareholderValue = capitalValue + buyingProfitValue
    buyingStockValue = round(buyingShareholderValue / listedStocks, 0)

    if excessProfit < 0:
        switchValue = excessStockValue
        excessStockValue = buyingStockValue
        buyingStockValue = switchValue

    # ref_value = 0
    # ref_profit_rate = 0
    # try:
    #     future_price = bps * find_compound_power(_roe)
    #     profit = future_price / price
    #     ref_value = find_profit_rate(profit)
    #     ref_profit_rate = round(future_price / find_compound_power(earning_rate), 0)
    # except:
    #     pass
    price_gap_ratio = round(price / buyingStockValue, 2)
    foreign_holding_ratio = foreign_holding_item(db, code).foreign_holding_ratio
    ir = invest_reference_item(db, code)
    per = 0
    pbr = 0
    dividend = 0
    dividend_yield = 0
    if ir is not None:
        per = ir.per
        pbr = ir.pbr
        dividend = ir.dividend
        dividend_yield = ir.dividend_yield

    stock_definition = model.StockDefinition(datetime.today().strftime('%Y-%m-%d'), code, name, stock_company.sector,
                                             stock_company.induty_code, capitalValue, listedStocks, trading_volume,
                                             total_market_price, foreign_holding_ratio, excessProfit, price_gap_ratio,
                                             price, buyingStockValue, adequateStockValue, excessStockValue, per, pbr,
                                             dividend, dividend_yield, _roe, roe_dic)
    return stock_definition


def aligned_roe_dic(roe_dic):
    _aligned_roe = {}

    roe_tuple_list = sorted(roe_dic.items(), key=operator.itemgetter(0), reverse=True)
    for index, roe_tuple in enumerate(roe_tuple_list):
        _aligned_roe[index] = roe_tuple[1]

    return _aligned_roe


def recommend_stocks(db: SQLAlchemy, steady_roe, volatility, yield_rate):
    stocks = []
    result = common.stock_codes(db)

    for item in result:
        stock_definition = recommend_stock(db, item.stock_code, steady_roe, volatility, yield_rate)
        if stock_definition is None:
            continue

        if stock_definition.price < stock_definition.buy_price:
            # print(stock_definition.as_dict())
            stocks.append(stock_definition)

    return stocks


def analyze_stock(db: SQLAlchemy, stock_code, volatility, yield_rate):
    return __stock(db, stock_code, False, False, volatility, yield_rate)


def recommend_stock(db: SQLAlchemy, stock_code, steady_roe, volatility, yield_rate):
    return __stock(db, stock_code, True, steady_roe, volatility, yield_rate)


def __stock(db: SQLAlchemy, stock_code, filter_recommend, steady_roe, volatility, yield_rate):
    roe_dic = {}

    stock_company = db.session.query(model.Company).filter(model.Company.stock_code == stock_code).one()

    annual_roe_dic, is_valid = annual_roe(db, stock_code, stock_company.performance_updated)
    if not is_valid:
        return None

    for key in annual_roe_dic.keys():
        _roe = annual_roe_dic.get(key)
        if _roe != 0:
            roe_dic[key] = _roe
        else:
            assumed_roe, is_valid = quarter_roe(key, db, stock_code, stock_company.performance_updated,
                                                filter_recommend, steady_roe, volatility, yield_rate)
            if is_valid and assumed_roe != 0:
                roe_dic[key] = assumed_roe
            # else:
            #     return None

    _aligned_roe_dic = aligned_roe_dic(roe_dic)
    if steady_roe and len(_aligned_roe_dic) < 3:
        return None

    trend = roe_trend(_aligned_roe_dic, filter_recommend, steady_roe, volatility, yield_rate)

    if trend < 0:
        return None

    defined_roe = define_roe(trend, _aligned_roe_dic, True)
    if filter_recommend and defined_roe < yield_rate:
        return None
    return define_value(db, stock_code, stock_company, defined_roe, _aligned_roe_dic, yield_rate)
