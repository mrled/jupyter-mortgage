

class MCCalcType(Enum):
    """Determines how the amount of the MonthlyCost is calculated

    DOLLAR_AMOUNT           a raw dollar amount
    SALE_FRACTION           a percentage of the sale price
    LOAN_FRACTION           a percentage of the loan
    PROPERTY_TAX_FRACTION   a percentage of the first year of property taxes
    """
    DOLLAR_AMOUNT = auto()
    SALE_FRACTION = auto()
    LOAN_FRACTION = auto()
    PROPERTY_TAX_FRACTION = auto()


class MonthlyCost():
    """A single monthly cost line item

    Properties:
    label:          an arbitrary text label
    value           the value to be paid, expressed in dollars
    calc            how the value amount is calculated
                    for DOLLAR_AMOUNT, this is empty; for other calculation
                    types, it may be a percentage or something else; see
                    MCCalcType for more information
    calctype        how the value is to be interpreted
                    should be a CCCalcType
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

    def __repr__(self):
        return f"{self.label} - {self.value}"


IRONHARBOR_FHA_MONTHLY_COSTS = [
    MonthlyCost(
        label="Mortgage insurance",
        calc=0.85,
        calctype=MCCalcType.LOAN_FRACTION)
]

