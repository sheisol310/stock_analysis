"""

@project       : Queens College CSCI 365/765 Computational Finance
@Instructor    : Dr. Alex Pang

@Group Name    : Group 7
@Student Name  : Weifeng Zhao
                 Ching Kung Lin
                 Jianhui Chen

@Date          : Fall 2021

A Bond Calculator Class

"""

import math
import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta
from bisection_method import bisection

import enum
import calendar

from datetime import date

from bond import Bond, DayCount, PaymentFrequency


def get_actual360_daycount_frac(start, end):
    day_in_year = 360
    day_count = (end - start).days
    return (day_count / day_in_year)


def get_30360_daycount_frac(start, end):
    day_in_year = 360
    day_count = 360 * (end.year - start.year) + 30 * (end.month - start.month - 1) + \
                max(0, 30 - start.day) + min(30, end.day)
    return (day_count / day_in_year)


def get_actualactual_daycount_frac(start, end):
    # TODO by Jianhui
    day_in_year = 365
    if start.year == end.year:
        if calendar.isleap(start.year):
            day_in_year += 1
        result = (end - start).days / day_in_year
    else:
        if calendar.isleap(start.year):
            result = (date(start.year, 12, 31) - start).days / 366 + (end - date(end.year, 1, 1)).days / 365
        elif calendar.isleap(end.year):
            result = (date(start.year, 12, 31) - start).days / 365 + (end - date(end.year, 1, 1)).days / 366
        else:
            result = (end - start).days / day_in_year

    return result


class BondCalculator(object):
    """
    Bond Calculator class for pricing a bond
    """

    def __init__(self, pricing_date):
        self.pricing_date = pricing_date

    def calc_one_period_discount_factor(self, bond, yld):
        # TODO by Jianhui
        payment_frequency = bond.payment_freq
        if payment_frequency == PaymentFrequency.ANNUAL:
            payments_per_year = 1
        elif payment_frequency == PaymentFrequency.SEMIANNUAL:
            payments_per_year = 2
        elif payment_frequency == PaymentFrequency.QUARTERLY:
            payments_per_year = 4
        elif payment_frequency == PaymentFrequency.MONTHLY:
            payments_per_year = 12
        else:
            raise Exception("Unsupported Payment Frequency")

        return 1 / (1 + yld / payments_per_year)

    def calc_clean_price(self, bond, yld):
        """
        Calculate bond price as of the pricing_date for a given yield
        bond price should be expressed in percentage eg 100 for a par bond
        """
        # TODO by Jianhui
        one_period_factor = self.calc_one_period_discount_factor(bond, yld)
        cash_flow = bond.coupon_payment.copy()
        cash_flow[-1] += bond.principal

        present_values = [cash_flow[i] * math.pow(one_period_factor, i + 1) for i in range(len(bond.coupon_payment))]

        return sum(present_values)

    def calc_accrual_interest(self, bond, settle_date):
        """
        calculate the accrual interest on given a settle_date
        by calculating the previous payment date first and use the date count
        from previous payment date to the settle_date
        """
        prev_pay_date = bond.get_previous_payment_date(settle_date)
        end_date = settle_date

        if bond.day_count == DayCount.DAYCOUNT_30360:
            frac = get_30360_daycount_frac(prev_pay_date, end_date)
        elif bond.day_count == DayCount.DAYCOUNT_ACTUAL_360:
            frac = get_actual360_daycount_frac(prev_pay_date, end_date)
        elif bond.day_count == DayCount.DAYCOUNT_ACTUAL_ACTUAL:
            frac = get_actualactual_daycount_frac(prev_pay_date, end_date)
        else:
            raise Exception("Unsupported Day Count")

        return frac * bond.coupon * bond.principal / 100

    def calc_macaulay_duration(self, bond, yld):
        """
        time to cashflow weighted by PV
        """
        present_value = self.calc_clean_price(bond, yld)
        one_period_factor = self.calc_one_period_discount_factor(bond, yld)

        cash_flows = bond.coupon_payment.copy()
        cash_flows[-1] += bond.principal
        discount_factors = [math.pow(one_period_factor, i) for i in range(1, len(cash_flows) + 1)]
        weighted_averages = [bond.payment_times_in_year[i] * cash_flows[i] * discount_factors[i]
                             for i in range(len(cash_flows))]
        return sum(weighted_averages) / present_value

    def calc_modified_duration(self, bond, yld):
        """
        calculate modified duration at a certain yield yld
        """
        macaulay_duration = self.calc_macaulay_duration(bond, yld)
        one_period_factor = self.calc_one_period_discount_factor(bond, yld)
        return - macaulay_duration * one_period_factor

    def calc_yield(self, bond, bond_price):
        """
        Calculate the yield to maturity on given a bond price using bisection method
        """
        def match_price(yld):
            calculator = BondCalculator(self.pricing_date)
            px = calculator.calc_clean_price(bond, yld)
            return (px - bond_price)

        # TODO: implement details here - Weifeng
        yld, n_iteractions = bisection(match_price, 0, 1, eps=1.0e-6)
        return (yld)

    def calc_convexity(self, bond, yld):
        # calculate convexity of a bond at a certain yield yld

        # TODO: implement details here - Weifeng
        one_period_factor = self.calc_one_period_discount_factor(bond, yld)
        discount_factors = [math.pow(one_period_factor, i + 1) for i in range(len(bond.coupon_payment))]
        cash_flows = bond.coupon_payment.copy()
        cash_flows[-1] += bond.principal
        present_values = [cash_flows[i] * discount_factors[i] for i in range(len(bond.coupon_payment))]

        payment_times = bond.payment_times_in_year

        convexities = [payment_times[i] * present_values[i] * (payment_times[i] + payment_times[0]) * one_period_factor ** 2
                       for i in range(len(bond.payment_times_in_year))]

        return sum(convexities) / sum(present_values)


