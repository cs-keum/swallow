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
    bsns_year_updated = Column(Integer)
    reprt_code_updated = Column(String(50))

    def __init__(self, corp_code, corp_name, corp_name_eng, stock_name, stock_code, ceo_nm, corp_cls, jurir_no,
                 bizr_no, address, hm_url, ir_url, phn_no, fax_no, industry_code, est_dt, acc_mt, sector,
                 performance_updated, bsns_year_updated, reprt_code_updated):
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
        self.bsns_year_updated = bsns_year_updated
        self.reprt_code_updated = reprt_code_updated

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

    def as_dict(self):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns}


class CompanyPresumed(Base):
    __tablename__ = 'company_presumed'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)  # primary key for event table
    stock_code = Column(String(50), nullable=False)
    performance_updated = Column(Date)
    yield_rate = Column(Float)
    roe = Column(Float)
    roes = Column(String(150))
    capital_value = Column(Float)
    cash_flows = Column(Float)

    def __init__(self, stock_code, performance_updated, yield_rate, roe, roes, capital_value, cash_flows):
        self.stock_code = stock_code
        self.performance_updated = performance_updated
        self.yield_rate = yield_rate
        self.roe = roe
        self.roes = roes
        self.capital_value = capital_value
        self.cash_flows = cash_flows

    def as_dict(self):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns}


class FinancialData(Base):
    __tablename__ = 'financial_data'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)  # primary key for event table
    rcept_no = Column(String(50))
    reprt_code = Column(String(5))
    bsns_year = Column(String(10))
    corp_code = Column(String(8))
    stock_code = Column(String(6))
    sj_div = Column(String(6))
    sj_nm = Column(String(20))
    account_id = Column(String(100))
    account_nm = Column(String(50))
    account_detail = Column(String(80))
    thstrm_nm = Column(String(30))
    thstrm_amount = Column(String(50))
    thstrm_add_amount = Column(String(50))
    frmtrm_nm = Column(String(30))
    frmtrm_amount = Column(String(50))
    frmtrm_q_nm = Column(String(30))
    frmtrm_q_amount = Column(String(50))
    frmtrm_add_amount = Column(String(50))
    bfefrmtrm_nm = Column(String(30))
    bfefrmtrm_amount = Column(String(50))
    ord = Column(String(5))

    def __init__(self, rcept_no=None, reprt_code=None, bsns_year=None, corp_code=None, stock_code=None, fs_div=None,
                 fs_nm=None, sj_div=None, sj_nm=None, account_nm=None, thstrm_nm=None, thstrm_dt=None,
                 thstrm_amount=None, frmtrm_nm=None, frmtrm_dt=None, frmtrm_amount=None, ord=None,
                 thstrm_add_amount=None, frmtrm_add_amount=None, bfefrmtrm_nm=None, bfefrmtrm_dt=None,
                 bfefrmtrm_amount=None):
        self.rcept_no = rcept_no
        self.reprt_code = reprt_code
        self.bsns_year = bsns_year
        self.corp_code = corp_code
        self.stock_code = stock_code
        self.fs_div = fs_div
        self.fs_nm = fs_nm
        self.sj_div = sj_div
        self.sj_nm = sj_nm
        self.account_nm = account_nm
        self.thstrm_nm = thstrm_nm
        self.thstrm_dt = thstrm_dt
        self.thstrm_amount = thstrm_amount
        self.frmtrm_nm = frmtrm_nm
        self.frmtrm_dt = frmtrm_dt
        self.frmtrm_amount = frmtrm_amount
        self.ord = ord
        self.thstrm_add_amount = thstrm_add_amount
        self.frmtrm_add_amount = frmtrm_add_amount
        self.bfefrmtrm_nm = bfefrmtrm_nm
        self.bfefrmtrm_dt = bfefrmtrm_dt
        self.bfefrmtrm_amount = bfefrmtrm_amount

    def as_dict(self):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns}


