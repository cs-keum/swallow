from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import exists
from orm import model
from sqlalchemy import orm
from sqlalchemy import or_

from enum import Enum

from logic import common


class Risk(Enum):
    REVENUE = 1
    BUSINESS_LOSS = 2
    OPERATING_LOSS = 3
    CAPITAL_IMPAIRMENT = 4


class Inspection(object):

    def __init__(self, company=None, risk_results=[]):
        self._company = company
        self._risk_results = risk_results

    @property
    def company(self):
        return self._company

    @property
    def risk_results(self):
        return self._risk_results


class RiskResult(object):

    def __init__(self, risk_type=None):
        self._risk_type = risk_type
        self._data_supported = True
        self._year = None
        self._is_normal = None
        self._evidence = []

    @property
    def risk_type(self):
        return self._risk_type

    @property
    def data_supported(self):
        return self._data_supported

    @data_supported.setter
    def data_supported(self, data_supported):
        self._data_supported = data_supported

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, year):
        self._year = year

    @property
    def is_normal(self):
        return self._is_normal

    @is_normal.setter
    def is_normal(self, is_normal):
        self._is_normal = is_normal

    @property
    def evidence(self):
        return self._evidence


def analyze_risk(db: SQLAlchemy, stock_code):
    risk_results = []
    company_item = db.session.query(model.Company).filter(model.Company.stock_code == stock_code).one()
    risk_results = analyze_revenue_risk(db, company_item, risk_results)
    risk_results = analyze_business_loss_risk(db, company_item, risk_results)
    risk_results = analyze_operating_loss_risk(db, company_item, risk_results)
    risk_results = analyze_capital_impairment_risk(db, company_item, risk_results)
    return Inspection(company_item, risk_results)


def analyze_revenue_risk(db: SQLAlchemy, company_item: model.Company, results: []):
    if company_item.corp_cls == 'Y':
        standard_amount = 5000000000  # 50억
    elif company_item.corp_cls == 'K':
        standard_amount = 3000000000  # 30억

    result = common.revenue(db, company_item, '11011')
    result_count = result.count()

    if result_count == 0:
        risk_result = RiskResult(risk_type=Risk.REVENUE)
        risk_result.data_supported = False
        results.append(risk_result)
    else:
        for item in result:
            try:
                revenue = common.amount(item)
            except ValueError:
                risk_result = RiskResult(risk_type=Risk.REVENUE)
                risk_result.year = item.bsns_year
                risk_result.data_supported = False
                results.append(risk_result)
                continue

            risk_result = RiskResult(risk_type=Risk.REVENUE)
            risk_result.year = item.bsns_year
            risk_result.evidence.append(('revenue', revenue))

            if revenue < standard_amount * 1.1:
                risk_result.is_normal = False
            else:
                risk_result.is_normal = True

            results.append(risk_result)

    return results


def analyze_business_loss_risk(db: SQLAlchemy, company_item: model.Company, results: []):
    if company_item.corp_cls == 'Y':
        risk_result = RiskResult(risk_type=Risk.BUSINESS_LOSS)
        risk_result.is_normal = None
        risk_result.evidence.append('Not applicable')
        results.append(risk_result)

    elif company_item.corp_cls == 'K':

        result = common.equity(db, company_item, '11011')

        result_count = result.count()
        if result_count == 0:
            risk_result = RiskResult(risk_type=Risk.BUSINESS_LOSS)
            risk_result.data_supported = False
            results.append(risk_result)
        else:
            latest_year = int(result.first().bsns_year)
            for item in result:
                if latest_year - int(item.bsns_year) < 3:
                    try:
                        equity = common.amount(item)
                    except ValueError:
                        risk_result = RiskResult(risk_type=Risk.CAPITAL_IMPAIRMENT)
                        risk_result.data_supported = False
                        risk_result.year = item.bsns_year
                        risk_result.evidence.append('equity data invalid')
                        results.append(risk_result)
                        continue

                    profit_loss_before_tax_value = common.profit_loss_before_tax_value(db, company_item, item.bsns_year,
                                                                                       '11011')

                    if profit_loss_before_tax_value is None:
                        risk_result = RiskResult(risk_type=Risk.BUSINESS_LOSS)
                        risk_result.data_supported = False
                        risk_result.year = item.bsns_year
                        results.append(risk_result)
                    else:
                        risk_result = RiskResult(risk_type=Risk.BUSINESS_LOSS)
                        risk_result.year = item.bsns_year
                        risk_result.evidence.append(('profit_loss_before_tax_value', profit_loss_before_tax_value))
                        risk_result.evidence.append(('equity', equity))

                        if equity * 0.5 < profit_loss_before_tax_value * -1 and profit_loss_before_tax_value * -1 > 1000000000:
                            risk_result.is_normal = False
                        else:
                            risk_result.is_normal = True

                    results.append(risk_result)

    return results


