"""Monthly expenses"""

import copy
import logging

from bloodloan.mortgage import costconfig
from bloodloan.mortgage import mmath


logger = logging.getLogger(__name__)  # pylint: disable=C0103


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
        if cost.calctype == costconfig.CostCalculationType.DOLLAR_AMOUNT and cost.value is None:
            raise Exception(
                f"The {cost.label} MonthlyCost calctype is DOLLAR_AMOUNT, "
                "but with an empty value property")
        elif (
                cost.calctype is not costconfig.CostCalculationType.DOLLAR_AMOUNT and
                cost.calc is None):
            raise Exception(
                f"The {cost.label} MonthlyCost calctype is {cost.calctype}, "
                "but with an empty calc property")

        # Now calculate what can be calculated now
        # Don't calculate LOAN_FRACTION or INTEREST_MONTHS calctypes here,
        # because any PRINCIPAL paytypes will affect their value
        if cost.calctype is costconfig.CostCalculationType.DOLLAR_AMOUNT:
            pass
        elif cost.calctype is costconfig.CostCalculationType.YEARLY_PRINCIPAL_FRACTION:
            cost.value = boyprincipal * cost.calc / mmath.MONTHS_IN_YEAR
        elif cost.calctype is costconfig.CostCalculationType.SALE_FRACTION:
            cost.value = saleprice * cost.calc
        elif cost.calctype is costconfig.CostCalculationType.VALUE_FRACTION:
            cost.value = propvalue * cost.calc
        elif cost.calctype is costconfig.CostCalculationType.MONTHLY_RENT_FRACTION:
            cost.value = rent * cost.calc
        elif cost.calctype is costconfig.CostCalculationType.CAPEX:
            cost.value = cost.calc.monthly
        else:
            raise NotImplementedError(
                f"Cannot process a cost with a calctype of {cost.calctype}")

        # logger.info(f"Calculating monthy expense: {cost}")
        expenses.append(cost)

    return expenses
