from sqlalchemy import Column, String, Integer, Float, Date, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Company(Base):
    __tablename__ = 'company'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)  # primary key for event table
    corp_code = Column(String(8))
    corp_name = Column(String(50))
    corp_name_eng = Column(String(100))
    stock_name = Column(String(50))
    stock_code = Column(String(6))
    ceo_nm = Column(String(150))
    corp_cls = Column(String(1))
    jurir_no = Column(String(50))
    bizr_no = Column(String(50))
    adres = Column(String(100))
    hm_url = Column(String(50))
    ir_url = Column(String(100))
    phn_no = Column(String(50))
    fax_no = Column(String(50))
    induty_code = Column(String(10))
    est_dt = Column(Date)
    acc_mt = Column(String(10))
    sector = Column(String(100))
    performance_updated = Column(Date)

    def __init__(self, corp_code, corp_name, corp_name_eng, stock_name, stock_code, ceo_nm, corp_cls, jurir_no,
                 bizr_no, address, hm_url, ir_url, phn_no, fax_no, industry_code, est_dt, acc_mt, sector,
                 performance_updated):
        self.corp_code = corp_code
        self.corp_name = corp_name
        self.corp_name_eng = corp_name_eng
        self.stock_name = stock_name
        self.stock_code = stock_code
        self.ceo_nm = ceo_nm
        self.corp_cls = corp_cls
        self.jurir_no = jurir_no
        self.bizr_no = bizr_no
        self.address = address
        self.hm_url = hm_url
        self.ir_url = ir_url
        self.phn_no = phn_no
        self.fax_no = fax_no
        self.industry_code = industry_code
        self.est_dt = est_dt
        self.acc_mt = acc_mt
        self.sector = sector
        self.performance_updated = performance_updated

    def as_dict(self):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns}


class CompanyPerformance(Base):
    __tablename__ = 'company_performance'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)  # primary key for event table
    stock_code = Column(String(50), nullable=False)
    period_division = Column(String(50))
    is_consensus = Column(Boolean)
    creation_date = Column(Date)
    settlement_date = Column(Date)
    revenue = Column(String(20))
    operating_profit = Column(String(20))
    net_income = Column(String(20))
    op_margin = Column(Float)
    net_margin = Column(Float)
    roe = Column(Float)
    debt_ratio = Column(Float)
    quick_ratio = Column(Float)
    reserve_ration = Column(String(20))
    eps = Column(String(20))
    per = Column(Float)
    bps = Column(String(20))
    pbr = Column(Float)
    dividend_per_share = Column(String(20))
    dividend_yield_ratio = Column(Float)
    dividend_payout_ratio = Column(String(20))

    def __init__(self, stock_code=None, period_division=None, is_consensus=None, creation_date=None,
                 settlement_date=None, revenue=None, operating_profit=None,
                 net_income=None, op_margin=None, net_margin=None, roe=None, debt_ratio=None, quick_ratio=None,
                 reserve_ration=None, eps=None,
                 per=None, bps=None, pbr=None, dividend_per_share=None, dividend_yield_ratio=None,
                 dividend_payout_ratio=None):
        self.stock_code = stock_code
        self.period_division = period_division
        self.is_consensus = is_consensus
        self.creation_date = creation_date
        self.settlement_date = settlement_date
        self.revenue = revenue
        self.operating_profit = operating_profit
        self.net_income = net_income
        self.op_margin = op_margin
        self.net_margin = net_margin
        self.roe = roe
        self.debt_ratio = debt_ratio
        self.quick_ratio = quick_ratio
        self.reserve_ration = reserve_ration
        self.eps = eps
        self.per = per
        self.bps = bps
        self.pbr = pbr
        self.dividend_per_share = dividend_per_share
        self.dividend_yield_ratio = dividend_yield_ratio
        self.dividend_payout_ratio = dividend_payout_ratio


class InvestRatio(Base):
    __tablename__ = 'invest_ratio'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)  # primary key for event table
    tdate = Column(Date)
    stock_code = Column(String(50))
    stock_name = Column(String(50))
    managed = Column(String(10))
    price = Column(Integer)
    eps = Column(Float)
    per = Column(Float)
    bps = Column(Float)
    pbr = Column(Float)
    roe = Column(Float)
    dividend = Column(Integer)
    dividend_yield = Column(Integer)

    def __init__(self, tdate, stock_code, stock_name, managed, price, eps, per, bps, pbr, roe, dividend,
                 dividend_yield):
        self.tdate = tdate
        self.stock_code = stock_code
        self.stock_name = stock_name
        self.managed = managed
        self.price = price
        self.eps = eps
        self.per = per
        self.bps = bps
        self.pbr = pbr
        self.roe = roe
        self.dividend = dividend
        self.dividend_yield = dividend_yield

    def as_dict(self):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns}


class StockDefinition(Base):
    __tablename__ = 'stock_definition'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)  # primary key for event table
    creation_datetime = Column(DateTime)
    stock_code = Column(String(50))
    stock_name = Column(String(50))
    stock_sector = Column(String(50))
    capital_value = Column(Integer)
    listed_stocks = Column(Integer)
    excess_profit = Column(Integer)
    price = Column(Integer)
    buy_price = Column(Integer)
    adequate_price = Column(Integer)
    excess_price = Column(Integer)
    roe = Column(Float)
    roes = Column(String(150))

    def __init__(self, creation_datetime=None, stock_code=None, stock_name=None, stock_sector=None, capital_value=0,
                 listed_stocks=0, excess_profit=0, price=0, buy_price=0, adequate_price=0, excess_price=0, roe=0,
                 roes={}):
        self.creation_datetime = creation_datetime
        self.stock_code = stock_code
        self.stock_name = stock_name
        self.stock_sector = stock_sector
        self.capital_value = capital_value
        self.listed_stocks = listed_stocks
        self.excess_profit = excess_profit
        self.price = price
        self.buy_price = buy_price
        self.adequate_price = adequate_price
        self.excess_price = excess_price
        self.roe = roe
        self.roes = roes

    def as_dict(self):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns}