def analyze_operating_loss_risk(db: SQLAlchemy, company_item: model.Company, results: []):
    if company_item.corp_cls == 'Y':
        risk_result = RiskResult(risk_type=Risk.OPERATING_LOSS)
        risk_result.is_normal = None
        risk_result.evidence.append('Not applicable')
        results.append(risk_result)

    elif company_item.corp_cls == 'K':

        result = common.operating_income_loss(db, company_item, '11011')
        result_count = result.count()
        if result_count == 0:
            risk_result = RiskResult(risk_type=Risk.OPERATING_LOSS)
            risk_result.data_supported = False
            results.append(risk_result)
        else:
            for item in result:
                try:
                    operating_loss = common.amount(item)
                except ValueError:
                    risk_result = RiskResult(risk_type=Risk.OPERATING_LOSS)
                    risk_result.data_supported = False
                    risk_result.year = item.bsns_year
                    results.append(risk_result)
                    continue

                risk_result = RiskResult(risk_type=Risk.OPERATING_LOSS)
                risk_result.year = item.bsns_year
                risk_result.evidence.append(('operating_income_loss', operating_loss))

                if operating_loss < 0:
                    risk_result.is_normal = False
                else:
                    risk_result.is_normal = True

                results.append(risk_result)

    return results


def analyze_capital_impairment_risk(db: SQLAlchemy, company_item: model.Company, results: []):
    # 자본금
    result = common.issued_capital(db, company_item, '11011')
    result_count = result.count()
    if result_count == 0:
        risk_result = RiskResult(risk_type=Risk.CAPITAL_IMPAIRMENT)
        risk_result.data_supported = False
        results.append(risk_result)
    else:
        for capital_item in result:
            try:
                capital = common.amount(capital_item)
            except ValueError:
                risk_result = RiskResult(risk_type=Risk.CAPITAL_IMPAIRMENT)
                risk_result.data_supported = False
                risk_result.year = capital_item.bsns_year
                risk_result.evidence.append('capital data invalid')
                results.append(risk_result)
                continue

            equity_owners_value = common.equity_owners_value(db, company_item, capital_item.bsns_year, '11011')
            if equity_owners_value is None:
                risk_result = RiskResult(risk_type=Risk.CAPITAL_IMPAIRMENT)
                risk_result.data_supported = False
                risk_result.year = capital_item.bsns_year
                risk_result.evidence.append('total_capital data invalid')
                results.append(risk_result)
                continue

            capital_impairment_ratio = (capital - equity_owners_value) / capital * 100

            risk_result = RiskResult(risk_type=Risk.CAPITAL_IMPAIRMENT)
            risk_result.year = capital_item.bsns_year
            risk_result.evidence.append(('capital', capital))
            risk_result.evidence.append(('equity_owners', equity_owners_value))
            risk_result.evidence.append(('capital_impairment_ratio', capital_impairment_ratio))

            if company_item.corp_cls == 'Y':

                if capital_impairment_ratio >= 50:
                    risk_result.is_normal = False
                else:
                    risk_result.is_normal = True

            elif company_item.corp_cls == 'K':

                if capital_impairment_ratio >= 50 or equity_owners_value < 1000000000:
                    risk_result.is_normal = False
                else:
                    risk_result.is_normal = True

            results.append(risk_result)

    return results
