"""Closing costs"""

import copy
import enum
import logging

from bloodloan.mortgage import mmath
from bloodloan.mortgage import schedule


logger = logging.getLogger(__name__)  # pylint: disable=C0103


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

    # TODO: Document valid input strings
    @classmethod
    def fromstr(cls, string):
        """Return a new instance from a string
        """
        if string == '' or string == 'amount':
            return cls.DOLLAR_AMOUNT
        elif string == 'sale fraction':
            return cls.SALE_FRACTION
        elif string == 'loan fraction':
            return cls.LOAN_FRACTION
        elif string == 'months of interest':
            return cls.INTEREST_MONTHS
        elif string == 'yearly property tax fraction':
            return cls.PROPERTY_TAX_FRACTION
        else:
            raise ValueError(f"No known CCCalcType type of {string}")


class CCPayType(enum.Enum):
    """Determines how the ClosingCost will be paid

    PRINCIPAL       added to the total amount of the loan
    DOWN_PAYMENT    the down payment (probably there is just one)
    FEE             fees owed to other parties
    """
    PRINCIPAL = enum.auto()
    DOWN_PAYMENT = enum.auto()
    FEE = enum.auto()

    # TODO: Document valid input strings
    @classmethod
    def fromstr(cls, string):
        """Return a new instance from a string
        """
        if string == '' or string == 'fee':
            return cls.FEE
        elif string == 'downpayment':
            return cls.DOWN_PAYMENT
        elif string == 'principal':
            return cls.PRINCIPAL
        else:
            raise ValueError(f"No known CCPayType type of {string}")


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

    def __str__(self):
        return f"{self.label} - {self.value} ({self.paytype.name})"

    def __repr__(self):
        return str(self)

    # TODO: Document the dictionary format
    @classmethod
    def fromdict(cls, dictionary):
        """Return a new MonthlyCost from a dictionary
        """
        label = dictionary['label']
        value = dictionary['value'] if 'value' in dictionary else None
        calc = dictionary['calculation'] if 'calculation' in dictionary else None

        try:
            calctype = CCCalcType.fromstr(dictionary['calculation type'])
        except KeyError:
            calctype = CCCalcType.DOLLAR_AMOUNT

        try:
            paytype = CCPayType.fromstr(dictionary['payment type'])
        except KeyError:
            paytype = CCPayType.FEE

        return cls(label=label, value=value, calc=calc, calctype=calctype, paytype=paytype)


class CloseResult:
    """The result of a close() function call"""

    def __init__(self, saleprice=0, downpayment=None, fees=None, principal=None):
        self.saleprice = saleprice
        self.downpayment = downpayment or []
        self.fees = fees or []
        self.principal = principal or []
        self.principal.append(ClosingCost(
            "Sale price",
            value=saleprice,
            paytype=CCPayType.PRINCIPAL))

    def __str__(self):
        return ", ".join([
            f"<CloseResult: Price ${self.saleprice}",
            f"Down ${self.downpayment_total} ({len(self.downpayment)})",
            f"Fees ${self.fees_total} ({len(self.fees)})",
            f"Principal ${self.principal_total} ({len(self.principal)})>",
        ])

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

    def sum(self, costs):
        """Sum up costs"""
        total = 0
        for cost in costs:
            total += cost.value
        return total

    def apply(self, cost):
        """Add a ClosingCost"""
        logger.info(f"Closing cost: {cost}")

        if cost.paytype == CCPayType.PRINCIPAL:
            self.principal.append(cost)

        elif cost.paytype == CCPayType.DOWN_PAYMENT:
            self.downpayment.append(cost)
            self.principal.append(ClosingCost(
                "Down payment",
                value=-cost.value,
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
            cost.value = saleprice * mmath.percent2decimal(cost.calc)
            result.apply(cost)
        elif cost.calctype == CCCalcType.PROPERTY_TAX_FRACTION:
            cost.value = propertytaxes * mmath.percent2decimal(cost.calc)
            result.apply(cost)

    for cost in costs:
        # Now that we have calculated the other costs, including loan amount,
        # we can calculate LOAN_FRACTION or INTEREST_MONTHS calctypes
        # Note that theoretically you could have something weird like a cost of
        # calctype=LOAN_FRACTION paytype=PRINCIPAL,
        # but that wouldn't make much sense so we don't really handle it here
        if cost.calctype == CCCalcType.LOAN_FRACTION:
            cost.value = result.principal_total * mmath.percent2decimal(cost.calc)
            result.apply(cost)
        elif cost.calctype == CCCalcType.INTEREST_MONTHS:
            # TODO: Improve INTEREST_MONTHS closing cost calculation
            # 1)    Assumes interest is the same in all months (not true)
            #       OK because we don't expect INTEREST_MONTHS to be many months long
            # 2)    Assumes saleprice == value
            #       OK for now but should be fixed at some point
            monthgen = schedule.schedule(
                interestrate, saleprice, result.principal_total, saleprice, loanterm)
            firstmonth = next(monthgen)
            cost.value = firstmonth.interestpmt * cost.calc
            result.apply(cost)

    return result
