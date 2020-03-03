from flask_sqlalchemy import SQLAlchemy
from orm import model
from sqlalchemy import orm


def analyze_revenue_risk(db: SQLAlchemy, stock_code):
    company_item = db.session.query(model.Company).filter(model.Company.stock_code == stock_code).one()
    if company_item.corp_cls == 'Y':
        standard_amount = 5000000000
    elif company_item.corp_cls == 'K':
        standard_amount = 3000000000
    else:
        return None

    result = db.session.query(model.FinancialData).filter(
        model.FinancialData.stock_code == stock_code).filter(model.FinancialData.fs_div == 'CFS').filter(
        model.FinancialData.account_nm == '매출액').order_by(model.FinancialData.bsns_year.asc())

    for item in result:
        standard_amount = 0
        thstrm_amount = int(item.thstrm_amount.replace(',', ''))
        if thstrm_amount < standard_amount * 1.1:
            return False
        else:
            return True


def analyze_business_ross_risk(db: SQLAlchemy, stock_code):
    company_item = db.session.query(model.Company).filter(model.Company.stock_code == stock_code).one()
    if company_item.corp_cls == 'Y':
        return True
    elif company_item.corp_cls == 'K':

        result = db.session.query(model.FinancialData).filter(
            model.FinancialData.stock_code == stock_code).filter(model.FinancialData.fs_div == 'CFS').filter(
            model.FinancialData.account_nm == '자본총계').order_by(model.FinancialData.bsns_year.desc())

        if result.first() is None:
            return None

        latest_year = int(result.first().bsns_year)
        count = 0
        for item in result:
            if latest_year - int(item.bsns_year) < 3:
                total_capital = int(item.thstrm_amount.replace(',', ''))
                try:
                    profit_ross_item = db.session.query(model.FinancialData).filter(
                        model.FinancialData.stock_code == stock_code).filter(
                        model.FinancialData.fs_div == 'CFS').filter(
                        model.FinancialData.account_nm == '법인세차감전 순이익').filter(
                        model.FinancialData.bsns_year == item.bsns_year).one()
                except orm.exc.NoResultFound:
                    return None

                profit_ross = int(profit_ross_item.thstrm_amount.replace(',', ''))

                if profit_ross > 0:
                    continue

                if total_capital * 0.5 < profit_ross * -1 and profit_ross * -1 > 100000000:
                    count += 1

        if count >= 2:
            return False
        else:
            return True
    else:
        return None
