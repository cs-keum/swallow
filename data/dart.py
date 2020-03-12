import requests
import pandas as pd
import numpy as np
import json


def financial_data(corpCode, bsns_year, reprt_code, fs_div):
    req_url = 'https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json'
    params = {
        'crtfc_key': '25d08389cf2f30201056ef7d4e5627539b55d784', #25d08389cf2f30201056ef7d4e5627539b55d784 e97f75b01939a7d21c9226287e9b9a7d46cb4116
        'corp_code': corpCode,
        'bsns_year': str(bsns_year),
        'reprt_code': reprt_code,
        'fs_div': fs_div,
    }
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