class MarketCondition(Base):
    __tablename__ = 'market_condition'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)  # primary key for event table
    stock_code = Column(String(50))
    stock_name = Column(String(50))
    current_price = Column(Integer)
    compare = Column(Integer)
    fluctuation_rate = Column(Float)
    market_price = Column(Integer)
    high_price = Column(Integer)
    low_price = Column(Integer)
    trading_volume = Column(Float)
    transaction_amount = Column(Float)
    total_market_price = Column(Float)
    total_market_price_ratio = Column(Float)
    listed_stocks = Column(Float)

    def __init__(self, stock_code, stock_name, current_price, compare, fluctuation_rate, market_price, high_price,
                 low_price, trading_volume, transaction_amount, total_market_price, total_market_price_ratio,
                 listed_stocks):
        self.stock_code = stock_code
        self.stock_name = stock_name
        self.current_price = current_price
        self.compare = compare
        self.fluctuation_rate = fluctuation_rate
        self.market_price = market_price
        self.high_price = high_price
        self.low_price = low_price
        self.trading_volume = trading_volume
        self.transaction_amount = transaction_amount
        self.total_market_price = total_market_price
        self.total_market_price_ratio = total_market_price_ratio
        self.listed_stocks = listed_stocks

    def as_dict(self):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns}


class ForeignHolding(Base):
    __tablename__ = 'foreign_holding'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)  # primary key for event table
    stock_code = Column(String(50))
    stock_name = Column(String(50))
    listed_stocks = Column(Float)
    foreign_holding_limit = Column(Float)
    foreign_holding = Column(Float)
    foreign_holding_ratio = Column(Float)

    def __init__(self, stock_code, stock_name, listed_stocks, foreign_holding_limit, foreign_holding,
                 foreign_holding_ratio):
        self.stock_code = stock_code
        self.stock_name = stock_name
        self.listed_stocks = listed_stocks
        self.foreign_holding_limit = foreign_holding_limit
        self.foreign_holding = foreign_holding
        self.foreign_holding_ratio = foreign_holding_ratio

    def as_dict(self):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns}


class InvestReference(Base):
    __tablename__ = 'invest_reference'
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
    dividend = Column(Integer)
    dividend_yield = Column(Integer)

    def __init__(self, tdate, stock_code, stock_name, managed, price, eps, per, bps, pbr, dividend,
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
    industry_code = Column(String(10))
    capital_value = Column(Integer)
    applied_bsns_year = Column(Integer)
    applied_reprt_code = Column(String(50))
    listed_stocks = Column(Integer)
    trading_volume = Column(Integer)
    total_market_price = Column(Integer)
    cash_flows = Column(Integer)
    total_market_price_cash_flows_ratio = Column(Integer)
    foreign_holding_ratio = Column(Float)
    excess_profit = Column(Integer)
    price_gap_ratio = Column(Float)
    price = Column(Integer)
    buy_price = Column(Integer)
    adequate_price = Column(Integer)
    excess_price = Column(Integer)
    per = Column(Float)
    bpr = Column(Float)
    dividend = Column(Integer)
    dividend_yield = Column(Float)
    roe = Column(Float)
    roes = Column(String(150))

    def __init__(self, creation_datetime=None, stock_code=None, stock_name=None, stock_sector=None,
                 industry_code=None, capital_value=0, applied_bsns_year=None, applied_reprt_code=None, listed_stocks=0,
                 trading_volume=0, total_market_price=0, cash_flows=0, total_market_price_cash_flows_ratio=0,
                 foreign_holding_ratio=0, excess_profit=0, price_gap_ratio=0, price=0, buy_price=0, adequate_price=0,
                 excess_price=0, per=0, bpr=0, dividend=0, dividend_yield=0, roe=0, roes={}):
        self.creation_datetime = creation_datetime
        self.stock_code = stock_code
        self.stock_name = stock_name
        self.stock_sector = stock_sector
        self.industry_code = industry_code
        self.capital_value = capital_value
        self.applied_bsns_year = applied_bsns_year
        self.applied_reprt_code = applied_reprt_code
        self.listed_stocks = listed_stocks
        self.trading_volume = trading_volume
        self.total_market_price = total_market_price
        self.cash_flows = cash_flows
        self.total_market_price_cash_flows_ratio = total_market_price_cash_flows_ratio
        self.foreign_holding_ratio = foreign_holding_ratio
        self.excess_profit = excess_profit
        self.price_gap_ratio = price_gap_ratio
        self.price = price
        self.buy_price = buy_price
        self.adequate_price = adequate_price
        self.excess_price = excess_price
        self.per = per
        self.bpr = bpr
        self.dividend = dividend
        self.dividend_yield = dividend_yield
        self.roe = roe
        self.roes = roes

    def as_dict(self):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns}
