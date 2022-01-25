"""
@project       : Queens College CSCI 365/765 Computational Finance
@Instructor    : Dr. Alex Pang
@Date          : June 2021

@Group Name    : Group 7
@Student Name  : Weifeng Zhao
                 Ching Kung Lin
                 Jianhui Chen

@Date          : Nov 2021

"""

import pandas as pd
import datetime

from stock import Stock
from DCF_model import DiscountedCashFlowModel
import yfinance as yf
from TA import RSI, ExponentialMovingAverages, SimpleMovingAverages


def run():
    """
    Read in the input file.
    Call the DCF to compute its DCF value and add the following columns to the output file.
    You are welcome to add additional valuation metrics as you see fit

    Symbol
    EPS Next 5Y in percent
    DCF Value
    Current Price
    Sector
    Market Cap
    Beta
    Total Assets
    Total Debt
    Free Cash Flow
    P/E Ratio
    Price to Sale Ratio
    RSI
    10 day EMA
    20 day SMA
    50 day SMA
    200 day SMA

    """
    input_fname = "StockUniverse.csv"
    output_fname = "StockUniverseOutput.csv"

    as_of_date = datetime.date(2021, 12, 1)
    df = pd.read_csv(input_fname)

    # TODO
    results = []
    for index, row in df.iterrows():
        stock = Stock(row['Symbol'], 'annual')
        print('Start Working on {}'.format(stock.symbol))
        try:
            stock.get_daily_hist_price('2021-11-1', as_of_date)
            model = DiscountedCashFlowModel(stock, as_of_date)

            short_term_growth_rate = float(row['EPS Next 5Y in percent']) / 100
            medium_term_growth_rate = short_term_growth_rate / 2
            long_term_growth_rate = 0.04

            model.set_FCC_growth_rate(short_term_growth_rate, medium_term_growth_rate, long_term_growth_rate)

            eps = row['EPS Next 5Y in percent']
            fair_value = model.calc_fair_value()
            current_price = stock.yfinancial.get_current_price()
            sector = yf.Ticker(stock.symbol).info['sector']
            market_cap = stock.yfinancial.get_market_cap()
            beta = stock.get_beta()
            total_assets = list(
                stock.yfinancial.get_financial_stmts('annual', 'balance').get('balanceSheetHistory')[stock.symbol][
                    0].values())[0]['totalAssets']
            total_debt = stock.get_total_debt()
            free_cash_flow = stock.get_free_cashflow()
            p_e_ratio = stock.yfinancial.get_pe_ratio()
            price_to_sale_ratio = stock.yfinancial.get_price_to_sales()
            rsi = RSI(stock.ohlcv_df).run()[-1]

            ema = ExponentialMovingAverages(stock.ohlcv_df, [10])
            ema.run()
            ema10 = ema.get_series(10)[-1]

            smas = SimpleMovingAverages(stock.ohlcv_df, [20, 50, 200])
            smas.run()
            smas20 = smas.get_series(20)[-1]
            smas50 = smas.get_series(50)[-1]
            smas200 = smas.get_series(200)[-1]

            results.append(
                [stock.symbol, eps, fair_value, current_price, sector, market_cap, beta, total_assets, total_debt,
                 free_cash_flow, p_e_ratio, price_to_sale_ratio, rsi, ema10, smas20, smas50, smas200])
        except KeyError:
            empty_result = ['' for i in range(16)]
            empty_result.insert(0, stock.symbol)
            results.append(empty_result)

        print('Finish Working on {}'.format(stock.symbol))

    # save the output into a StockUniverseOutput.csv file
    header = ['Symbol', 'EPS Next 5Y in percent', 'DCF value', 'Current Price', 'Sector', 'Market Cap', 'Beta',
              'Total Assets', 'Total Debt', 'Free Cash Flow', 'P/E Ratio', 'P/S Ratio', 'RSI', '10 day EMA',
              '20 day SMA', '50 day SMA', '200 day SMA']
    data = pd.DataFrame(results, columns=header)
    data.to_csv(output_fname, index=False, header=header)
    # ....

    # end TODO


if __name__ == "__main__":
    run()
