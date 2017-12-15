"""Closing costs"""

import copy
import logging

from bloodloan.mortgage import costconfig
from bloodloan.mortgage import mmath
from bloodloan.mortgage import schedule


logger = logging.getLogger(__name__)  # pylint: disable=C0103


class CloseResult:
    """The result of a close() function call"""

    def __init__(self):
        self.downpayment = []
        self.fees = []
        self.principal = []

    def __str__(self):
        return " ".join([
            f"<CloseResult:",
            f"Down ${self.downpayment_total} ({len(self.downpayment)}),",
            f"Fees ${self.fees_total} ({len(self.fees)}),",
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

    @staticmethod
    def sum(costs):
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


def close(saleprice, interestrate, loanterm, closingcosts, monthlycosts):
    """Calculate loan amount and closing costs

    saleprice       sale price for the property
    interestrate    interest rate for the loan
    loanterm        loan term in months
    costs           list of costconfig.Cost objects
    """

    result = CloseResult()

    result.apply(costconfig.Cost(
        label="Sale price",
        costtype=costconfig.CostType.CLOSING,
        value=saleprice,
        paytype=costconfig.CostPaymentType.PRINCIPAL))

    # Don't modify costs we were passed, in case they are reused elsewhere
    closingcosts = copy.deepcopy(closingcosts)
    monthlycosts = copy.deepcopy(monthlycosts)

    # BEWARE!
    # ORDER IS IMPORTANT AND SUBTLE!

    for cost in closingcosts:
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
        elif (
                cost.calctype == costconfig.CostCalculationType.SALE_FRACTION or
                cost.calctype == costconfig.CostCalculationType.VALUE_FRACTION):
            # At closing, assume sale price == value
            cost.value = saleprice * cost.calc
            result.apply(cost)

    # Check that we have calculated all costs that affect principal
    # (or which affect down payment, which affects principal)
    for cost in closingcosts:
        if cost.paytype != costconfig.CostPaymentType.FEE and not cost.value:
            raise Exception(
                f"The '{cost.label}' cost (paytype: {cost.paytype}, calctype: {cost.calctype}) "
                "but has not yet been able to calculate its value")

    # This means that we know know the total principal
    principal = result.principal_total

    # Now calculate a schedule to be used as the basis for subsequent calculations
    sched = [month for month in schedule.schedule(
        interestrate, saleprice, principal, saleprice, loanterm, monthlycosts=monthlycosts)]

    for cost in closingcosts:
        # Now that we have calculated the other costs, including loan amount,
        # we can calculate LOAN_FRACTION or INTEREST_MONTHS calctypes
        # Note that theoretically you could have something weird like a cost of
        # calctype=LOAN_FRACTION paytype=PRINCIPAL,
        # but that wouldn't make much sense so we don't really handle it here
        if cost.calctype == costconfig.CostCalculationType.LOAN_FRACTION:
            cost.value = principal * cost.calc
            result.apply(cost)
        elif cost.calctype == costconfig.CostCalculationType.INTEREST_MONTHS:
            # We make some assumptions here
            # 1)    Assumes interest is the same in all months (not true)
            #       OK because we don't expect INTEREST_MONTHS to be many months long
            # 2)    Assumes saleprice == value
            #       OK at closing, but won't be right for calculating a monthly cost
            cost.value = sched[0].interestpmt * cost.calc
            result.apply(cost)
        elif cost.calctype == costconfig.CostCalculationType.PROPERTY_TAX_FRACTION:
            logger.info("Calculating property taxes...")
            # We only need the first year, because this is a closing cost
            prop_tax_values = []
            for month in sched[0:mmath.MONTHS_IN_YEAR]:
                for monthcost in month.othercosts:
                    if monthcost.identifier == costconfig.CostIdentifier.PROPERTY_TAXES:
                        prop_tax_values += [monthcost.value]
            logger.info("Calculated property taxes to be {} from monthly costs: {}".format(
                sum(prop_tax_values), prop_tax_values))
            cost.value = sum(prop_tax_values) * cost.calc
            result.apply(cost)

    return result
