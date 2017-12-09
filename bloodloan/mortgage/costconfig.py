"""Cost Configuration

Code related to closing costs and monthly expenses
"""

import enum
import logging
import numbers
import os

import yaml

from bloodloan.mortgage import mmath
from bloodloan.ui import uiutil


logger = logging.getLogger(__name__)  # pylint: disable=C0103


class CostType(enum.Enum):
    """Determines the type of a cost

    CLOSING     a cost which must be paid at closing
    MONTHLY     a cost which must be paid each month
    """

    CLOSING = 'closing'
    MONTHLY = 'monthly'


class CostPaymentType(enum.Enum):
    """Determines how cost a will be paid

    PRINCIPAL       added to the total amount of the loan
    DOWN_PAYMENT    the down payment (probably there is just one)
    FEE             fees owed to other parties
    """

    PRINCIPAL = 'principal'
    DOWN_PAYMENT = 'downpayment'
    FEE = 'fee'


class CostCalculationType(enum.Enum):
    """Determines how the amount of the MonthlyCost is calculated

    DOLLAR_AMOUNT               a raw dollar amount
    SALE_FRACTION               a percentage of the sale price
    VALUE_FRACTION              a percentage of the property's current value
    LOAN_FRACTION               a percentage of the initial loan value
    YEARLY_PRINCIPAL_FRACTION   a percentage of the loan, calculated once per year, paid monthly
    PROPERTY_TAX_FRACTION       a percentage of the first year of property taxes
    MONTHLY_RENT_FRACTION       a percentage of projected rent received from property
    INTEREST_MONTHS             a number representing months (or a month fraction) of interest
    CAPEX                       the calc property is a CapitalExpenditure
    """

    DOLLAR_AMOUNT = 'amount'
    SALE_FRACTION = 'sale fraction'
    VALUE_FRACTION = 'value fraction'
    LOAN_FRACTION = 'loan fraction'
    YEARLY_PRINCIPAL_FRACTION = 'BOY remaining principal fraction'
    PROPERTY_TAX_FRACTION = 'yearly property tax fraction'
    MONTHLY_RENT_FRACTION = 'rent fraction'
    INTEREST_MONTHS = 'months of interest'
    CAPEX = 'capex'


class CapitalExpenditure():
    """A capital expenditure

    cost        cost of the item new
    lifespan    lifespan in years of the item
    monthly     monthly cost to put aside to afford it
                (assumes the item is currently brand new)
    """

    def __init__(self, dictionary=None, cost=None, lifespan=None):
        """Initialize the object

        Note that there are mandatory fields which may be initialized either as a property of the
        dictionary or as a kwarg. If a field is present in both, the kwarg takes precedence.
        """
        self.total = cost or dictionary.get('cost')
        self.lifespan = lifespan or dictionary.get('lifespan')

        if not self.total or not isinstance(self.total, numbers.Number):
            raise ValueError(f"Invalid total cost value {self.total}")
        if not self.lifespan or not isinstance(self.lifespan, numbers.Number):
            raise ValueError(f"Invalid lifespan value {self.lifespan}")

        self.monthly = self.total / self.lifespan / mmath.MONTHS_IN_YEAR

    def __str__(self):
        return f"{uiutil.dollar(self.total)} over {self.lifespan} years"


