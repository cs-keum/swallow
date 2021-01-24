from datetime import datetime
import time
import requests
import pandas as pd
import numpy as np
from io import BytesIO


def stock_market_condition(trade_date):
    req_url = 'http://data.krx.co.kr/comm/fileDn/GenerateOTP/generate.cmd'
    params = {
        'name': 'fileDown',
        'filetype': 'xls',
        'url': 'dbms/MDC/STAT/standard/MDCSTAT01501',
        'market_gubun': 'ALL',
        'sect_tp_cd': 'ALL',
        'trdDd': str(trade_date),
        # 'trdDd': str(20210122),
        'mktId': 'ALL',
        'share': 1,
        'money': 1,
        'csvxls_isNo': 'false',
        'pagePath': '/contents/MKD/13/1302/13020101/MKD13020101.jsp'
    }
    headers = {
        'Referer': 'http://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201',
        'User-Agent': 'swallow'
    }
    r1 = requests.get(url=req_url, params=params, headers=headers)

    doTry = 0
    while len(r1.content) <= 0:
        r1 = requests.get(url=req_url, params=params, headers={'User-Agent': 'swallow'})
        doTry += 1
        if doTry == 10:
            break

    req_url = 'http://data.krx.co.kr/comm/fileDn/download_excel/download.cmd'
    headers = {
        'Referer': 'http://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201',
        'User-Agent': 'swallow'
    }
    data = {
        'code': r1.content
    }

    r = requests.post(url=req_url, data=data, headers=headers)
    doTry = 0
    while len(r.content) <= 0:
        time.sleep(2.0)
        r = requests.post(url=req_url, data=data, headers=headers)
        doTry = + 1
        if doTry == 10:
            break

    if len(r.content) <= 0:
        print("Fail to get invest reference data", trade_date)
        return

    df = pd.read_excel(BytesIO(r.content), thousands=',')

    if df.iloc[0, 4] == "-":
        return None;

    df.columns = ["stock_code", "stock_name", "gubun", "sosok", "current_price", "compare", "fluctuation_rate",
                  "market_price",
                  "high_price", "low_price", "trading_volume", "transaction_amount", "total_market_price",
                  "listed_stocks"]
    return df


def invest_reference(trade_date):
    req_url = 'http://data.krx.co.kr/comm/fileDn/GenerateOTP/generate.cmd'
    params = {
        'searchType': 1,
        'mktId': 'ALL',
        'trdDd': str(trade_date),
        # 'trdDd': str(20210122),
        'tboxisuCd_finder_stkisu0_0': '005930 / 삼성전자',
        'isuCd': 'KR7005930003',
        'isuCd2': 'KR7005930003',
        'codeNmisuCd_finder_stkisu0_0': '삼성전자',
        'param1isuCd_finder_stkisu0_0': 'STK',
        'strtDd': '20200103',
        'endDd': '20200110',
        'name': 'fileDown',
        'filetype': 'xls',
        'url': 'dbms/MDC/STAT/standard/MDCSTAT03501',
        'gubun': '1'
    }
    headers = {
        'Referer': 'http://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201020502',
        'User-Agent': 'swallow'
    }
    r1 = requests.get(url=req_url, params=params, headers=headers)

    doTry = 0
    while len(r1.content) <= 0:
        time.sleep(2.0)
        r1 = requests.get(url=req_url, params=params, headers=headers)
        doTry += 1
        if doTry == 10:
            break

    req_url = 'http://data.krx.co.kr/comm/fileDn/download_excel/download.cmd'
    headers = {
        'Referer': 'http://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201020502',
        'User-Agent': 'swallow'
    }
    data = {
        'code': r1.content
    }

    r = requests.post(url=req_url, data=data, headers=headers)
    doTry = 0
    while len(r.content) <= 0:
        time.sleep(2.0)
        r = requests.post(url=req_url, data=data, headers=headers)
        doTry = + 1
        if doTry == 10:
            break

    if len(r.content) <= 0:
        print("Fail to get invest reference data", trade_date)
        return

    df = pd.read_excel(BytesIO(r.content), thousands=',')

    df.columns = ["stock_code", "stock_name", "price", "compare", "fluctuation_rate", "eps", "per", "bps", "pbr",
                  "dividend",
                  "dividend_yield"]

    if df.iloc[0, 2] == "-":
        return None;
    # df.insert(column='stock_code', value=str(trade_date))
    # df['tdate'] = df['tdate'].str.replace('/', '')
    df['eps'] = df['eps'].apply(lambda x: '0' if x == "-" else x)
    df['per'] = df['per'].apply(lambda x: '0' if x == "-" else x)
    df['bps'] = df['bps'].apply(lambda x: '0' if x == "-" else x)
    df['pbr'] = df['pbr'].apply(lambda x: '0' if x == "-" else x)

    df['dividend'] = df['dividend'].apply(lambda x: '0' if x == np.inf else x)
    df['dividend_yield'] = df['dividend_yield'].apply(lambda x: '0' if x == np.inf else x)
    df.fillna(0)
    return df


