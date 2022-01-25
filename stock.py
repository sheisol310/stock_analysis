"""
@project       : Queens College CSCI 365/765 Computational Finance
@Instructor    : Dr. Alex Pang

@Group Name    : Group 7
@Student Name  : Weifeng Zhao
                 Ching Kung Lin
                 Jianhui Chen

@Date          : Nov 2021


"""
import enum
import calendar
import math
import pandas as pd
import numpy as np

import datetime
from scipy.stats import norm

from math import log, exp, sqrt

from utils import MyYahooFinancials


class Stock(object):
    """
    Stock class for getting financial statements as well as pricing data
    """

    def __init__(self, symbol, spot_price=None, sigma=None, dividend_yield=0, freq='annual'):
        self.symbol = symbol
        self.spot_price = spot_price
        self.sigma = sigma
        self.dividend_yield = dividend_yield
        self.yfinancial = MyYahooFinancials(symbol, freq)
        self.ohlcv_df = None

    def get_daily_hist_price(self, start_date, end_date):
        """
        Get daily historical OHLCV pricing dataframe
        """
        # TODO
        data = self.yfinancial.get_historical_price_data(str(start_date), str(end_date), 'daily')
        self.ohlcv_df = pd.DataFrame(data[self.symbol]['prices']).set_index('formatted_date')
        # end TODO

    def calc_returns(self):
        """
        """
        self.ohlcv_df['prev_close'] = self.ohlcv_df['close'].shift(1)
        self.ohlcv_df['returns'] = (self.ohlcv_df['close'] - self.ohlcv_df['prev_close']) / \
                                   self.ohlcv_df['prev_close']

    # financial statements related methods

    def get_total_debt(self):
        """
        return Total debt of the company

        Total Debt = Long Term Debt + Current (short term) Debt
        Current Liabilities = Account Payables + Current Deferred Liabilities + Current Debt + Other Current Liabilities
        Current Debt = Current Liabilities - Account Payables - Current Deferred Liabilities - Other Current Liabilities
        """
        result = None
        # TODO
        long_term_debt = self.yfinancial.get_long_term_debt()
        total_current_liabilities = self.yfinancial.get_total_current_liabilities()
        account_payable = self.yfinancial.get_account_payable()
        other_current_liabilities = self.yfinancial.get_other_current_liabilities()
        short_term_debt = total_current_liabilities - account_payable - other_current_liabilities

        result = long_term_debt + short_term_debt
        # end TODO
        return (result)

    def get_free_cashflow(self):
        """
        return Free Cashflow of the company

        Free Cash Flow = Operating Cash Flow + Capital Expenditure
        """
        result = None
        # TODO
        opertating_cash_flow = self.yfinancial.get_operating_cashflow()
        capital_expenditure = self.yfinancial.get_capital_expenditures()

        result = opertating_cash_flow + capital_expenditure
        # end TODO
        return (result)

    def get_cash_and_cash_equivalent(self):
        """
        Return cash and cash equivalent of the company
        """
        result = None
        # TODO
        result = self.yfinancial.get_cash()
        # end TODO
        return (result)

    def get_num_shares_outstanding(self):
        """
        get current number of shares outstanding from Yahoo financial library
        """
        result = None
        # TODO
        result = self.yfinancial.get_num_shares_outstanding()
        # end TODO
        return (result)

    def get_beta(self):
        """
        get beta from Yahoo financial
        """
        result = None
        # TODO
        result = self.yfinancial.get_beta()
        # end TODO
        return (result)

    def lookup_wacc_by_beta(self, beta):
        """
        lookup wacc by using the table in the DiscountedCashFlowModel lecture powerpoint
        """
        result = None
        # TODO:
        if beta < 0.8:
            result = 0.05
        elif beta < 1.0:
            result = 0.06
        elif beta < 1.1:
            result = 0.065
        elif beta < 1.2:
            result = 0.07
        elif beta < 1.3:
            result = 0.075
        elif beta < 1.5:
            result = 0.08
        elif beta < 1.6:
            result = 0.085
        else:
            result = 0.09
        # end TODO
        return (result)


def _test():
    # a few basic unit tests
    symbol = 'AAPL'
    stock = Stock(symbol)
    print(f"Free Cash Flow for {symbol} is {stock.get_free_cashflow()}")

    # 
    start_date = datetime.date(2020, 1, 1)
    end_date = datetime.date(2021, 11, 1)
    stock.get_daily_hist_price(start_date, end_date)
    print(type(stock.ohlcv_df))
    print(stock.ohlcv_df.head())


if __name__ == "__main__":
    _test()