class Cost():
    """A single closing cost line item

    Properties:
    label       an arbitrary text label
    costtype    the type of cost
                must be a CostType
    value       the value to be paid, expressed in dollars
                for DOLLAR_AMOUNT, this is populated, but for other calculation types, it is
                empty at first. Then when costs are applied (for example, in close() or
                monthly_expenses()), it is calculated and then set
    calc        how the value amount is calculated
                for DOLLAR_AMOUNT, this is empty
                for CAPEX, this is a CapitalExpenditure object
                for other calculations, it is a percentage
    calctype    how the value is to be interpreted
                should be a CostCalculationType
    paytype     how the payment is applied
                should be a CostPaymentType
    """

    def __init__(
            self,
            dictionary=None,
            label=None,
            value=None,
            calc=None,
            costtype=None,
            calctype=None,
            paytype=None):
        """Initialize the object

        Note that there are mandatory fields which may be initialized either as a property of the
        dictionary or as a kwarg. If a field is present in both, the kwarg takes precedence.

        (See class docstring for a description of these properties)

        dictionary  optional
        label       mandatory
        value       mandatory if calctype is CostCalculationType.DOLLAR_AMOUNT
        calc        mandatory if calctype is not CostCalculationType.DOLLAR_AMOUNT
        costtype    mandatory
        calctype    optional; defaults to CostCalculationType.DOLLAR_AMOUNT
        paytype     optional; defaults to CostPaymentType.FEE
        """

        dictionary = dictionary or {}

        if not isinstance(dictionary, dict):
            raise ValueError(f"dictionary was type {type(dictionary)} with value {dictionary}")

        self.label = label or dictionary['label']
        self.value = value or dictionary.get('value')
        self.calc = calc or dictionary.get('calc') or dictionary.get('calculation')
        self.costtype = CostType(
            costtype or
            dictionary.get('costtype') or
            dictionary.get('cost type'))
        self.calctype = CostCalculationType(
            calctype or
            dictionary.get('calctype') or
            dictionary.get('calculation type') or
            CostCalculationType.DOLLAR_AMOUNT)
        self.paytype = CostPaymentType(
            paytype or
            dictionary.get('paytype') or
            dictionary.get('payment type') or
            CostPaymentType.FEE)

        if not self.label:
            raise ValueError(f"Invalid empty label")
        if not (self.value is None or isinstance(self.value, numbers.Number)):
            raise ValueError(f"Invalid value '{self.value}'")
        if not (self.calc is None or isinstance(self.calc, (numbers.Number, CapitalExpenditure))):
            raise ValueError(f"Invalid calc '{self.calc}'")

        if not isinstance(self.costtype, CostType):
            raise ValueError(f"Invalid value for costtype: '{self.costtype}'")
        if not isinstance(self.calctype, CostCalculationType):
            raise ValueError(f"Invalid value for calctype: '{self.calctype}'")
        if not isinstance(self.paytype, CostPaymentType):
            raise ValueError(f"Invalid value for paytype: '{self.paytype}'")

        if self.calc and self.calctype in [CostCalculationType.DOLLAR_AMOUNT, None]:
            raise ValueError(f"Non-None calc value ({self.calc}) but DOLLAR_AMOUNT calctype")
        if not self.calc and self.calctype is not CostCalculationType.DOLLAR_AMOUNT:
            raise ValueError(f"Missing calculation for calctype of {self.calctype}")

        calc_capex = isinstance(self.calc, CapitalExpenditure)
        calctype_capex = self.calctype is CostCalculationType.CAPEX
        if calc_capex != calctype_capex:
            raise ValueError(" ".join([
                f"1: {isinstance(self.calc, CapitalExpenditure)}\n",
                f"2: {self.calctype is CostCalculationType.CAPEX}\n",
                f"A capex entry must have matching calc ({self.calc})",
                f"and calctype ({self.calctype}) values"]))

    @property
    def calcstr(self):
        """A nice string to explain how the calculation is done"""
        if self.calctype is CostCalculationType.DOLLAR_AMOUNT:
            return self.calctype.value
        elif self.calctype is CostCalculationType.CAPEX:
            return self.calc
        else:
            return f"{uiutil.percent(self.calc)} of {self.calctype.value}"

    def __str__(self):
        return " ".join([
            f"{self.costtype}: {self.label} - {self.value}",
            f"({self.calcstr}) ({self.paytype})"])

    def __repr__(self):
        return str(self)


class CostConfiguration:
    """A bundle of closing and monthly costs
    """

    def __init__(self, label, description="", closing=None, monthly=None):
        self.label = label
        self.description = description
        self.closing = closing or []
        self.monthly = monthly or []

    @classmethod
    def fromdict(cls, dictionary):
        """Return an instance given a dictionary that describes it

        (e.g. from a YAML config file)
        """
        result = CostConfiguration(dictionary['label'])
        result.description = dictionary['description'] if 'description' in dictionary else ""
        if 'closing' in dictionary:
            for cost in dictionary['closing']:
                result.closing.append(Cost(dictionary=cost, costtype=CostType.CLOSING))
        if 'monthly' in dictionary:
            for cost in dictionary['monthly']:
                result.monthly.append(Cost(dictionary=cost, costtype=CostType.MONTHLY))
        if 'capex' in dictionary:
            for cost in dictionary['capex']:
                result.monthly.append(Cost(
                    label=cost['label'],
                    costtype=CostType.MONTHLY,
                    calc=CapitalExpenditure(cost),
                    calctype=CostCalculationType.CAPEX))
        return result


class CostConfigurationCollection:
    """A collection of CostConfiguration objects
    """

    def __init__(self, configs=None, directory=None):
        self.configs = configs or []
        if directory:
            self.configs += self._fromdir(directory)

    def __str__(self):
        return " ".join([
            "<CostConfigurationCollection:",
            f"{len(self.closing)} closing costs,",
            f"{len(self.monthly)} monthly costs",
            ">"
        ])

    def _fromdir(self, directory):
        """Read all cost configuration YAML files from a directory

        Return a list of config objects
        """
        result = []

        for child in [os.path.join(directory, f) for f in os.listdir(directory)]:
            if not os.path.isfile(child):
                continue

            with open(child) as cfile:
                try:
                    contents = yaml.load(cfile)
                except yaml.parser.ParserError as exc:
                    logger.error(f"Error parsing config file {child}: {exc}")
                    continue

            # TODO: Do real validation here - is there such a thing as a YAML schema?
            #       Alternatively: maybe just try to apply them, then if they don't work display a
            #       message saying that cost configurations from xyz file are not available?

            result.append(CostConfiguration.fromdict(contents))

        return result

    @property
    def closing(self):
        """All closing costs from all configs
        """
        result = []
        for config in self.configs:
            for cost in config.closing:
                result.append(cost)
        return result

    @property
    def monthly(self):
        """All monthly costs from all configs
        """
        result = []
        for config in self.configs:
            for cost in config.monthly:
                result.append(cost)
        return result

    def get(self, labels):
        """Get cost configurations from their labels

        labels      a list of labels to retrieve

        returns     a CostConfigurationCollection
        """
        return CostConfigurationCollection(
            configs=[cc for cc in self.configs if cc.label in labels])
