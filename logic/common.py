from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import exists
from sqlalchemy import or_
from orm import model


def stock_codes(db: SQLAlchemy):
    results = db.session.query(model.Company)
    return results


def company(db: SQLAlchemy, stock_code):
    result = db.session.query(model.Company).filter(model.Company.stock_code == stock_code).one()
    return result


def amount(item):
    try:
        return int(item.thstrm_amount.replace(',', ''))
    except:
        return None


def revenue(db: SQLAlchemy, company_item, reprt_code):
    result = db.session.query(model.FinancialData).filter(
        model.FinancialData.corp_code == company_item.corp_code).filter(
        model.FinancialData.reprt_code == reprt_code).filter(
        or_(model.FinancialData.account_id == 'ifrs_Revenue',
            model.FinancialData.account_id == 'ifrs-full_Revenue')).order_by(
        model.FinancialData.bsns_year.desc())

    result_count = result.count()

    if result_count == 0 and db.session.query(
            exists().where(model.FinancialData.corp_code == company_item.corp_code).where(
                model.FinancialData.reprt_code == reprt_code)).scalar():
        result = db.session.query(model.FinancialData).filter(
            model.FinancialData.corp_code == company_item.corp_code).filter(
            model.FinancialData.reprt_code == reprt_code).filter(
            or_(model.FinancialData.account_nm == '영업수익',
                model.FinancialData.account_nm == '매출',
                model.FinancialData.account_nm == '매출액')).order_by(
            model.FinancialData.bsns_year.desc())

    return result


def cash_flows(db: SQLAlchemy, company_item, reprt_code):
    result = db.session.query(model.FinancialData).filter(
        model.FinancialData.corp_code == company_item.corp_code).filter(
        model.FinancialData.reprt_code == reprt_code).filter(
        or_(model.FinancialData.account_id == 'ifrs_CashFlowsFromUsedInOperatingActivities',
            model.FinancialData.account_id == 'ifrs-full_CashFlowsFromUsedInOperatingActivities')).order_by(
        model.FinancialData.bsns_year.desc())

    result_count = result.count()

    if result_count == 0 and db.session.query(
            exists().where(model.FinancialData.corp_code == company_item.corp_code).where(
                model.FinancialData.reprt_code == reprt_code)).scalar():
        result = db.session.query(model.FinancialData).filter(
            model.FinancialData.corp_code == company_item.corp_code).filter(
            model.FinancialData.reprt_code == reprt_code).filter(
            or_(model.FinancialData.account_nm == '영업활동현금흐름',
                model.FinancialData.account_nm == '영업활동으로인한현금흐름',
                model.FinancialData.account_nm == '영업활동으로 인한 현금흐름',
                model.FinancialData.account_nm == 'Ⅰ.영업활동으로 인한 현금흐름')).order_by(
            model.FinancialData.bsns_year.desc())

    if result.count() == 0:
        return None
    else:
        return amount(result.first())


def equity(db: SQLAlchemy, company_item, reprt_code):
    result = db.session.query(model.FinancialData).filter(
        model.FinancialData.corp_code == company_item.corp_code).filter(model.FinancialData.sj_div == 'BS').filter(
        model.FinancialData.reprt_code == reprt_code).filter(
        or_(model.FinancialData.account_nm == '자본총계',
            model.FinancialData.account_nm == '자본 총계',
            model.FinancialData.account_nm == '자본의 총계',
            model.FinancialData.account_id == 'ifrs_Equity')).order_by(
        model.FinancialData.bsns_year.desc())

    return result


def profit_loss_before_tax_value(db, company_item, bsns_year, reprt_code):
    profit_loss_item = db.session.query(model.FinancialData).filter(
        model.FinancialData.corp_code == company_item.corp_code).filter(
        model.FinancialData.reprt_code == reprt_code).filter(
        or_(model.FinancialData.account_nm.ilike('%{0}%'.format('법인세비용차감전')),
            model.FinancialData.account_nm.ilike('%{0}%'.format('법인세차감전')),
            model.FinancialData.account_nm.ilike('%{0}%'.format('법인세 비용 차감전')),
            model.FinancialData.account_id == 'ifrs_ProfitLossBeforeTax')).filter(
        model.FinancialData.bsns_year == bsns_year)
    if profit_loss_item.count() == 0:
        return None
    else:
        return amount(profit_loss_item.first())


def operating_income_loss(db, company_item, reprt_code):
    result = db.session.query(model.FinancialData).filter(
        model.FinancialData.corp_code == company_item.corp_code).filter(
        or_(model.FinancialData.sj_div == 'CIS', model.FinancialData.sj_div == 'IS')).filter(
        or_(model.FinancialData.account_nm == '영업이익(손실)',
            model.FinancialData.account_nm == '영업이익',
            model.FinancialData.account_id == 'dart_OperatingIncomeLoss')).filter(
        model.FinancialData.reprt_code == reprt_code).order_by(
        model.FinancialData.bsns_year.desc())

    return result


def issued_capital(db, company_item, reprt_code):
    result = db.session.query(model.FinancialData).filter(
        model.FinancialData.corp_code == company_item.corp_code).filter(model.FinancialData.sj_div == 'BS').filter(
        or_(model.FinancialData.account_nm == '자본금',
            # model.FinancialData.account_nm == '보통주자본금',
            model.FinancialData.account_nm == '납입자본',
            model.FinancialData.account_id == 'ifrs_IssuedCapital')).filter(
        model.FinancialData.reprt_code == reprt_code).order_by(
        model.FinancialData.bsns_year.desc())
    return result


def equity_owners_value(db, company_item, bsns_year, reprt_code):
    # 지배지분
    equity_owners_of_parent_item = db.session.query(model.FinancialData).filter(
        model.FinancialData.corp_code == company_item.corp_code).filter(
        model.FinancialData.sj_div == 'BS').filter(
        or_(model.FinancialData.account_id == 'ifrs_EquityAttributableToOwnersOfParent')).filter(
        model.FinancialData.reprt_code == reprt_code).filter(
        model.FinancialData.bsns_year == bsns_year)

    if equity_owners_of_parent_item.count() > 0:
        try:
            return amount(equity_owners_of_parent_item.first())
        except ValueError:
            pass

    # 자본총계
    total_capital_item = db.session.query(model.FinancialData).filter(
        model.FinancialData.corp_code == company_item.corp_code).filter(
        model.FinancialData.sj_div == 'BS').filter(
        or_(model.FinancialData.account_nm == '자본총계',
            model.FinancialData.account_nm == '자본 총계',
            model.FinancialData.account_nm == '자본의 총계',
            model.FinancialData.account_id == 'ifrs_Equity')
    ).filter(model.FinancialData.reprt_code == reprt_code).filter(
        model.FinancialData.bsns_year == bsns_year)

    if total_capital_item.count() == 0:
        return None

    # 비지배지분
    non_controlling_interests_item = db.session.query(model.FinancialData).filter(
        model.FinancialData.corp_code == company_item.corp_code).filter(
        model.FinancialData.sj_div == 'BS').filter(
        or_(model.FinancialData.account_nm == '비지배지분',
            model.FinancialData.account_nm == '비지배주주지분',
            model.FinancialData.account_id == 'ifrs_NoncontrollingInterests')).filter(
        model.FinancialData.reprt_code == reprt_code).filter(
        model.FinancialData.bsns_year == bsns_year)

    if non_controlling_interests_item.count() > 0:
        try:
            return amount(total_capital_item.first()) - amount(non_controlling_interests_item.first())
        except:
            pass
    else:
        return amount(total_capital_item.first())
