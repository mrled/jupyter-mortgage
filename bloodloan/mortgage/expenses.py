"""Monthly expenses"""

import copy
import enum
import logging

from bloodloan.mortgage import mmath
# TODO: This violates my abstraction a bit
from bloodloan.ui import ui


logger = logging.getLogger(__name__)  # pylint: disable=C0103


class MCCalcType(enum.Enum):
    """Determines how the amount of the MonthlyCost is calculated

    DOLLAR_AMOUNT               a raw dollar amount
    SALE_FRACTION               a percentage of the sale price
    VALUE_FRACTION              a percentage of the property's current value
    YEARLY_PRINCIPAL_FRACTION   a percentage of the loan, calculated once per year,
                                and paid monthly
    PROPERTY_TAX_FRACTION       a percentage of the first year of property taxes
    MONTHLY_RENT_FRACTION       a percentage of projected rent received from property
    CAPEX                       the calc property is an MCCapEx
    """
    DOLLAR_AMOUNT = enum.auto()
    SALE_FRACTION = enum.auto()
    VALUE_FRACTION = enum.auto()
    YEARLY_PRINCIPAL_FRACTION = enum.auto()
    PROPERTY_TAX_FRACTION = enum.auto()
    MONTHLY_RENT_FRACTION = enum.auto()
    CAPEX = enum.auto()

    def __str__(self):
        #"""Provide a description for the basis of the calculation"""
        if self is MCCalcType.DOLLAR_AMOUNT:
            return "constant amount"
        elif self is MCCalcType.SALE_FRACTION:
            return "sale fraction"
        elif self is MCCalcType.VALUE_FRACTION:
            return "value fraction"
        elif self is MCCalcType.YEARLY_PRINCIPAL_FRACTION:
            return "BOY remaining principal fraction"
        elif self is MCCalcType.PROPERTY_TAX_FRACTION:
            return "yearly property tax fraction"
        elif self is MCCalcType.MONTHLY_RENT_FRACTION:
            return "rent fraction"
        elif self is MCCalcType.CAPEX:
            return "capex"
        else:
            raise NotImplementedError(f"No description for calculations of type {self}")

    # TODO: Document valid input strings
    @classmethod
    def fromstr(cls, string):
        """Return a new MCCalcType from a string
        """
        if string == '' or string == "constant amount" or string == 'amount':
            return MCCalcType.DOLLAR_AMOUNT
        elif string == 'sale fraction':
            return MCCalcType.SALE_FRACTION
        elif string == 'value fraction':
            return MCCalcType.VALUE_FRACTION
        elif string == 'BOY remaining principal fraction':
            return MCCalcType.YEARLY_PRINCIPAL_FRACTION
        elif string == 'yearly property tax fraction':
            return MCCalcType.PROPERTY_TAX_FRACTION
        elif string == 'rent fraction':
            return MCCalcType.MONTHLY_RENT_FRACTION
        elif string == 'capex':
            return MCCalcType.CAPEX
        else:
            raise ValueError(f"No known MCCalcType of {string}")

class MCCapEx():
    """A capital expenditure

    cost        cost of the item new
    lifespan    lifespan in years of the item
    monthly     monthly cost to put aside to afford it
                (assumes the item is currently brand new)
    """

    # TODO: A way to calculate total cost based on square footage?
    #       Would be very useful for flooring.

    def __init__(self, cost, lifespan):
        self.total = cost
        self.lifespan = lifespan
        self.monthly = cost / lifespan / mmath.MONTHS_IN_YEAR

    def __str__(self):
        return f"{ui.dollar(self.total)} over {self.lifespan} years"

    # TODO: Document the dictionary format
    @classmethod
    def fromdict(cls, dictionary):
        """Return a new MonthlyCost from a dictionary
        """
        return cls(
            dictionary['cost'],
            dictionary['lifespan'],
        )


