"""Monthly expenses"""

import copy
import enum

from bloodloan.log import LOG as log
from bloodloan.mortgage import mmath


class MCCalcType(enum.Enum):
    """Determines how the amount of the MonthlyCost is calculated

    DOLLAR_AMOUNT               a raw dollar amount
    SALE_FRACTION               a percentage of the sale price
    YEARLY_PRINCIPAL_FRACTION   a percentage of the loan, calculated once per year,
                                and paid monthly
    PROPERTY_TAX_FRACTION       a percentage of the first year of property taxes
    CAPEX                       the calc property is an MCCapEx
    """
    DOLLAR_AMOUNT = enum.auto()
    SALE_FRACTION = enum.auto()
    YEARLY_PRINCIPAL_FRACTION = enum.auto()
    PROPERTY_TAX_FRACTION = enum.auto()
    CAPEX = enum.auto()


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

    def __str__(self):
        result = f"{self.label} - ${self.value}"
        if self.calctype is MCCapEx:
            result += f" (${self.calctype.total}/{self.calctype.lifespan}y)"
        elif self.calctype is not MCCalcType.DOLLAR_AMOUNT:
            result += f" ({self.calc}% of {self.calctype})"
        return result


IRONHARBOR_FHA_MONTHLY_COSTS = [
    MonthlyCost(
        label="Mortgage insurance",
        calc=0.85,
        calctype=MCCalcType.YEARLY_PRINCIPAL_FRACTION),

    # TODO: This is not very precise - I think I'm calculating it wrong
    #       Looking at different sale prices, it goes between 0.0342% and 0.045%
    MonthlyCost(
        label="Hazard insurance (AKA homeowners insurance)",
        calc=0.04,
        calctype=MCCalcType.SALE_FRACTION)
]
CAPEX_MONTHLY_COSTS = [
    # TODO: Double check this, and complete this list
    MonthlyCost(
        label="New roof",
        calc=MCCapEx(12_000, 25),
        calctype=MCCalcType.CAPEX)
]


def monthly_expenses(costs, saleprice, boyprincipal):
    """Calculate monthly expenses

    costs           list of MonthlyCost objects
    saleprice       sale price of the property
    boyprincipal    principal at beginning of year to calculate for
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
        elif cost.calctype is MCCalcType.CAPEX:
            cost.value = cost.calc.monthly
        else:
            raise NotImplementedError()

        log.info(f"Calculating monthy expense: {cost}")
        expenses.append(cost)

    return expenses
