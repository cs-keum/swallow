from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import exists
from orm import model
from sqlalchemy import orm
from sqlalchemy import or_

from enum import Enum


class Risk(Enum):
    REVENUE = 1
    BUSINESS_LOSS = 2
    OPERATING_LOSS = 3
    CAPITAL_IMPAIRMENT = 4


class RiskResult(object):

    def __init__(self, company=None, risk_type=None):
        self._company = company
        self._risk_type = risk_type
        self._data_supported = True
        self._year = None
        self._is_normal = None
        self._evidence = []

    @property
    def company(self):
        return self._company

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


def analyze_revenue_risk(db: SQLAlchemy, stock_code):
    results = []
    company_item = db.session.query(model.Company).filter(model.Company.stock_code == stock_code).one()

    if company_item.corp_cls == 'Y':
        standard_amount = 5000000000  # 50억
    elif company_item.corp_cls == 'K':
        standard_amount = 3000000000  # 30억

    result = db.session.query(model.FinancialData).filter(
        model.FinancialData.corp_code == company_item.corp_code).filter(
        model.FinancialData.reprt_code == '11011').filter(
        or_(model.FinancialData.account_id == 'ifrs_Revenue',
            model.FinancialData.account_id == 'ifrs-full_Revenue')).order_by(
        model.FinancialData.bsns_year.desc())

    result_count = result.count()

    if result_count == 0 and db.session.query(
            exists().where(model.FinancialData.corp_code == company_item.corp_code).where(
                model.FinancialData.reprt_code == '11011')).scalar():
        result = db.session.query(model.FinancialData).filter(
            model.FinancialData.corp_code == company_item.corp_code).filter(
            model.FinancialData.reprt_code == '11011').filter(
            or_(model.FinancialData.account_nm == '영업수익',
                model.FinancialData.account_nm == '매출',
                model.FinancialData.account_nm == '매출액')).order_by(
            model.FinancialData.bsns_year.desc())

    result_count = result.count()

    if result_count == 0:
        risk_result = RiskResult(company=company_item, risk_type=Risk.REVENUE)
        risk_result.data_supported = False
        results.append(risk_result)
    else:
        for item in result:
            try:
                thstrm_amount = int(item.thstrm_amount.replace(',', ''))
            except ValueError:
                risk_result = RiskResult(company=company_item, risk_type=Risk.REVENUE)
                risk_result.year = item.bsns_year
                risk_result.data_supported = False
                results.append(risk_result)
                continue

            risk_result = RiskResult(company=company_item, risk_type=Risk.REVENUE)
            risk_result.year = item.bsns_year
            risk_result.evidence.append(('revenue', thstrm_amount))

            if thstrm_amount < standard_amount * 1.1:
                risk_result.is_normal = False
            else:
                risk_result.is_normal = True

            results.append(risk_result)

    return results


