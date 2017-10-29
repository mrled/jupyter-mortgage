#!/usr/bin/env python3

"""Mortgage calculations"""

import collections

MONTHS_IN_YEAR = 12

def dollar(amount):
    """Return a string dollar amount from a float

    For example, dollar(1926.2311831442486) => "$1,926.23"

    We aren't too concerned about the lost accuracy;
    this function should only be used for *display* values
    """
    return '${:,.2f}'.format(amount)

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

# A type to represent a month's payment and its result
MonthInSchedule = collections.namedtuple('MonthInSchedule', ['index', 'interestpmt', 'balancepmt', 'overpmt', 'principal'])

# Rather than using the formula to calculate principal balance,
# do it by brute-force
# (I guess if I remembered calculus better,
# I'd be able to use a calculus formula instead)
# Incorporates overpayments
def schedule(apryearly, principal, term, overpayments=[]):
    """A schedule of payments, including overpayments

    apryearly:      yearly APR of the loan
    principal:      total amount of the loan
    term:           loan term in months
    overpayments:   array of overpayment amounts for each month in the term
    """
    mapr = aprmonthly(apryearly)
    mpay = monthly_payment(apryearly, principal, term)
    monthidx = 0
    while principal > 0:
        interestpmt = principal * mapr
        balancepmt = mpay - interestpmt
        try:
            overpmt = overpayments[monthidx]
        except IndexError:
            overpmt = 0
        principal = principal - balancepmt - overpmt

        yield MonthInSchedule(
            index=monthidx,
            interestpmt=interestpmt,
            balancepmt=balancepmt,
            overpmt=overpmt,
            principal=principal)

        monthidx += 1

def htmlschedule(apryearly, principal, term, overpayment=0):
    """Create an HTML table of a loan schedule

    apryearly:      yearly APR of the loan
    principal:      total amount of the loan
    term:           loan term in months
    overpayment:    an extra amount to apply to *every* month's loan principal
    """

    mpay = monthly_payment(apryearly, principal, term)

    htmlstr  = "<h1>Mortgage amortization schedule</h1>"
    htmlstr += "<p>"
    htmlstr += f"Amortization schedule for a {principal} loan "
    htmlstr += f"over {term} months "
    htmlstr += f"at {apryearly}% interest, "
    htmlstr += f"including a {dollar(overpayment)} overpayment each month."
    htmlstr += "</p>"

    htmlstr += "<table>"

    htmlstr += "<tr>"
    htmlstr += "<th>Month</th>"
    htmlstr += "<th>Regular payment</th>"
    htmlstr += "<th>Interest</th>"
    htmlstr += "<th>Balance</th>"
    htmlstr += "<th>Overpayment</th>"
    htmlstr += "<th>Remaining principal</th>"
    htmlstr += "</tr> "

    htmlstr += "<tr>"
    htmlstr += "<td>Initial loan amount</td>"
    htmlstr += "<td></td>"
    htmlstr += "<td></td>"
    htmlstr += "<td></td>"
    htmlstr += "<td></td>"
    htmlstr += f"<td>{dollar(principal)}</td>"
    htmlstr += "</tr> "

    for month in schedule(apryearly, principal, term, [overpayment for _ in range(term)]):
        htmlstr += "<tr>"
        htmlstr += f"<td>{month.index}</td>"
        htmlstr += f"<td>{dollar(mpay)}</td>"
        htmlstr += f"<td>{dollar(month.interestpmt)}</td>"
        htmlstr += f"<td>{dollar(month.balancepmt)}</td>"
        htmlstr += f"<td>{dollar(month.overpmt)}</td>"
        htmlstr += f"<td>{dollar(month.principal)}</td>"
        htmlstr += "</tr> "

    htmlstr += "</table>"

    return htmlstr