##########################  some test cases ###################

def _example2():
    pricing_date = date(2021, 1, 1)
    issue_date = date(2021, 1, 1)
    engine = BondCalculator(pricing_date)

    # Example 2
    bond = Bond(issue_date, term=10, day_count=DayCount.DAYCOUNT_30360,
                payment_freq=PaymentFrequency.ANNUAL, coupon=0.05)

    yld = 0.06
    px_bond2 = engine.calc_clean_price(bond, yld)
    print("The clean price of bond 2 is: ", format(px_bond2, '.4f'))
    assert (abs(px_bond2 - 92.640) < 0.01)


def _example3():
    pricing_date = date(2021, 1, 1)
    issue_date = date(2021, 1, 1)
    engine = BondCalculator(pricing_date)

    bond = Bond(issue_date, term=2, day_count=DayCount.DAYCOUNT_30360,
                payment_freq=PaymentFrequency.SEMIANNUAL,
                coupon=0.08)

    yld = 0.06
    px_bond3 = engine.calc_clean_price(bond, yld)
    print("The clean price of bond 3 is: ", format(px_bond3, '.4f'))
    assert (abs(px_bond3 - 103.717) < 0.01)


def _example4():
    # unit tests
    pricing_date = date(2021, 1, 1)
    issue_date = date(2021, 1, 1)
    engine = BondCalculator(pricing_date)

    # Example 4 5Y bond with semi-annual 5% coupon priced at 103.72 should have a yield of 4.168%
    price = 103.72
    bond = Bond(issue_date, term=5, day_count=DayCount.DAYCOUNT_30360,
                payment_freq=PaymentFrequency.SEMIANNUAL, coupon=0.05, principal=100)

    yld = engine.calc_yield(bond, price)

    print("The yield of bond 4 is: ", yld)

    assert (abs(yld - 0.04168) < 0.01)


def _test():
    # basic test cases
    _example2()
    _example3()
    _example4()


if __name__ == "__main__":
    _test()