def analyze_business_loss_risk(db: SQLAlchemy, stock_code):
    results = []
    company_item = db.session.query(model.Company).filter(model.Company.stock_code == stock_code).one()

    risk_dic = {}

    if company_item.corp_cls == 'Y':
        risk_result = RiskResult(company=company_item, risk_type=Risk.BUSINESS_LOSS)
        risk_result.is_normal = True
        risk_result.evidence.append('Not applicable')
        results.append(risk_result)

    elif company_item.corp_cls == 'K':

        result = db.session.query(model.FinancialData).filter(
            model.FinancialData.corp_code == company_item.corp_code).filter(model.FinancialData.sj_div == 'BS').filter(
            model.FinancialData.reprt_code == '11011').filter(
            or_(model.FinancialData.account_nm == '자본총계', model.FinancialData.account_nm == '자본 총계',
                model.FinancialData.account_nm == '자본의 총계',
                model.FinancialData.account_id == 'ifrs_Equity')).order_by(
            model.FinancialData.bsns_year.desc())

        result_count = result.count()
        if result_count == 0:
            risk_result = RiskResult(company=company_item, risk_type=Risk.BUSINESS_LOSS)
            risk_result.data_supported = False
            results.append(risk_result)
        else:
            latest_year = int(result.first().bsns_year)
            for item in result:
                if latest_year - int(item.bsns_year) < 3:
                    try:
                        total_capital = int(item.thstrm_amount.replace(',', ''))
                    except ValueError:
                        risk_dic[item.bsns_year] = None

                    profit_loss_item = db.session.query(model.FinancialData).filter(
                        model.FinancialData.corp_code == company_item.corp_code).filter(
                        or_(model.FinancialData.account_nm.ilike('%{0}%'.format('법인세비용차감전')),
                            model.FinancialData.account_nm.ilike('%{0}%'.format('법인세차감전')),
                            model.FinancialData.account_nm.ilike('%{0}%'.format('법인세 비용 차감전')),
                            model.FinancialData.account_id == 'ifrs_ProfitLossBeforeTax')).filter(
                        model.FinancialData.bsns_year == item.bsns_year)

                    if profit_loss_item.count() == 0:
                        risk_result = RiskResult(company=company_item, risk_type=Risk.BUSINESS_LOSS)
                        risk_result.data_supported = False
                        risk_result.year = item.bsns_year
                        results.append(risk_result)
                    else:
                        profit_loss = int(profit_loss_item.first().thstrm_amount.replace(',', ''))

                        risk_result = RiskResult(company=company_item, risk_type=Risk.BUSINESS_LOSS)
                        risk_result.year = item.bsns_year
                        risk_result.evidence.append(('profit_loss', profit_loss))
                        risk_result.evidence.append(('total_capital', total_capital))

                        if profit_loss > 0:
                            risk_result.is_normal = True
                        else:
                            if total_capital * 0.5 < profit_loss * -1 and profit_loss * -1 > 1000000000:
                                risk_result.is_normal = False
                            else:
                                risk_result.is_normal = True

                        results.append(risk_result)

    return results


def analyze_operating_loss_risk(db: SQLAlchemy, stock_code):
    results = []
    company_item = db.session.query(model.Company).filter(model.Company.stock_code == stock_code).one()

    if company_item.corp_cls == 'Y':
        risk_result = RiskResult(company=company_item, risk_type=Risk.OPERATING_LOSS)
        risk_result.is_normal = True
        risk_result.evidence.append('Not applicable')
        results.append(risk_result)

    elif company_item.corp_cls == 'K':

        result = db.session.query(model.FinancialData).filter(
            model.FinancialData.corp_code == company_item.corp_code).filter(
            or_(model.FinancialData.sj_div == 'CIS', model.FinancialData.sj_div == 'IS')).filter(
            or_(model.FinancialData.account_nm == '영업이익(손실)', model.FinancialData.account_nm == '영업이익',
                model.FinancialData.account_id == 'dart_OperatingIncomeLoss')
        ).order_by(model.FinancialData.bsns_year.desc())

        result_count = result.count()
        if result_count == 0:
            risk_result = RiskResult(company=company_item, risk_type=Risk.OPERATING_LOSS)
            risk_result.data_supported = False
            results.append(risk_result)
        else:
            for item in result:
                try:
                    operating_loss = int(item.thstrm_amount.replace(',', ''))
                except ValueError:
                    risk_result = RiskResult(company=company_item, risk_type=Risk.OPERATING_LOSS)
                    risk_result.data_supported = False
                    risk_result.year = item.bsns_year
                    results.append(risk_result)
                    continue

                risk_result = RiskResult(company=company_item, risk_type=Risk.OPERATING_LOSS)
                risk_result.year = item.bsns_year
                risk_result.evidence.append(('operating_income_loss', operating_loss))

                if operating_loss < 0:
                    risk_result.is_normal = False
                else:
                    risk_result.is_normal = True

                results.append(risk_result)

    return results


