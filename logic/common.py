from flask_sqlalchemy import SQLAlchemy
from orm import model


def stock_codes(db: SQLAlchemy):
    results = db.session.query(model.Company)
    return results


def company(db: SQLAlchemy, stock_code):
    result = db.session.query(model.Company).filter(model.Company.stock_code == stock_code).one()
    return result
