#!/usr/bin/env python3

"""Mortgage calculations"""

import copy
from enum import Enum, auto

import util
from log import LOG as log


MONTHS_IN_YEAR = 12
DAYS_IN_MONTH_APPROX = 30


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


# Use the actual formula
# I haven't figured out a way to incorporate overpayments into the formula
# https://en.wikipedia.org/wiki/Mortgage_calculator#Monthly_payment_formula
def balance_after(interestrate, principal, term, month):
    """The principal balance after N months of on-time patyments of *only* the monthly_payment

    interestrate    yearly interest rate of the loan
    principal       total amount of the loan
    term            loan term in months
    month           the month to calculate from
    """
    mrate = monthlyrate(interestrate)
    mpay = monthly_payment(interestrate, principal, term)
    return (1 + mrate)**month * principal - ((1 + mrate)**month - 1) / mrate * mpay


# Had to change this from a named tuple because a named tuple is immutable
class LoanPayment:
    """A single loan payment and its result"""

    def __init__(
            self,
            index=0,
            totalpmt=0,
            interestpmt=0,
            balancepmt=0,
            overpmt=0,
            principal=0,
            value=0,
            equity=0,
            totalinterest=0):
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
def schedule(interestrate, value, principal, term, overpayments=None, appreciation=0):
    """A schedule of payments, including overpayments

    interestrate    yearly interest rate of the loan
    principal       total amount of the loan
    term            loan term in months
    overpayments    array of overpayment amounts for each month in the term
    appreciation    appreciation in decimal value representing percent
    """
    overpayments = overpayments or []
    mpay = monthly_payment(interestrate, principal, term)
    monthidx = 0
    totalinterest = 0
    while principal > 0:
        interestpmt = principal * monthlyrate(interestrate)
        totalinterest += interestpmt
        balancepmt = mpay - interestpmt
        try:
            overpmt = overpayments[monthidx]
        except IndexError:
            overpmt = 0

        if principal <= 0:
            # Break before the yield so we don't get empty lines
            log.info(f"#{monthidx}: Principal {principal} is <= 0 in final month")
            break
        elif principal < 0.01:
            # Also break if the principal is less than a cent
            # This prevents a weird payment that looks like it's for $0,
            # but actually is a rounded-down fraction of a cent
            log.info(
                f"#{monthidx}: Ignoring remaining principal of {principal} "
                "because it is a fraction of a cent in final month")
            break
        elif principal - balancepmt - overpmt <= 0:
            # Paying the normal amount will result in overpaying in the final month
            # Handle this by adjusting the balancepmt and overpmt
            if principal - balancepmt > 0:
                log.info(f"#{monthidx}: Truncating overpayment to {overpmt} in final month")
                overpmt = principal - balancepmt
                principal = 0
            elif balancepmt > principal:
                log.info(f"#{monthidx}: Truncating balance payment to {balancepmt} in final month")
                overpmt = 0
                balancepmt = principal
                principal = 0
            else:
                raise Exception("This should not happen")
        else:
            log.debug(f"#{monthidx}: Paying normal amounts in non-final month")
            principal = principal - balancepmt - overpmt

        monthapprec = appreciation / MONTHS_IN_YEAR
        value = value * (1 + monthapprec)

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


class CCCalcType(Enum):
    """Determines how the amount of the ClosingCost is calculated

    DOLLAR_AMOUNT           a raw dollar amount
    SALE_FRACTION           a percentage of the sale price
    LOAN_FRACTION           a percentage of the loan
    INTEREST_MONTHS         a number representing months (or a month fraction)
                            of interest to be paid in advance
    PROPERTY_TAX_FRACTION   a percentage of the first year of property taxes
    """
    DOLLAR_AMOUNT = auto()
    SALE_FRACTION = auto()
    LOAN_FRACTION = auto()
    INTEREST_MONTHS = auto()
    PROPERTY_TAX_FRACTION = auto()


class CCPayType(Enum):
    """Determines how the ClosingCost will be paid

    PRINCIPAL       added to the total amount of the loan
    DOWN_PAYMENT    the down payment (probably there is just one)
    FEE             fees owed to other parties
    """
    PRINCIPAL = auto()
    DOWN_PAYMENT = auto()
    FEE = auto()


class ClosingCost():
    """A single closing cost line item

    Properties:
    label:          an arbitrary text label
    value           the value to be paid, expressed in dollars
    calc            how the value amount is calculated
                    for DOLLAR_AMOUNT, this is empty; for other calculation
                    types, it may be a percentage or something else; see
                    CCCalcType for more information
    calctype        how the value is to be interpreted
                    should be a CCCalcType
    paytype         how the payment is applied
                    should be a CCPayType
    """

    def __init__(
            self,
            label=None,
            value=None,
            calc=None,
            calctype=CCCalcType.DOLLAR_AMOUNT,
            paytype=CCPayType.FEE):
        self.label = label
        self.value = value
        self.calc = calc
        self.calctype = calctype
        self.paytype = paytype

    def __repr__(self):
        return f"{self.label} - {self.value} ({self.paytype.name})"