def analyze_capital_impairment_risk(db: SQLAlchemy, stock_code):
    results = []
    company_item = db.session.query(model.Company).filter(model.Company.stock_code == stock_code).one()

    # 자본금
    result = db.session.query(model.FinancialData).filter(
        model.FinancialData.corp_code == company_item.corp_code).filter(model.FinancialData.sj_div == 'BS').filter(
        or_(model.FinancialData.account_nm == '자본금',
            model.FinancialData.account_nm == '보통주자본금',
            model.FinancialData.account_nm == '납입자본',
            model.FinancialData.account_id == 'ifrs_IssuedCapital')).filter(
        model.FinancialData.reprt_code == '11011').order_by(
        model.FinancialData.bsns_year.desc())

    result_count = result.count()
    if result_count == 0:
        risk_result = RiskResult(company=company_item, risk_type=Risk.CAPITAL_IMPAIRMENT)
        risk_result.data_supported = False
        results.append(risk_result)
    else:
        for capital_item in result:
            try:
                capital = int(capital_item.thstrm_amount.replace(',', ''))
            except ValueError:
                risk_result = RiskResult(company=company_item, risk_type=Risk.CAPITAL_IMPAIRMENT)
                risk_result.data_supported = False
                risk_result.year = capital_item.bsns_year
                risk_result.evidence.append('capital data invalid')
                results.append(risk_result)
                continue

            controlling_interests = None

            # 지배지분
            controlling_interests_item = db.session.query(model.FinancialData).filter(
                model.FinancialData.corp_code == company_item.corp_code).filter(
                model.FinancialData.sj_div == 'BS').filter(
                or_(model.FinancialData.account_id == 'ifrs_EquityAttributableToOwnersOfParent')
            ).filter(model.FinancialData.reprt_code == '11011').filter(
                model.FinancialData.bsns_year == capital_item.bsns_year)

            if controlling_interests_item.count() > 0:
                try:
                    controlling_interests = int(controlling_interests_item.first().thstrm_amount.replace(',', ''))
                except ValueError:
                    pass

            if controlling_interests is None:

                # 자본총계
                total_capital_item = db.session.query(model.FinancialData).filter(
                    model.FinancialData.corp_code == company_item.corp_code).filter(
                    model.FinancialData.sj_div == 'BS').filter(
                    or_(model.FinancialData.account_nm == '자본총계',
                        model.FinancialData.account_nm == '자본 총계',
                        model.FinancialData.account_nm == '자본의 총계',
                        model.FinancialData.account_id == 'ifrs_Equity')
                ).filter(model.FinancialData.reprt_code == '11011').filter(
                    model.FinancialData.bsns_year == capital_item.bsns_year)

                if total_capital_item.count() == 0:
                    risk_result = RiskResult(company=company_item, risk_type=Risk.CAPITAL_IMPAIRMENT)
                    risk_result.data_supported = False
                    risk_result.year = capital_item.bsns_year
                    risk_result.evidence.append('total_capital data invalid')
                    results.append(risk_result)
                    continue

                controlling_interests = int(total_capital_item.first().thstrm_amount.replace(',', ''))

                # 비지배지분
                non_controlling_interests_item = db.session.query(model.FinancialData).filter(
                    model.FinancialData.corp_code == company_item.corp_code).filter(
                    model.FinancialData.sj_div == 'BS').filter(
                    or_(model.FinancialData.account_nm == '비지배지분',
                        model.FinancialData.account_nm == '비지배주주지분',
                        model.FinancialData.account_id == 'ifrs_NoncontrollingInterests')
                ).filter(model.FinancialData.reprt_code == '11011').filter(
                    model.FinancialData.bsns_year == capital_item.bsns_year)

                if non_controlling_interests_item.count() > 0:
                    try:
                        controlling_interests = int(
                            total_capital_item.first().thstrm_amount.replace(',', '')) - int(
                            non_controlling_interests_item.first().thstrm_amount.replace(',', ''))
                    except ValueError:
                        pass

            capital_impairment_ratio = (capital - controlling_interests) / capital * 100

            risk_result = RiskResult(company=company_item, risk_type=Risk.CAPITAL_IMPAIRMENT)
            risk_result.year = capital_item.bsns_year
            risk_result.evidence.append(('capital', capital))
            risk_result.evidence.append(('controlling_interests', controlling_interests))
            risk_result.evidence.append(('capital_impairment_ratio', capital_impairment_ratio))

            if company_item.corp_cls == 'Y':

                if capital_impairment_ratio >= 50:
                    risk_result.is_normal = False
                else:
                    risk_result.is_normal = True

            elif company_item.corp_cls == 'K':

                if capital_impairment_ratio >= 50 or controlling_interests < 1000000000:
                    risk_result.is_normal = False
                else:
                    risk_result.is_normal = True

            results.append(risk_result)

    return results