def industry_type():
    req_url = 'http://marketdata.krx.co.kr/contents/COM/GenerateOTP.jspx'
    params = {
        'name': 'fileDown',
        'filetype': 'xls',
        'url': 'MKD/04/0406/04060100/mkd04060100_01',
        'market_gubun': 'ALL',
        'pagePath': '/contents/MKD/04/0406/04060100/MKD04060100.jsp'
    }
    r1 = requests.get(url=req_url, params=params, headers={'User-Agent': 'test'})

    print("기본 데이터 가져오기 중 ...")

    doTry = 0
    while len(r1.content) <= 0:
        time.sleep(2.0)
        r1 = requests.get(url=req_url, params=params, headers={'User-Agent': 'test'})
        doTry += 1
        print("기본 데이터 가져오기 중 ...", doTry)
        if doTry == 10:
            break

    req_url = 'http://file.krx.co.kr/download.jspx'
    headers = {
        'Referer': 'http://marketdata.krx.co.kr/mdi',
        'User-Agent': 'test'
    }
    data = {
        'code': r1.content
    }

    r = requests.post(url=req_url, data=data, headers=headers)
    doTry = 0
    while len(r.content) <= 0:
        time.sleep(2.0)
        r = requests.post(url=req_url, data=data, headers=headers)
        doTry = + 1
        if doTry == 10:
            break

    if len(r.content) <= 0:
        return

    df = pd.read_excel(BytesIO(r.content), thousands=',')

    df.columns = ["id", "code", "name", "sector_code", "sector", "listed_stocks", "capital", "face_value", "currency",
                  "phone_number", "address"]

    return df


