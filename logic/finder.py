from builtins import print
import json
import pandas as pd

from sqlalchemy import create_engine
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
import operator
from logic import common
from orm import model

# earning_rate = 8.0
table = pd.read_excel('./excel/compound_ten_years.xlsx', index_col=0)


# conn = create_engine("mysql+pymysql://root:" + "root" + "@127.0.0.1:3306/marketdata?charset=utf8",
#                      encoding='utf-8').connect()


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


def annual_op_margin(db: SQLAlchemy, stock_code, performance_updated):
    op_margin_dic = {}

    result = db.session.query(model.CompanyPerformance.settlement_date, model.CompanyPerformance.op_margin,
                              model.CompanyPerformance.is_consensus).filter(
        model.CompanyPerformance.stock_code == stock_code).filter(
        model.CompanyPerformance.creation_date == performance_updated).filter(
        model.CompanyPerformance.period_division == 'annual')

    for item in result:
        if item.op_margin != 0 or item.op_margin == 0 and item.is_consensus:
            op_margin_dic[item.settlement_date] = item.op_margin

    return op_margin_dic, True


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

        # if filter_recommend:
        #     if cur_roe < yield_rate:
        #         return -1

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


def define_value(db, code, stock_company, _roe, roe_dic, yield_rate, capital_value, cash_flows, filter_recommend):
    if capital_value is None:
        return None

    if cash_flows is None or cash_flows < 0:
        return None

    annual_op_margin_dic, is_valid = annual_op_margin(db, stock_company.stock_code, stock_company.performance_updated)
    _aligned_op_margin_dic = aligned_roe_dic(annual_op_margin_dic)
    # trend = roe_trend(_ali/gned_op_margin_dic, filter_recommend, False, 0, yield_rate)

    # if trend < 0:
    #     return None

    op_margin = define_roe(2, _aligned_op_margin_dic, True)

    item = current_stock(db, code)
    try:
        price = item.current_price
        name = item.stock_name
        listedStocks = item.listed_stocks
        trading_volume = item.trading_volume
        total_market_price = item.total_market_price
    except:
        return None

    if filter_recommend and trading_volume < 50000:
        return None

    if filter_recommend and total_market_price < 100000000000:
        return None

    total_market_price_cash_flows_ratio = None
    if cash_flows is not None:
        total_market_price_cash_flows_ratio = round(total_market_price / cash_flows, 2)

    if filter_recommend and total_market_price_cash_flows_ratio > 10:
        return None

    gap_roe = _roe - yield_rate
    excessProfit = (capital_value * gap_roe / 100)

    std_discount_rate = yield_rate / 100

    # excessStockValue
    excessProfitValue = excessProfit * 1 / std_discount_rate
    excessShareholderValue = capital_value + excessProfitValue
    excessStockValue = round(excessShareholderValue / listedStocks, 0)

    # adequateStockValue
    adequateProfitValue = excessProfit * 0.9 / (1 + std_discount_rate - 0.9)
    adequateShareholderValue = capital_value + adequateProfitValue
    adequateStockValue = round(adequateShareholderValue / listedStocks, 0)

    # buyingStockValue
    buyingProfitValue = excessProfit * 0.8 / (1 + std_discount_rate - 0.8)
    buyingShareholderValue = capital_value + buyingProfitValue
    buyingStockValue = round(buyingShareholderValue / listedStocks, 0)

    if excessProfit < 0:
        switchValue = excessStockValue
        excessStockValue = buyingStockValue
        buyingStockValue = switchValue

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

    stock_definition = model.StockDefinition(datetime.today().strftime('%Y-%m-%d'), code, name, capital_value,
                                             listedStocks, trading_volume,
                                             total_market_price, cash_flows, total_market_price_cash_flows_ratio,
                                             foreign_holding_ratio, excessProfit, price_gap_ratio, price,
                                             buyingStockValue, adequateStockValue, excessStockValue, per, pbr,
                                             dividend, dividend_yield, op_margin, _roe, roe_dic)
    return stock_definition


