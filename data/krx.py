from datetime import datetime
import time
import requests
import pandas as pd
import numpy as np
from io import BytesIO


def stock_market_condition(trade_date):
    req_url = 'http://marketdata.krx.co.kr/contents/COM/GenerateOTP.jspx'
    params = {
        'name': 'fileDown',
        'filetype': 'xls',
        'url': 'MKD/13/1302/13020101/mkd13020101',
        'market_gubun': 'ALL',
        'sect_tp_cd': 'ALL',
        'schdate': str(trade_date),
        'pagePath': '/contents/MKD/13/1302/13020101/MKD13020101.jsp'
    }
    r1 = requests.get(url=req_url, params=params, headers={'User-Agent': 'swallow'})

    doTry = 0
    while len(r1.content) <= 0:
        r1 = requests.get(url=req_url, params=params, headers={'User-Agent': 'swallow'})
        doTry += 1
        if doTry == 10:
            break

    req_url = 'http://file.krx.co.kr/download.jspx'
    headers = {
        'Referer': 'http://marketdata.krx.co.kr/mdi',
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

    df.columns = ["stock_code", "stock_name", "current_price", "compare", "fluctuation_rate", "market_price", "high_price",
                  "low_price", "trading_volume", "transaction_amount", "total_market_price", "total_market_price_ratio",
                  "listed_stocks"]

    print("Success to get market condition data", trade_date)
    return df


# def invest_ratio(trade_date):
#     time.sleep(2.0)
#
#     req_url = 'http://marketdata.krx.co.kr/contents/COM/GenerateOTP.jspx'
#     params = {
#         'name': 'fileDown',
#         'filetype': 'xls',
#         'url': 'MKD/13/1302/13020401/mkd13020401',
#         'market_gubun': 'ALL',
#         'gubun': '1',
#         'isu_cdnm': 'A005930/삼성전자',
#         'isu_cd': 'KR7005930003',
#         'isu_nm': '삼성전자',
#         'isu_srt_cd': 'A005930',
#         'schdate': str(trade_date),
#         'fromdate': '20200103',
#         'todate': '20200110',
#         'pagePath': '/contents/MKD/13/1302/13020401/MKD13020401.jsp'
#     }
#     r1 = requests.get(url=req_url, params=params, headers={'User-Agent': 'swallow'})
#
#     doTry = 0
#     while len(r1.content) <= 0:
#         time.sleep(2.0)
#         r1 = requests.get(url=req_url, params=params, headers={'User-Agent': 'swallow'})
#         doTry += 1
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
#         print("Fail to get invest reference data", trade_date)
#         return
#
#     df = pd.read_excel(BytesIO(r.content), thousands=',')
#
#     df.columns = ["tdate", "stock_code", "stock_name", "managed", "price", "eps", "per", "bps", "pbr", "dividend",
#                   "dividend_yield"]
#
#     df['tdate'] = df['tdate'].str.replace('/', '')
#     df['eps'] = df['eps'].apply(lambda x: '0' if x == "-" else x)
#     df['per'] = df['per'].apply(lambda x: '0' if x == "-" else x)
#     df['bps'] = df['bps'].apply(lambda x: '0' if x == "-" else x)
#     df['pbr'] = df['pbr'].apply(lambda x: '0' if x == "-" else x)
#
#     df['roe'] = round(pd.to_numeric(df['eps']) / pd.to_numeric(df['bps']) * 100, 3)
#
#     df['roe'] = df['roe'].apply(lambda x: '0' if x == np.inf or np.isnan(x) else x)
#     df['dividend'] = df['dividend'].apply(lambda x: '0' if x == np.inf or np.isnan(x) else x)
#     df['dividend_yield'] = df['dividend_yield'].apply(lambda x: '0' if x == np.inf or np.isnan(x) else x)
#     df.fillna(0)
#
#     print("Success to get invest reference data", trade_date)
#     return df


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
