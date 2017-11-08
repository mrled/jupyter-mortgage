"""Closing costs"""

import copy
import enum

from ..log import LOG as log
from .mmath import *
from .schedule import *


class CCCalcType(enum.Enum):
    """Determines how the amount of the ClosingCost is calculated

    DOLLAR_AMOUNT           a raw dollar amount
    SALE_FRACTION           a percentage of the sale price
    LOAN_FRACTION           a percentage of the loan
    INTEREST_MONTHS         a number representing months (or a month fraction)
                            of interest to be paid in advance
    PROPERTY_TAX_FRACTION   a percentage of the first year of property taxes
    """
    DOLLAR_AMOUNT = enum.auto()
    SALE_FRACTION = enum.auto()
    LOAN_FRACTION = enum.auto()
    INTEREST_MONTHS = enum.auto()
    PROPERTY_TAX_FRACTION = enum.auto()


class CCPayType(enum.Enum):
    """Determines how the ClosingCost will be paid

    PRINCIPAL       added to the total amount of the loan
    DOWN_PAYMENT    the down payment (probably there is just one)
    FEE             fees owed to other parties
    """
    PRINCIPAL = enum.auto()
    DOWN_PAYMENT = enum.auto()
    FEE = enum.auto()


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
            cost.value = saleprice * percent2decimal(cost.calc)
            result.apply(cost)
        elif cost.calctype == CCCalcType.PROPERTY_TAX_FRACTION:
            cost.value = propertytaxes * percent2decimal(cost.calc)
            result.apply(cost)

    for cost in costs:
        # Now that we have calculated the other costs, including loan amount,
        # we can calculate LOAN_FRACTION or INTEREST_MONTHS calctypes
        # Note that theoretically you could have something weird like a cost of
        # calctype=LOAN_FRACTION paytype=PRINCIPAL,
        # but that wouldn't make much sense so we don't really handle it here
        if cost.calctype == CCCalcType.LOAN_FRACTION:
            cost.value = result.principal_total * percent2decimal(cost.calc)
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