IRONHARBOR_FHA_CLOSING_COSTS = [
    ClosingCost(
        "Down payment",
        calc=3.5,
        calctype=CCCalcType.SALE_FRACTION,
        paytype=CCPayType.DOWN_PAYMENT),
    ClosingCost(
        "Upfront FHA mortgage insurance",
        calc=1.75,
        calctype=CCCalcType.LOAN_FRACTION,
        paytype=CCPayType.PRINCIPAL),
    ClosingCost(
        "Prepaid interest (est 15 days)",
        calc=0.5,
        calctype=CCCalcType.INTEREST_MONTHS,
        paytype=CCPayType.FEE),
    ClosingCost(
        "Taxes escrow (3 months)",
        calc=0.25,
        calctype=CCCalcType.PROPERTY_TAX_FRACTION,
        paytype=CCPayType.FEE),

    # The broker will give origination options to the buyer, which affect the
    # interest rate
    # The buyer might choose to pay a higher fee with a lower interest rate,
    # or instead a negative fee (aka cash in hand) for a higher interest rate
    ClosingCost("Origination points", 0),

    ClosingCost("Flat lender fee", 600),
    ClosingCost("Appraisal", 495),
    ClosingCost("Lender attorney", 150),
    ClosingCost("Tax service", 72),
    ClosingCost("Credit reports/supplements", 150),
    ClosingCost("Title lenders and endorsements", 443),
    ClosingCost("Title closing/courier fee", 450),
    ClosingCost("County recording", 175),
    ClosingCost("Estimated prepaid insurance (1 year)", 1440),
    ClosingCost("Insurance escrow (3 months)", 360),
]


class CloseResult:
    """The result of a close() function call"""

    def __init__(self, saleprice=0, downpayment=None, fees=None, principal=None):
        self.saleprice = saleprice
        self.downpayment = downpayment or []
        self.fees = fees or []
        self.principal = principal or []

    def sum(self, costs):
        """Sum up costs"""
        total = 0
        for cost in costs:
            total += cost.value
        return total

    @property
    def downpayment_total(self):
        """Total downpayment"""
        return self.sum(self.downpayment)

    @property
    def fees_total(self):
        """Total fees"""
        return self.sum(self.fees)

    @property
    def principal_total(self):
        """Total principal"""
        return self.sum(self.principal)

    def apply(self, cost):
        """Add a ClosingCost"""
        log.info(f"Closing cost: {cost}")

        if cost.paytype == CCPayType.PRINCIPAL:
            self.principal.append(cost)

        elif cost.paytype == CCPayType.DOWN_PAYMENT:
            self.downpayment.append(cost)
            principalvalue = self.saleprice - cost.value
            self.principal.append(ClosingCost(
                "Principal",
                value=principalvalue,
                paytype=CCPayType.PRINCIPAL))

        elif cost.paytype == CCPayType.FEE:
            self.fees.append(cost)

        else:
            raise Exception(f"Unknown paytype {cost.paytype}")


def close(saleprice, interestrate, loanterm, propertytaxes, costs):
    """Calculate loan amount and closing costs

    saleprice       sale price for the property
    interestrate    interest rate for the loan
    loanterm        loan term in months
    propertytaxes   estimated property taxes
    costs           list of ClosingCost objects
    """

    result = CloseResult(saleprice=saleprice)

    # Don't modify costs we were passed, in case they are reused elsewhere
    costs = copy.deepcopy(costs)

    # BEWARE!
    # ORDER IS IMPORTANT AND SUBTLE!

    for cost in costs:
        # First, check our inputs
        if cost.calctype == CCCalcType.DOLLAR_AMOUNT and cost.value is None:
            raise Exception(
                f"The {cost.label} ClosingCost calctype is DOLLAR_AMOUNT, "
                "but with an empty value property")
        elif cost.calctype != CCCalcType.DOLLAR_AMOUNT and cost.calc is None:
            raise Exception(
                f"The {cost.label} ClosingCost calctype is {cost.calctype}, "
                "but with an empty calc property")

        # Now calculate what can be calculated now
        # Don't calculate LOAN_FRACTION or INTEREST_MONTHS calctypes here,
        # because any PRINCIPAL paytypes will affect their value
        if cost.calctype == CCCalcType.DOLLAR_AMOUNT:
            result.apply(cost)
        if cost.calctype == CCCalcType.SALE_FRACTION:
            cost.value = saleprice * util.percent2decimal(cost.calc)
            result.apply(cost)
        elif cost.calctype == CCCalcType.PROPERTY_TAX_FRACTION:
            cost.value = propertytaxes * util.percent2decimal(cost.calc)
            result.apply(cost)

    for cost in costs:
        # Now that we have calculated the other costs, including loan amount,
        # we can calculate LOAN_FRACTION or INTEREST_MONTHS calctypes
        # Note that theoretically you could have something weird like a cost of
        # calctype=LOAN_FRACTION paytype=PRINCIPAL,
        # but that wouldn't make much sense so we don't really handle it here
        if cost.calctype == CCCalcType.LOAN_FRACTION:
            cost.value = result.principal_total * util.percent2decimal(cost.calc)
            result.apply(cost)
        elif cost.calctype == CCCalcType.INTEREST_MONTHS:
            # This is not a perfect way to do this calculation.
            # This way assumes interest is the same in all months, which is not
            # the case. However, we don't expect to get an INTEREST_MONTHS cost
            # that is many months long, so we just assume here that the first
            # month's interest is a good estimate of subsequent months'.
            firstmonth = None
            for month in schedule(interestrate, saleprice, result.principal_total, loanterm):
                firstmonth = month
                break
            cost.value = firstmonth.interestpmt * cost.calc
            result.apply(cost)

    return result
