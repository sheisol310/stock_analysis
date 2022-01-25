"""

@project       : Queens College CSCI 365/765 Computational Finance
@Instructor    : Dr. Alex Pang

@Group Name    : Group 7
@Student Name  : Weifeng Zhao
                 Ching Kung Lin
                 Jianhui Chen

@Date          : Fall 2021

A Simplified Bond Class

"""

import math
import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta

import enum
import calendar

from datetime import date


class DayCount(enum.Enum):
    DAYCOUNT_30360 = "30/360"
    DAYCOUNT_ACTUAL_360 = "Actual/360"
    DAYCOUNT_ACTUAL_ACTUAL = "Actual/Actual"


class PaymentFrequency(enum.Enum):
    ANNUAL = "Annual"
    SEMIANNUAL = "Semi-annual"
    QUARTERLY = "Quarterly"
    MONTHLY = "Monthly"
    CONTINUOUS = "Continuous"


class Bond(object):
    """
    term is maturity term in years
    coupon is the coupon in fraction (decimal) eg 5% should be expressed as 0.05
    maturity date will be issue_date + term
    """

    def __init__(self, issue_date, term, day_count, payment_freq, coupon, principal=100):
        self.issue_date = issue_date
        self.term = term
        self.day_count = day_count
        self.payment_freq = payment_freq
        self.coupon = coupon
        self.principal = principal
        # internal data structures
        self.payment_times_in_year = []
        self.payment_dates = []
        self.coupon_payment = []
        self._calc()

    def _add_months(self, dt, n_months):
        # helper method to add n_months to date dt
        return (dt + relativedelta(months=n_months))

    def _calc(self):
        # calculate maturity date
        self.maturity_date = self._add_months(self.issue_date, 12 * self.term)

        # calculate all the payment dates
        dt = self.issue_date
        while dt < self.maturity_date:
            if self.payment_freq == PaymentFrequency.ANNUAL:
                next_dt = self._add_months(dt, 12)
            elif self.payment_freq == PaymentFrequency.SEMIANNUAL:
                next_dt = self._add_months(dt, 6)
            elif self.payment_freq == PaymentFrequency.QUARTERLY:
                next_dt = self._add_months(dt, 4)
            elif self.payment_freq == PaymentFrequency.MONTHLY:
                next_dt = self._add_months(dt, 1)
            else:
                raise Exception("Unsupported Payment frequency")

            if next_dt <= self.maturity_date:
                self.payment_dates.append(next_dt)

            dt = next_dt

        # calculate the future cashflow vectors
        if self.payment_freq == PaymentFrequency.ANNUAL:
            coupon_cf = self.principal * self.coupon
        elif self.payment_freq == PaymentFrequency.SEMIANNUAL:
            coupon_cf = self.principal * self.coupon / 2
        elif self.payment_freq == PaymentFrequency.QUARTERLY:
            coupon_cf = self.principal * self.coupon / 4
        elif self.payment_freq == PaymentFrequency.MONTHLY:
            coupon_cf = self.principal * self.coupon / 12
        else:
            raise Exception("Unsupported Payment frequency")

        self.coupon_payment = [coupon_cf for i in range(len(self.payment_dates))]

        # calculate payment_time in years
        if self.payment_freq == PaymentFrequency.ANNUAL:
            period = 1
        elif self.payment_freq == PaymentFrequency.SEMIANNUAL:
            period = 1 / 2
        elif self.payment_freq == PaymentFrequency.QUARTERLY:
            period = 1 / 4
        elif self.payment_freq == PaymentFrequency.MONTHLY:
            period = 1 / 12
        else:
            raise Exception("Unsupported Payment frequency")

        self.payment_times_in_year = [period * (i + 1) for i in range(len(self.payment_dates))]

    def get_next_payment_date(self, as_of_date):
        """
        return the next payment date after as_of_date
        """
        if as_of_date <= self.issue_date:
            return (self.payment_dates[0])
        elif as_of_date > self.payment_dates[-1]:
            return (None)
        else:
            i = 0
            while i < len(self.payment_dates):
                dt = self.payment_dates[i]
                if as_of_date <= dt:
                    return (dt)
                else:
                    i += 1
            return (None)

    def get_previous_payment_date(self, as_of_date):
        """
        return the previous payment date before as_of_date if as_of_date is after the first pay date
        if it is before first pay date, return the issue date
        """
        if as_of_date < self.issue_date:
            return (None)
        elif as_of_date < self.payment_dates[0]:
            return (self.issue_date)
        else:
            i = 1
            while i < len(self.payment_dates):
                dt = self.payment_dates[i]
                if as_of_date <= dt:
                    return (self.payment_dates[i - 1])
                else:
                    i += 1
            return (None)


def _example2():
    # Example 2 from the class
    issue_date = date(2021, 1, 1)
    bond = Bond(issue_date, term=10, day_count=DayCount.DAYCOUNT_30360,
                payment_freq=PaymentFrequency.ANNUAL, coupon=0.05, principal=1000)

    print("Example 2 of a 10Y bond with 5% coupon annual compounding frequency")
    print("Issue Date", bond.issue_date)
    print("Maturity Date", bond.maturity_date)
    print("Payment Dates:", bond.payment_dates)
    print("Coupon Payment:", bond.coupon_payment)
    print("Payment time in year:", bond.payment_times_in_year)


def _example3():
    # Example 3 from the class
    issue_date = date(2021, 1, 1)
    bond = Bond(issue_date, term=2, day_count=DayCount.DAYCOUNT_30360,
                payment_freq=PaymentFrequency.SEMIANNUAL, coupon=0.08, principal=1000)

    print("Example 3 of a 2Y bond with 5% coupon and semi-annual compounding frequency")
    print("Issue Date", bond.issue_date)
    print("Maturity Date", bond.maturity_date)
    print("Payment Dates:", bond.payment_dates)
    print("Coupon Payment:", bond.coupon_payment)
    print("Payment time in year:", bond.payment_times_in_year)


def _test():
    # unit test
    _example2()
    _example3()


if __name__ == "__main__":
    _test()
