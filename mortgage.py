"""Mortgage calculations"""

import collections

MONTHS_IN_YEAR = 12

def dollar(amount):
    """Return a string dollar amount from a float

    For example, dollar(1926.2311831442486) => "$1,926.23"

    We aren't too concerned about the lost accuracy;
    this function should only be used for *display* values
    """
    return '${:,.2f}'.format(amount)

class Loan(object):
    """A loan"""

    overpayments = ()

    MonthInSchedule = collections.namedtuple('MonthInSchedule', ['index', 'interestpmt', 'balancepmt', 'overpmt', 'principal'])

    def __init__(self, principal, apryearly, months, overpayment=0):
        """Initialize a loan

        principal:  total amount of the loan
        apryearly:  yearly APR of the loan,
                    probably the number from a mortgage broker,
                    such as 3.5% or 8%
        months:     term length of the loan in months
        addtlpay:   an additional amount to apply to the loan principal
                    *every month*
        """
        self.principal = principal
        self.apryearly = apryearly
        self.months = months
        self.monthly_overpayment = overpayment
        self.overpayments = [overpayment for _ in range(self.months)]

    @property
    def monthlyrate(self):
        """The monthly rate, as calculated from the yearly APR

        I'm not honestly clear on what this *is*,
        or the difference betweenit and the "monthly APR" below,
        or if I'm even using the right terms for these,
        but it's required for the way my existing spreadsheet
        calculates principal balance after overpayment
        """
        return self.apryearly / MONTHS_IN_YEAR

    @property
    def aprmonthly(self):
        """The monthly APR, as calculated from the yearly APR"""
        return self.apryearly / MONTHS_IN_YEAR / 100

    # https://en.wikipedia.org/wiki/Mortgage_calculator#Monthly_payment_formula
    @property
    def monthly_payment(self):
        """The monthly mortgage payment amount"""
        return self.aprmonthly * self.principal / (1 - (1 + self.aprmonthly)**(-self.months))

    # Use the actual formula
    # I haven't figured out a way to incorporate overpayments into the formula
    # https://en.wikipedia.org/wiki/Mortgage_calculator#Monthly_payment_formula
    def balance_after(self, monthidx):
        """The principal balance after N months of on-time patyments of *only* the monthly_payment

        monthidx:   the month to calculate from
        """
        return (1 + self.aprmonthly)**monthidx * self.principal - ((1 + self.aprmonthly)**monthidx - 1) / self.aprmonthly * self.monthly_payment

    # Rather than using the formula to calculate principal balance,
    # do it by brute-force
    # (I guess if I remembered calculus better,
    # I'd be able to use a calculus formula instead)
    # Incorporates overpayments
    def schedule(self):
        """A schedule of payments, including overpayments"""
        principal = self.principal
        monthidx = 0
        while principal > 0:
            interestpmt = principal * self.aprmonthly
            balancepmt = self.monthly_payment - interestpmt
            principal = principal - balancepmt - self.overpayments[monthidx]

            yield self.MonthInSchedule(
                index=monthidx,
                interestpmt=interestpmt,
                balancepmt=balancepmt,
                overpmt=self.overpayments[monthidx],
                principal=principal)

            monthidx += 1

    def htmlschedule(self):
        htmlstr  = "<h1>Mortgage amortization schedule</h1>"
        htmlstr += "<p>"
        htmlstr += f"Amortization schedule for a {self.principal} loan "
        htmlstr += f"over {self.months} months "
        htmlstr += f"at {self.apryearly}% interest, "
        htmlstr += f"including a {dollar(self.monthly_overpayment)} overpayment each month."
        htmlstr += "</p>"

        htmlstr += "<table>"

        htmlstr += "<tr>"
        htmlstr += "<th>Month</th>"
        htmlstr += "<th>Regular payment</th>"
        htmlstr += "<th>Interest</th>"
        htmlstr += "<th>Balance</th>"
        htmlstr += "<th>Overpayment</th>"
        htmlstr += "<th>Remaining principal</th>"
        htmlstr += "</tr>"

        htmlstr += "<tr>"
        htmlstr += "<td>Initial loan amount</td>"
        htmlstr += "<td></td>"
        htmlstr += "<td></td>"
        htmlstr += "<td></td>"
        htmlstr += "<td></td>"
        htmlstr += f"<td>{dollar(self.principal)}</td>"
        htmlstr += "</tr>"

        for month in self.schedule():
            htmlstr += "<tr>"
            htmlstr += f"<td>{month.index}</td>"
            htmlstr += f"<td>{dollar(self.monthly_payment)}</td>"
            htmlstr += f"<td>{dollar(month.interestpmt)}</td>"
            htmlstr += f"<td>{dollar(month.balancepmt)}</td>"
            htmlstr += f"<td>{dollar(month.overpmt)}</td>"
            htmlstr += f"<td>{dollar(month.principal)}</td>"
            htmlstr += "</tr>"

        htmlstr += "</table>"

        return htmlstr
