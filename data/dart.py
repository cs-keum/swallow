import requests
import pandas as pd
import numpy as np
import json
import io
from urllib import request
from zipfile import ZipFile
import ssl, os
import xml.etree.ElementTree as ET
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import exists
from sqlalchemy import or_
from orm import model

context = ssl._create_unverified_context()

API_KEY = "a1b7922fe391322aef38d0cdfa2cc7a337dd65e4"

new_companies = []


def company_data(db: SQLAlchemy):
    req_url = 'https://opendart.fss.or.kr/api/corpCode.xml?crtfc_key=' + API_KEY
    params = {
        'crtfc_key': 'a1b7922fe391322aef38d0cdfa2cc7a337dd65e4',
        # 25d08389cf2f30201056ef7d4e5627539b55d784 e97f75b01939a7d21c9226287e9b9a7d46cb4116
    }

    data = request.urlopen(req_url, context=context)
    filename = data.info().get_filename()
    print("파일명 : " + filename)

    with open(filename, 'wb') as f:
        f.write(data.read())
        f.close

    print("다운로드 완료.")

    with ZipFile(filename, 'r') as zipObj:
        zipObj.extractall('./')  # 현재 디렉토리에 압축을 해제

    tree = ET.parse("CORPCODE.xml")
    root = tree.getroot()

    # 기존의 모든 레코드를 가져옵니다.
    existing_companies = db.session.query(model.BaseCompany).all()
    market_company_list = db.session.query(model.MarketCondition).all()

    # 기존 레코드의 corp_code를 메모리에 보관합니다.
    existing_corp_codes = set(company.corp_code for company in existing_companies)
    market_stock_codes = set(market.stock_code for market in market_company_list)

    for item in root.findall('list'):  # 'list' 태그를 찾아서 반복
        # XML에서 필요한 데이터 추출
        corp_code = item.find('corp_code').text
        corp_name = item.find('corp_name').text
        stock_code = item.find('stock_code').text
        modify_date = item.find('modify_date').text

        # stock_code가 None이거나 길이가 0이거나 기존 데이터에 이미 있는 경우 건너뜁니다.
        if not stock_code or stock_code not in market_stock_codes or corp_code in existing_corp_codes:
            continue

        # 새로운 회사 정보를 생성하여 데이터베이스에 추가
        new_companies.append(model.BaseCompany(
            corp_code=corp_code,
            corp_name=corp_name,
            stock_code=stock_code,
            modify_date=modify_date,
        ))

    db.session.bulk_save_objects(new_companies)
    # 변경사항 저장
    db.session.commit()
    # 세션 종료
    db.session.close()

    if os.path.isfile(filename):
        os.remove(filename)  # 원본 압축파일 삭제
    if os.path.isfile(filename):
        os.remove("CORPCODE.xml")  # 원본 압축파일 삭제


def financial_data(corpCode, bsns_year, reprt_code, fs_div):
    req_url = 'https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json'
    params = {
        'crtfc_key': 'a1b7922fe391322aef38d0cdfa2cc7a337dd65e4',
        # 25d08389cf2f30201056ef7d4e5627539b55d784 e97f75b01939a7d21c9226287e9b9a7d46cb4116
        'corp_code': corpCode,
        'bsns_year': str(bsns_year),
        'reprt_code': reprt_code,
        'fs_div': fs_div,
    }

    try:
        response = requests.get(url=req_url, params=params, headers={'User-Agent': 'swallow'})
        content_dic = json.loads(response.content)
        if content_dic['status'] == '013':
            print("No contents", corpCode, bsns_year)
            return None
        else:
            try:
                df = pd.DataFrame.from_records(content_dic['list'])
            except KeyError:
                return None

            df['bsns_year'] = bsns_year
            # df.replace()
            df.fillna(0, inplace=True)
            return df
    except:
        print("No response")
        return None