def aligned_roe_dic(roe_dic):
    _aligned_roe = {}

    roe_tuple_list = sorted(roe_dic.items(), key=operator.itemgetter(0), reverse=True)
    for index, roe_tuple in enumerate(roe_tuple_list):
        if index < 3:
            _aligned_roe[index] = roe_tuple[1]

    return _aligned_roe


def recommend_stocks(db: SQLAlchemy, steady_roe, volatility, yield_rate, type):
    stocks = []
    result = common.stock_codes(db)

    for company in result:
        company.reprt_code_updated = '11014'
        stock_definition = recommend_stock(db, company, steady_roe, volatility, yield_rate)
        if stock_definition is None:
            continue

        if type == 0:  # ALL
            stocks.append(stock_definition)

        if type == 1:
            if stock_definition.price < stock_definition.buy_price:
                # print(stock_definition.as_dict())
                stocks.append(stock_definition)

        if type == 2:
            if stock_definition.buy_price <= stock_definition.price < stock_definition.adequate_price:
                stocks.append(stock_definition)

        if type == 3:
            if stock_definition.adequate_price <= stock_definition.price < stock_definition.excess_price:
                stocks.append(stock_definition)

    return stocks


def analyze_stock(db: SQLAlchemy, company, volatility, yield_rate):
    return __stock(db, company, False, False, volatility, yield_rate)


def recommend_stock(db: SQLAlchemy, company, steady_roe, volatility, yield_rate):
    return __stock(db, company, True, steady_roe, volatility, yield_rate)


def __stock(db: SQLAlchemy, company, filter_recommend, steady_roe, volatility, yield_rate):
    # if filter_recommend:
    #     item = db.session.query(model.CompanyPresumed).filter(
    #         model.CompanyPresumed.stock_code == company.stock_code).filter(
    #         model.CompanyPresumed.performance_updated == company.performance_updated).filter(
    #         model.CompanyPresumed.yield_rate == yield_rate).first()
    #
    #     if item is not None:
    #         if item.roe is not None and item.roes is not None:
    #             return define_value(db, company.stock_code, company, item.roe, json.loads(item.roes), yield_rate,
    #                                 item.capital_value, item.cash_flows, filter_recommend)
    #         else:
    #             return

    roe_dic = {}

    annual_roe_dic, is_valid = annual_roe(db, company.stock_code, company.performance_updated)
    if not is_valid:
        # return None
        return handle_invalid_performance(db, company, yield_rate)

    for key in annual_roe_dic.keys():
        _roe = annual_roe_dic.get(key)
        if _roe != 0:
            roe_dic[key] = _roe
        else:
            assumed_roe, is_valid = quarter_roe(key, db, company.stock_code, company.performance_updated,
                                                filter_recommend, steady_roe, volatility, yield_rate)
            if is_valid and assumed_roe != 0:
                roe_dic[key] = assumed_roe
            # else:
            #     return None

    _aligned_roe_dic = aligned_roe_dic(roe_dic)
    if steady_roe and len(_aligned_roe_dic) < 3:
        return handle_invalid_performance(db, company, yield_rate)

    trend = roe_trend(_aligned_roe_dic, filter_recommend, steady_roe, volatility, yield_rate)

    if trend < 0:
        return handle_invalid_performance(db, company, yield_rate)

    defined_roe = define_roe(trend, _aligned_roe_dic, True)
    if filter_recommend and defined_roe < yield_rate:
        return handle_invalid_performance(db, company, yield_rate)

    capital_value = common.equity_owners_value(db, company, company.bsns_year_updated, company.reprt_code_updated)
    cash_flows = common.cash_flows(db, company, company.reprt_code_updated)

    if filter_recommend:
        company_presumed = model.CompanyPresumed(company.stock_code, company.performance_updated, yield_rate,
                                                 defined_roe, json.dumps(_aligned_roe_dic), capital_value, cash_flows)
        db.session.add(company_presumed)
        db.session.commit()

    return define_value(db, company.stock_code, company, defined_roe, _aligned_roe_dic, yield_rate, capital_value,
                        cash_flows, filter_recommend)


def handle_invalid_performance(db, company, yield_rate):
    company_presumed = model.CompanyPresumed(company.stock_code, company.performance_updated, yield_rate, None, None,
                                             None, None)
    db.session.add(company_presumed)
    db.session.commit()
    return None
