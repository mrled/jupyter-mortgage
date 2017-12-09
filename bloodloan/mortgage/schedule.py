"""Mortgage schedule"""

import logging

from bloodloan.mortgage import expenses
from bloodloan.mortgage import mmath


logger = logging.getLogger(__name__)  # pylint: disable=C0103


class LoanPayment:
    """A single loan payment and its result"""

    def __init__(
            self,
            index=0,
            regularpmt=0,
            interestpmt=0,
            balancepmt=0,
            overpmt=0,
            principal=0,
            value=0,
            rent=0,
            totalinterest=0,
            othercosts=None):
        self.index = index
        self.regularpmt = regularpmt
        self.interestpmt = interestpmt
        self.balancepmt = balancepmt
        self.overpmt = overpmt
        self.principal = principal
        self.value = value
        self.rent = rent
        self.totalinterest = totalinterest
        self.othercosts = othercosts or []

    def __str__(self):
        return " ".join([
            "LoanPayment<",
            f"#{self.index}",
            f"RegularPayment({self.regularpmt})",
            f"Total({self.totalpmt})",
            f"Interest({self.interestpmt})",
            f"Balance({self.balancepmt})",
            f"Over({self.overpmt})",
            f"RemainingPrincipal({self.principal})",
            f"Value({self.value})",
            f"Equity({self.equity})",
            f"ProjectedRent({self.rent})",
            f"TotalInterest({self.totalinterest})",
            f"OtherCosts({self.totalothercosts})",
            ">"
        ])

    def __repr__(self):
        return str(self)

    @property
    def totalothercosts(self):
        """Total dollar amount for all othercosts"""
        return sum([cost.value for cost in self.othercosts])

    @property
    def totalpmt(self):
        """Total payment amount"""
        return self.interestpmt + self.balancepmt + self.overpmt + self.totalothercosts

    @property
    def equity(self):
        """Equity as of this payment"""
        return self.value - self.principal


def schedule(
        interestrate,
        value,
        principal,
        saleprice,
        term,
        overpayments=None,
        appreciation=0,
        monthlycosts=None,
        monthlyrent=0):
    """A schedule of payments, including overpayments

    interestrate    yearly interest rate of the loan
    value           value of the property
                    (what it would be worth when sold)
    principal       total amount of the loan
                    (saleprice - downpayment + anything rolled in to loan)
    saleprice       price actually paid for the property
                    (when purchased)
    term            loan term in months
    overpayments    array of overpayment amounts for each month in the term
    appreciation    appreciation in decimal value representing percent
    monthlycosts    list of MonthlyCost objects to apply
    monthlyrent     projected monthly rent for the property

    yield           LoanPayment objects

    NOTE: Calculating with the actual formula
    You can use the formula to calculate monthly payments
    The disadvantage to this is basically me: I haven't figured out how to apply overpayments
    (I guess if I remembered calculus better, I could use a calculus formula instead.)
    def balance_after(interestrate, principal, term, month):
        '''The principal balance after N months of on-time patyments of *only* the monthly_payment

        Formula from: https://en.wikipedia.org/wiki/Mortgage_calculator#Monthly_payment_formula

        interestrate    yearly interest rate of the loan
        principal       total amount of the loan
        term            loan term in months
        month           the month to calculate from
        '''
        mrate = monthlyrate(interestrate)
        mpay = monthly_payment(interestrate, principal, term)
        return (1 + mrate)**month * principal - ((1 + mrate)**month - 1) / mrate * mpay
    """
    overpayments = overpayments or []
    mpay = mmath.monthly_payment(interestrate, principal, term)
    logger.info(f"Monthly payment calculated at {mpay}")
    monthidx = 0
    totalinterest = 0
    # beginning-of-year principal
    boyprincipal = principal
    while principal > 0:
        if monthidx > term:
            raise Exception("This should never happen")

        if monthidx % 12 == 0:
            boyprincipal = principal

        interestpmt = principal * mmath.monthlyrate(interestrate)
        totalinterest += interestpmt
        balancepmt = mpay - interestpmt
        try:
            overpmt = overpayments[monthidx]
        except IndexError:
            overpmt = 0

        if principal <= 0:
            # Break before the yield so we don't get empty lines
            logger.info(f"#{monthidx}: Principal {principal} is <= 0 in final month")
            break
        elif principal < 0.01:
            # Also break if the principal is less than a cent
            # This prevents a weird payment that looks like it's for $0,
            # but actually is a rounded-down fraction of a cent
            logger.info(
                f"#{monthidx}: Ignoring remaining principal of {principal} "
                "because it is a fraction of a cent in final month")
            break
        elif principal - balancepmt - overpmt <= 0:
            # Paying the normal amount will result in overpaying in the final month
            # Handle this by adjusting the balancepmt and overpmt
            if principal - balancepmt > 0:
                logger.info(f"#{monthidx}: Truncating overpayment to {overpmt} in final month")
                overpmt = principal - balancepmt
                principal = 0
            elif balancepmt > principal:
                logger.info(
                    f"#{monthidx}: Truncating balance payment to {balancepmt} in final month")
                overpmt = 0
                balancepmt = principal
                principal = 0
            else:
                raise Exception("This should not happen")
        else:
            # logger.debug(f"#{monthidx}: Paying normal amounts in non-final month")
            principal = principal - balancepmt - overpmt

        monthapprec = appreciation / mmath.MONTHS_IN_YEAR
        value = value * (1 + monthapprec)
        othercosts = expenses.monthly_expenses(
            monthlycosts, saleprice, value, boyprincipal, monthlyrent)

        payment = LoanPayment(
            index=monthidx,
            regularpmt=mpay,
            interestpmt=interestpmt,
            balancepmt=balancepmt,
            overpmt=overpmt,
            principal=principal,
            value=value,
            rent=monthlyrent,
            totalinterest=totalinterest,
            othercosts=othercosts)

        yield payment

        monthidx += 1


def monthly2yearly_schedule(months):
    """Convert a monthly schedule to a yearly one

    months: array of LoanPayment objects
    """
    year = None
    idx = 0
    for month in months:
        if idx % mmath.MONTHS_IN_YEAR == 0:
            if year:
                yield year
                newyearidx = year.index + 1
            else:
                newyearidx = 0
            year = LoanPayment(index=newyearidx)

        # Adds:
        year.regularpmt += month.regularpmt
        year.totalpmt += month.totalpmt
        year.interestpmt += month.interestpmt
        year.balancepmt += month.balancepmt
        year.overpmt += month.overpmt
        year.rent += month.rent
        year.othercosts += month.othercosts

        # Overwrites:
        year.principal = month.principal
        year.value = month.value
        year.equity = month.equity
        year.totalinterest = month.totalinterest
        idx += 1

    yield year