def foreign_holding(trade_date):
    req_url = 'http://data.krx.co.kr/comm/fileDn/GenerateOTP/generate.cmd'
    params = {
        'searchType': 1,
        'mktId': 'ALL',
        'trdDd': str(trade_date),
        # 'trdDd': str(20210122),
        'tboxisuCd_finder_stkisu0_1': '005930/삼성전자',
        'isuCd': 'KR7005930003',
        'isuCd2': 'KR7005930003',
        'codeNmisuCd_finder_stkisu0_1': '삼성전자',
        'param1isuCd_finder_stkisu0_1': 'STK',
        'strtDd': '20210115',
        'endDd': '20210122',
        'share': 1,
        'csvxls_isNo': 'false',
        'name': 'fileDown',
        'url': 'dbms/MDC/STAT/standard/MDCSTAT03701'
    }
    headers = {
        'Referer': 'http://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201020502',
        'User-Agent': 'swallow'
    }
    r1 = requests.get(url=req_url, params=params, headers=headers)

    # print("기본 데이터 가져오기 중 ...")

    doTry = 0
    while len(r1.content) <= 0:
        time.sleep(2.0)
        r1 = requests.get(url=req_url, params=params, headers=headers)
        doTry += 1
        # print("기본 데이터 가져오기 중 ...", doTry)
        if doTry == 10:
            break

    req_url = 'http://data.krx.co.kr/comm/fileDn/download_excel/download.cmd'
    headers = {
        'Referer': 'http://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201020502',
        'User-Agent': 'swallow'
    }
    data = {
        'code': r1.content
    }

    r = requests.post(url=req_url, data=data, headers=headers)
    doTry = 0
    while len(r.content) <= 0:
        time.sleep(2.0)
        r = requests.post(url=req_url, data=data, headers=headers)
        doTry = + 1
        if doTry == 10:
            break

    if len(r.content) <= 0:
        return

    df = pd.read_excel(BytesIO(r.content), thousands=',')

    df.columns = ["stock_code", "stock_name", "price", "compare", "fluctuation_rate", "listed_stocks",
                  "foreign_holding", "foreign_holding_ratio", "foreign_holding_limit", "foreign_holding_limit_exhaust"]

    if df.iloc[0, 2] == "-":
        return None;

    return df

# def stock(date):
#     req_url = 'http://marketdata.krx.co.kr/contents/COM/GenerateOTP.jspx'
#     params = {
#         'name': 'fileDown',
#         'filetype': 'xls',
#         'url': 'MKD/04/0406/04060200/mkd04060200',
#         'market_gubun': 'ALL',
#         'sect_tp_cd': 'ALL',
#         'isu_cdnm': '전체',
#         'secugrp': 'ST',
#         'stock_gubun': 'on',
#         'schdate': str(date),
#         'pagePath': '/contents/MKD/04/0406/04060200/MKD04060200.jsp'
#     }
#     r1 = requests.get(url=req_url, params=params, headers={'User-Agent': 'swallow'})
#
#     print("기본 데이터 가져오기 중 ...", date)
#
#     doTry = 0
#     while len(r1.content) <= 0:
#         time.sleep(2.0)
#         r1 = requests.get(url=req_url, params=params, headers={'User-Agent': 'swallow'})
#         doTry += 1
#         print("기본 데이터 가져오기 중 ...", date, doTry)
#         if doTry == 10:
#             break
#
#     req_url = 'http://file.krx.co.kr/download.jspx'
#     headers = {
#         'Referer': 'http://marketdata.krx.co.kr/mdi',
#         'User-Agent': 'swallow'
#     }
#     data = {
#         'code': r1.content
#     }
#
#     r = requests.post(url=req_url, data=data, headers=headers)
#     doTry = 0
#     while len(r.content) <= 0:
#         time.sleep(2.0)
#         r = requests.post(url=req_url, data=data, headers=headers)
#         doTry = + 1
#         if doTry == 10:
#             break
#
#     if len(r.content) <= 0:
#         print("기본 데이터 가져오기 실패", date)
#         return
#
#     print("기본 데이터 가져오기 중 2", date)
#
#     df = pd.read_excel(BytesIO(r.content), thousands=',')
#
#     df.columns = ["code", "name", "price", "compare", "fluctuation_rate", "sell", "buy", "trading_volume",
#                   "transaction_amount", "market_price", "high_price", "low_price", "face_value", "currency",
#                   "listed_stocks", "listed_market_cap"]
#     df['tdatetime'] = datetime.today()
#
#     executor = db.Executor()
#     executor.insert(df, "stock_info")
#     # engine = create_engine("mysql+pymysql://root:" + "root" + "@127.0.0.1:3306/marketdata?charset=utf8",
#     #                        encoding='utf-8')
#     #
#     # conn = engine.connect()
#     # df.to_sql(name='stock_info', con=engine, if_exists='append', index=False)
#     # conn.close()
#
#     print("기본 데이터 가져오기 성공", date)
