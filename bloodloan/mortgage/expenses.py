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
            return "constant dollar amount"
        elif self is MCCalcType.SALE_FRACTION:
            return "sale price"
        elif self is MCCalcType.VALUE_FRACTION:
            return "property value"
        elif self is MCCalcType.YEARLY_PRINCIPAL_FRACTION:
            return "BOY remaining principal"
        elif self is MCCalcType.PROPERTY_TAX_FRACTION:
            return "property tax"
        elif self is MCCalcType.MONTHLY_RENT_FRACTION:
            return "monthly rent"
        elif self is MCCalcType.CAPEX:
            return "capital expenditure"
        else:
            raise NotImplementedError(f"No description for calculations of type {self}")


class MCCapEx():
    """A capital expenditure

    cost        cost of the item new
    lifespan    lifespan in years of the item
    monthly     monthly cost to put aside to afford it
                (assumes the item is currently brand new)
    """

    def __init__(self, cost, lifespan):
        self.total = cost
        self.lifespan = lifespan
        self.monthly = cost / lifespan / mmath.MONTHS_IN_YEAR

    def __str__(self):
        return f"{ui.dollar(self.total)} over {self.lifespan} years"


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
            return f"{mmath.decimal2percent(self.calc)}% of {str(self.calctype)}"

    def __str__(self):
        return f"{self.label} - ${self.value} ({self.calcstr})"

    def __repr__(self):
        return str(self)


IRONHARBOR_FHA_MONTHLY_COSTS = [
    MonthlyCost(
        label="Mortgage insurance estimate",
        calc=0.85,
        calctype=MCCalcType.YEARLY_PRINCIPAL_FRACTION),

    # TODO: This is not very precise - I think I'm calculating it wrong
    #       Looking at different sale prices, it goes between 0.0342% and 0.045%
    MonthlyCost(
        label="Hazard insurance (AKA homeowners insurance) estimate",
        calc=0.04,
        calctype=MCCalcType.SALE_FRACTION),
]

TEXAS_PROPERTY_TAXES_MONTHLY_COSTS = [
    MonthlyCost(
        label="Property taxes estimate - 2.0%",
        # I just google'd for an average and rounded up a bit;
        # users with more precise knowledge should not use this cost,
        # and define their own instead
        calc=0.020,
        calctype=MCCalcType.VALUE_FRACTION),
]

CAPEX_MONTHLY_COSTS = [
    MonthlyCost(
        # Source: hearsay. Is this too high? I'm seeing wildly varying numbers here
        label="Roof",
        calc=MCCapEx(12_000, 25),
        calctype=MCCalcType.CAPEX),
    MonthlyCost(
        # Source: hearsay
        label="Water heater",
        calc=MCCapEx(600, 10),
        calctype=MCCalcType.CAPEX),
    MonthlyCost(
        # Source: Total guess
        label="Refrigerator",
        calc=MCCapEx(1000, 10),
        calctype=MCCalcType.CAPEX),
    MonthlyCost(
        # Source: Total guess
        label="Oven / stovetop",
        calc=MCCapEx(600, 10),
        calctype=MCCalcType.CAPEX),
    MonthlyCost(
        # Source: hearsay
        label="Dishwasher",
        calc=MCCapEx(600, 10),
        calctype=MCCalcType.CAPEX),
    MonthlyCost(
        # Source: TBORPI
        label="Driveway",
        calc=MCCapEx(5000, 50),
        calctype=MCCalcType.CAPEX),
    MonthlyCost(
        # Source: https://www.angieslist.com/articles/how-much-does-installing-new-ac-cost.htm
        label="Air conditioner",
        calc=MCCapEx(5_500, 10),
        calctype=MCCalcType.CAPEX),
    MonthlyCost(
        # Source: ttps://www.angieslist.com/articles/how-much-does-it-cost-install-new-furnace.htm
        label="Heater / furnace",
        calc=MCCapEx(4_500, 10),
        calctype=MCCalcType.CAPEX),
    MonthlyCost(
        # Source: hearsay
        # TODO: A way to calculate based on square footage?
        label="Flooring",
        calc=MCCapEx(3_000, 5),
        calctype=MCCalcType.CAPEX),
    MonthlyCost(
        # Source: TBORPI
        label="Plumbing",
        calc=MCCapEx(3_000, 30),
        calctype=MCCalcType.CAPEX),
    MonthlyCost(
        label="Windows",
        calc=MCCapEx(5_000, 50),
        calctype=MCCalcType.CAPEX),
    MonthlyCost(
        label="Paint",
        calc=MCCapEx(2_500, 5),
        calctype=MCCalcType.CAPEX),
    MonthlyCost(
        label="Cabinets and countertops",
        calc=MCCapEx(3_000, 20),
        calctype=MCCalcType.CAPEX),
    MonthlyCost(
        label="Structure (foundation / framing)",
        calc=MCCapEx(10_000, 50),
        calctype=MCCalcType.CAPEX),
    MonthlyCost(
        label="Components (garage door, etc)",
        calc=MCCapEx(1_000, 10),
        calctype=MCCalcType.CAPEX),
    MonthlyCost(
        label="Landscaping",
        calc=MCCapEx(1_000, 10),
        calctype=MCCalcType.CAPEX),
]

MISC_MONTHLY_COSTS = [
    MonthlyCost(
        label="Vacancy estimate (5%)",
        calc=0.05,
        calctype=MCCalcType.MONTHLY_RENT_FRACTION),
    MonthlyCost(
        label="Miscellaneous / unexpected repairs (10%)",
        calc=0.10,
        calctype=MCCalcType.MONTHLY_RENT_FRACTION),
    MonthlyCost(
        label="Property management estimate (10%)",
        calc=0.10,
        calctype=MCCalcType.MONTHLY_RENT_FRACTION),
    MonthlyCost(
        label="Lawn care estimate",
        value=100),
]


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