class MonthlyCost():
    """A single monthly cost line item

    (All monthly costs are fees;
    monthly costs do not include mortgage payments of principal and interest)

    Properties:
    label:          an arbitrary text label
    value           the value to be paid, expressed in dollars
    calc            how the value amount is calculated
                    for DOLLAR_AMOUNT, this is empty; for other calculation
                    types, it may be a percentage or something else; see
                    CCCalcType for more information
    calctype        how the value is to be interpreted
                    should be a MCCalcType or MCCapEx
    """

    def __init__(
            self,
            label=None,
            value=None,
            calc=None,
            calctype=MCCalcType.DOLLAR_AMOUNT):
        self.label = label
        self.value = value
        self.calc = calc
        self.calctype = calctype

    @property
    def calcstr(self):
        """A nice string to explain how the calculation is done"""
        if self.calctype is MCCalcType.DOLLAR_AMOUNT:
            return self.calctype
        elif self.calctype is MCCalcType.CAPEX:
            return self.calc
        else:
            return f"{ui.percent(self.calc)} of {str(self.calctype)}"

    def __str__(self):
        return f"{self.label} - ${self.value} ({self.calcstr})"

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
            calctype = MCCalcType.fromstr(dictionary['calculation type'])
        except KeyError:
            calctype = MCCalcType.DOLLAR_AMOUNT

        return MonthlyCost(label=label, value=value, calc=calc, calctype=calctype)

    # TODO: Document the dictionary format
    @classmethod
    def capexfromdict(cls, dictionary):
        """Return a new MonthlyCost from a dictionary
        """
        return MonthlyCost(
            label=dictionary['label'],
            calc=MCCapEx.fromdict(dictionary),
            calctype=MCCalcType.CAPEX,
        )


def monthly_expenses(costs, saleprice, propvalue, boyprincipal, rent):
    """Calculate monthly expenses

    costs           list of MonthlyCost objects
    saleprice       sale price of the property
    propvalue       actual value of the property
    boyprincipal    principal at beginning of year to calculate for
    rent            projected monthly rent for the property
    """
    expenses = []

    if not costs:
        return expenses

    # deepcopy the costs during *every* iteration,
    # or else we keep doing expenses.append(cost) on the same cost each time
    for cost in copy.deepcopy(costs):

        # First, check our inputs
        if cost.calctype == MCCalcType.DOLLAR_AMOUNT and cost.value is None:
            raise Exception(
                f"The {cost.label} MonthlyCost calctype is DOLLAR_AMOUNT, "
                "but with an empty value property")
        elif cost.calctype is not MCCalcType.DOLLAR_AMOUNT and cost.calc is None:
            raise Exception(
                f"The {cost.label} MonthlyCost calctype is {cost.calctype}, "
                "but with an empty calc property")

        # Now calculate what can be calculated now
        # Don't calculate LOAN_FRACTION or INTEREST_MONTHS calctypes here,
        # because any PRINCIPAL paytypes will affect their value
        if cost.calctype is MCCalcType.DOLLAR_AMOUNT:
            pass
        elif cost.calctype is MCCalcType.YEARLY_PRINCIPAL_FRACTION:
            fraction = mmath.percent2decimal(cost.calc)
            cost.value = boyprincipal * fraction / mmath.MONTHS_IN_YEAR
        elif cost.calctype is MCCalcType.SALE_FRACTION:
            cost.value = saleprice * mmath.percent2decimal(cost.calc)
        elif cost.calctype is MCCalcType.VALUE_FRACTION:
            cost.value = propvalue * mmath.percent2decimal(cost.calc)
        elif cost.calctype is MCCalcType.MONTHLY_RENT_FRACTION:
            cost.value = rent * mmath.percent2decimal(cost.calc)
        elif cost.calctype is MCCalcType.CAPEX:
            cost.value = cost.calc.monthly
        else:
            raise NotImplementedError(
                f"Cannot process a cost with a calctype of {cost.calctype}")

        logger.info(f"Calculating monthy expense: {cost}")
        expenses.append(cost)

    return expenses
