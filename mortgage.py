#!/usr/bin/env python3

"""Mortgage calculations"""

import collections

import util

MONTHS_IN_YEAR = 12

def monthlyrate(apryearly):
    """The monthly rate, as calculated from the yearly APR

    I'm not honestly clear on what this *is*,
    or the difference betweenit and the "monthly APR" below,
    or if I'm even using the right terms for these,
    but it's required for the way my existing spreadsheet
    calculates principal balance after overpayment
    """
    return apryearly / MONTHS_IN_YEAR

def aprmonthly(apryearly):
    """The monthly APR, as calculated from the yearly APR"""
    return apryearly / MONTHS_IN_YEAR / 100

# https://en.wikipedia.org/wiki/Mortgage_calculator#Monthly_payment_formula
def monthly_payment(apryearly, principal, term):
    """The monthly mortgage payment amount

    apryearly:  yearly APR of the loan
    principal:  total amount of the loan
    term:       loan term in months
    """
    mapr = aprmonthly(apryearly)
    return mapr * principal / (1 - (1 + mapr)**(-term))

# Use the actual formula
# I haven't figured out a way to incorporate overpayments into the formula
# https://en.wikipedia.org/wiki/Mortgage_calculator#Monthly_payment_formula
def balance_after(apryearly, principal, term, month):
    """The principal balance after N months of on-time patyments of *only* the monthly_payment

    apryearly:  yearly APR of the loan
    principal:  total amount of the loan
    term:       loan term in months
    month:      the month to calculate from
    """
    mapr = aprmonthly(apryearly)
    mpay = monthly_payment(apryearly, principal, term)
    return (1 + mapr)**month * principal - ((1 + mapr)**month - 1) / mapr * mpay


# Had to change this from a named tuple because a named tuple is immutable
class LoanPayment:
    """A single loan payment and its result"""

    index = 0
    totalpmt = 0
    interestpmt = 0
    balancepmt = 0
    overpmt = 0
    principal = 0
    value = 0
    equity = 0
    totalinterest = 0

    def __init__(self, index=0, totalpmt=0, interestpmt=0, balancepmt=0, overpmt=0, principal=0, value=0, equity=0, totalinterest=0):
        self.index = index
        self.totalpmt = totalpmt
        self.interestpmt = interestpmt
        self.balancepmt = balancepmt
        self.overpmt = overpmt
        self.principal = principal
        self.value = value
        self.equity = equity
        self.totalinterest = totalinterest


# Rather than using the formula to calculate principal balance,
# do it by brute-force
# (I guess if I remembered calculus better,
# I'd be able to use a calculus formula instead)
# Incorporates overpayments
def schedule(apryearly, principal, term, overpayments=None, appreciation=0):
    """A schedule of payments, including overpayments

    apryearly:      yearly APR of the loan
    principal:      total amount of the loan
    term:           loan term in months
    overpayments:   array of overpayment amounts for each month in the term
    appreciation:   appreciation in decimal value representing percent
    """
    logger = util.getlogger()
    overpayments = overpayments or []
    mapr = aprmonthly(apryearly)
    mpay = monthly_payment(apryearly, principal, term)
    monthidx = 0
    value = principal
    totalinterest = 0
    while principal > 0:
        interestpmt = principal * mapr
        totalinterest += interestpmt
        balancepmt = mpay - interestpmt
        try:
            overpmt = overpayments[monthidx]
        except IndexError:
            overpmt = 0

        if principal <= 0:
            # Break before the yield so we don't get empty lines
            logger.info(f"schedule()[{monthidx}]: Principal {principal} is <= 0 in final month")
            break
        elif principal < 0.01:
            # Also break if the principal is less than a cent
            # This prevents a weird payment that looks like it's for $0,
            # but actually is a rounded-down fraction of a cent
            logger.info(f"schedule()[{monthidx}]: Ignoring remaining principal of {principal} because it is a fraction of a cent in final month")
            break
        elif principal - balancepmt - overpmt <= 0:
            # Paying the normal amount will result in overpaying in the final month
            # Handle this by adjusting the balancepmt and overpmt
            if principal - balancepmt > 0:
                logger.info(f"schedule()[{monthidx}]: Truncating overpayment to {overpmt} in final month")
                overpmt = principal - balancepmt
                principal = 0
            elif balancepmt > principal:
                logger.info(f"schedule()[{monthidx}]: Truncating balance payment to {balancepmt} in final month")
                overpmt = 0
                balancepmt = principal
                principal = 0
            else:
                raise Exception("This should not happen")
        else:
            logger.info(f"schedule()[{monthidx}]: Paying normal amounts in non-final month")
            principal = principal - balancepmt - overpmt

        if not monthidx == 0:
            if monthidx % MONTHS_IN_YEAR == 0:
                value = value * (1 + appreciation)

        yield LoanPayment(
            index=monthidx,
            totalpmt=interestpmt + balancepmt + overpmt,
            interestpmt=interestpmt,
            balancepmt=balancepmt,
            overpmt=overpmt,
            principal=principal,
            value=value,
            equity=value - principal,
            totalinterest=totalinterest)

        monthidx += 1


def monthly2yearly_schedule(months):
    """Convert a monthly schedule to a yearly one

    months: array of LoanPayment objects
    """
    year = None
    idx = 0
    for month in months:
        if idx % MONTHS_IN_YEAR == 0:
            if year:
                yield year
                newyearidx = year.index + 1
            else:
                newyearidx = 0
            year = LoanPayment(
                index=newyearidx,
                totalpmt=month.totalpmt,
                interestpmt=month.interestpmt,
                balancepmt=month.balancepmt,
                overpmt=month.overpmt,
                principal=month.principal)
        else:
            # Adds:
            year.totalpmt += month.totalpmt
            year.interestpmt += month.interestpmt
            year.balancepmt += month.balancepmt
            year.overpmt += month.overpmt
            # Overwrites:
            year.principal = month.principal
            year.value = month.value
            year.equity = month.equity
            year.totalinterest = month.totalinterest
        idx += 1
    yield year
