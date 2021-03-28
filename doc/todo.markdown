# TODO

* Property taxes are inconsistent
    * Only tracked in monthly costs if the `texas_property_tax_monthly` cost configuration is selected
    * Used in closing costs based on hardcoded value? Or something.
* Doesn't track insurance
    * Insurance is calculated for closing costs
    * Not calculated at all for monthly costs
* Extremely slow
    * I think there must be some O(N^2) bullshit going on, investigate
* Adding new things to the UI is really confusing and happens in several places
    * Need to either document this or fix it

## Basic feature and UX improvements

- Denote additional one-time payments
- Track forced appreciation (aka spending money to improve property value, e.g. by remodeling)
- Record various property facts: historical rent in area, historical sell price in area, etc
- Calculate ROI after certain period of time (e.g. closing costs + mortgage payments vs cash when you sell)
- Calculate COCROI (cash-on-cash ROI, aka the return on investment just off monthly cashflow, not including principal or appreciation)
- Show "percent rules" e.g. 1% rule or 3% rule or whatever - what percentage of total loan (or is it principal?) is monthly rent?
- Calculate some numbers for recommended reserve cash on hand - maybe start with a six-month recommendation (per TBORPI)
- UI to show details on "house hack" type properties
- Allow reloading cost configs without having to restart the Jupyter kernel
- Figure out how to get property taxes from just one place... right now the monthly and closing costs are in costconfigs, but it's also defined as a parameter so I can pass it to schedule(), and these values are not synced

## Code cleanup tasks

- Validate YAML cost configs using voluptuous? (no external deps except nose!) <https://pypi.python.org/pypi/voluptuous/>
- LoanPayment objects now track more than mere loan payments. Rename to something that makes sense.
- It's wayyyyyy past time I should have tests on this shit
- I have bloodloan.ui.uiutil and bloodloan.util modules... do something about that

## Big / complex new features

- Automatically retrieve historical data about rents/sale prices in the area (from where?)
    - Maybe something like this could help? https://www.housecanary.com/product-analytics-api#pricing-calculator
    - Or perhaps this? https://developer.onboard-apis.com/pricing
    - This looks good, and is free: https://www.zillow.com/howto/api/GetDeepSearchResults.htm
    - Calculating exact property tax might be doable from this: https://comptroller.texas.gov/taxes/property-tax/rates/index.php
    however I don't know how to determine all the special districts that a property is part of
    - This is for regular people, but has the same problem: https://tax-office.traviscountytx.gov/property-tax-estimator
    - These pages might have info? http://www.txcip.org/tac/census/CountyProfiles.php
    for instance if I can figure out how to get this page for other counties: http://www.txcip.org/tac/census/districthist.php?FIPS=48439
- A way to calculate a CapitalExpenditure's cost based on square footage? Would be useful for flooring and maybe roofs
- Figure out a way to show ranges, e.g. if your mortgage broker gives you origination options
