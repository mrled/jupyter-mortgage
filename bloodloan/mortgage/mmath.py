"""Generic mortgage-related math"""

MONTHS_IN_YEAR = 12
DAYS_IN_MONTH_APPROX = 30


def percent2decimal(percent):
    """Take a percentage, such as 3.5, and convert it to a decimal, such as 0.035"""
    return percent / 100


def decimal2percent(decimal):
    """Take a decimal, such as 0.035, and convert it to a percentage, such as 3.5"""
    return decimal * 100


def monthlyrate(interestrate):
    """The monthly interest rate, as calculated from the yearly interest rate"""
    return interestrate / MONTHS_IN_YEAR


# https://en.wikipedia.org/wiki/Mortgage_calculator#Monthly_payment_formula
def monthly_payment(interestrate, principal, term):
    """The monthly mortgage payment amount

    interestrate    yearly interest rate of the loan
    principal       total amount of the loan
    term            loan term in months
    """
    mrate = monthlyrate(interestrate)
    return mrate * principal / (1 - (1 + mrate)**(-term))
