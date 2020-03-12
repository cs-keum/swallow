import datetime
import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd


def convert(finance_df, period_division, stock_code):

    if '' in finance_df:
        finance_df.drop([''], axis=1, inplace=True)

    _df = pd.DataFrame()

    dates = list(finance_df)

    is_consensus_array = []
    datetime_array = []
    for date in dates:
        if "(E)" in date:
            is_consensus_array.append(True)
            date = date.replace("(E)", "")
        else:
            is_consensus_array.append(False)
        datetime_array.append(datetime.datetime.strptime(date, "%Y.%m").date().strftime("%Y%m%d"))

    _df["settlement_date"] = datetime_array
    for _index, _row in finance_df.iterrows():
        _df[_index] = _row.tolist()
    _df.insert(loc=0, column='stock_code', value=stock_code)
    _df.insert(loc=1, column='period_division', value=period_division)
    _df.insert(loc=2, column='is_consensus', value=is_consensus_array)
    _df.insert(loc=3, column='creation_date', value=datetime.datetime.today().strftime("%Y%m%d"))

    _df.columns = ["stock_code", "period_division", "is_consensus", "creation_date", "settlement_date", "revenue", "operating_profit", "net_income", "op_margin", "net_margin", "roe",
                   "debt_ratio", "quick_ratio", "reserve_ration", "eps", "per", "bps", "pbr", "dividend_per_share",
                   "dividend_yield_ratio", "dividend_payout_ratio"]
    return _df


def company_performance(stock_code):
    URL = "https://finance.naver.com/item/main.nhn?code=" + str(stock_code)

    data = requests.get(URL)
    html = data.text

    soup = BeautifulSoup(html, 'html.parser')
    all_df = pd.DataFrame()
    section = soup.select('div.section.cop_analysis div.sub_section')
    if len(section) <= 0:
        return all_df

    finance_html = section[0]

    th_data = [item.get_text().strip() for item in finance_html.select('thead th')]
    annual_date = th_data[3:7]
    quarter_date = th_data[7:13]

    if len(annual_date) <= 0 or len(quarter_date) <= 0:
        return all_df

    finance_index = [item.get_text().strip() for item in finance_html.select('th.h_th2')][3:]
    finance_data = [item.get_text().strip().replace(',', '') for item in finance_html.select('td')]

    finance_data = np.array(finance_data)
    finance_data.resize(len(finance_index), 10)

    finance_date = annual_date + quarter_date

    re_finance_index = []
    for index in finance_index:
        re_finance_index.append(index.replace("(%)", ""))

    df = pd.DataFrame(data=finance_data[0:, 0:], index=re_finance_index, columns=finance_date)

    annual_finance = df.iloc[:, :4]
    quarter_finance = df.iloc[:, 4:]

    annual_df = convert(annual_finance, 'annual', stock_code)
    quarter_df = convert(quarter_finance, 'quarter', stock_code)

    all_df = annual_df.append(quarter_df)
    all_df = all_df.replace(r'^\s*$', 0, regex=True)
    all_df = all_df.replace(r'^-$', 0, regex=True)
    return all_df
