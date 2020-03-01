from flask_sqlalchemy import SQLAlchemy
from orm import model


def stock_codes(db: SQLAlchemy):
    results = db.session.query(model.Company.stock_code, model.Company.stock_name)
    return results
