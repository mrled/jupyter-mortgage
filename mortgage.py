"""Mortgage calculations"""

def yearly2monthly(apryearly):
    """Convert yearly APR to monthly APR"""
    return apryearly / 12 / 100

class Loan(object):
    """A loan"""

    overpayments = ()

    def __init__(self, principal, apryearly, months):
        """Initialize a loan

        principal:  total amount of the loan
        apryearly:  yearly APR of the loan,
                    probably the number from a mortgage broker,
                    such as 3.5% or 8%
        months:     term length of the loan in months
        """
        self.principal = principal
        self.apryearly = apryearly
        self.aprmonthly = yearly2monthly(apryearly)
        self.months = months
        self.overpayments = [0 for _ in range(self.months)]

    # https://en.wikipedia.org/wiki/Mortgage_calculator#Monthly_payment_formula
    @property
    def monthly_payment(self):
        """The monthly mortgage payment amount"""
        return self.aprmonthly * self.principal / (1 - (1 + self.aprmonthly)**(-self.months))

    # https://en.wikipedia.org/wiki/Mortgage_calculator#Monthly_payment_formula
    def balance_after(self, months):
        """The principal balance after N months

        months: the month to calculate from
        """
        return (1 + self.aprmonthly)**months * self.principal - ((1 + self.aprmonthly)**months - 1) / self.aprmonthly * self.monthly_payment

    def schedule(self):
        htmlstr  = f"<h1>Mortgage amortization schedule: ${self.principal} / {self.months} months @ {self.apryearly}%</h1>"
        htmlstr += "<table>"
        htmlstr += "<tr><th>Month</th><th>Mortgage payment</th><th>Principal balance</th></tr>"
        for month in range(self.months):
            htmlstr += f"<tr><td>{month}</td><td>{self.monthly_payment}</td><td>{self.balance_after(month)}</td>"
        htmlstr += "</table>"
        return htmlstr
