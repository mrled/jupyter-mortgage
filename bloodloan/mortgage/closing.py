"""Closing costs"""

import copy
import logging

from bloodloan.mortgage import costconfig
from bloodloan.mortgage import mmath
from bloodloan.mortgage import schedule


logger = logging.getLogger(__name__)  # pylint: disable=C0103


class CloseResult:
    """The result of a close() function call"""

    def __init__(self, saleprice=0, downpayment=None, fees=None, principal=None):
        self.saleprice = saleprice
        self.downpayment = downpayment or []
        self.fees = fees or []
        self.principal = principal or []
        self.principal.append(costconfig.Cost(
            label="Sale price",
            costtype=costconfig.CostType.CLOSING,
            value=saleprice,
            paytype=costconfig.CostPaymentType.PRINCIPAL))

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
        """Apply a cost to closing"""
        logger.info(f"Closing cost: {cost}")

        if cost.paytype == costconfig.CostPaymentType.PRINCIPAL:
            self.principal.append(cost)

        elif cost.paytype == costconfig.CostPaymentType.DOWN_PAYMENT:
            self.downpayment.append(cost)
            self.principal.append(costconfig.Cost(
                label="Down payment",
                costtype=costconfig.CostType.CLOSING,
                value=-cost.value,
                paytype=costconfig.CostPaymentType.PRINCIPAL))

        elif cost.paytype == costconfig.CostPaymentType.FEE:
            self.fees.append(cost)

        else:
            raise Exception(f"Unknown paytype {cost.paytype}")


def close(saleprice, interestrate, loanterm, propertytaxes, costs):
    """Calculate loan amount and closing costs

    saleprice       sale price for the property
    interestrate    interest rate for the loan
    loanterm        loan term in months
    propertytaxes   estimated property taxes
    costs           list of costconfig.Cost objects
    """

    result = CloseResult(saleprice=saleprice)

    # Don't modify costs we were passed, in case they are reused elsewhere
    costs = copy.deepcopy(costs)

    # BEWARE!
    # ORDER IS IMPORTANT AND SUBTLE!

    for cost in costs:
        # First, check our inputs
        if cost.calctype == costconfig.CostCalculationType.DOLLAR_AMOUNT and cost.value is None:
            raise Exception(
                f"The {cost.label} costconfig.Cost calctype is DOLLAR_AMOUNT, "
                "but with an empty value property")
        elif cost.calctype != costconfig.CostCalculationType.DOLLAR_AMOUNT and cost.calc is None:
            raise Exception(
                f"The {cost.label} costconfig.Cost calctype is {cost.calctype}, "
                "but with an empty calc property")

        # Now calculate what can be calculated now
        # Don't calculate LOAN_FRACTION or INTEREST_MONTHS calctypes here,
        # because any PRINCIPAL paytypes will affect their value
        if cost.calctype == costconfig.CostCalculationType.DOLLAR_AMOUNT:
            result.apply(cost)
        if cost.calctype == costconfig.CostCalculationType.SALE_FRACTION:
            cost.value = saleprice * mmath.percent2decimal(cost.calc)
            result.apply(cost)
        elif cost.calctype == costconfig.CostCalculationType.PROPERTY_TAX_FRACTION:
            cost.value = propertytaxes * mmath.percent2decimal(cost.calc)
            result.apply(cost)

    for cost in costs:
        # Now that we have calculated the other costs, including loan amount,
        # we can calculate LOAN_FRACTION or INTEREST_MONTHS calctypes
        # Note that theoretically you could have something weird like a cost of
        # calctype=LOAN_FRACTION paytype=PRINCIPAL,
        # but that wouldn't make much sense so we don't really handle it here
        if cost.calctype == costconfig.CostCalculationType.LOAN_FRACTION:
            cost.value = result.principal_total * mmath.percent2decimal(cost.calc)
            result.apply(cost)
        elif cost.calctype == costconfig.CostCalculationType.INTEREST_MONTHS:
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
