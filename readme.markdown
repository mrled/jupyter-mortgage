# Jupyter Mortgage Calculator

It's a work-in-progress Jupyter notebook for mortgage calculations.

You can use [Binder](https://mybinder.org/) to run this notebook online. No installation required!

- `master` branch: [![master](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/mrled/jupyter-mortgage/master?filepath=MortgageWorksheet.ipynb)
- `devel` branch: [![master](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/mrled/jupyter-mortgage/devel?filepath=MortgageWorksheet.ipynb)

## VH1's BEHIND THE REPO

I told Josiah I was doing this:

> Writing a mortgage calculator in a Jupyter notebook  
> Which… might not be a great use of my time  
> But I decided it was more fun than learning the Excel macro language, so here we are

He was not impressed:

> I’m  
> Um  
> It’s Friday night

But still. Here we are.

## Requirements / installation

I use [`conda`](https://conda.io/) to handle dependencies.

Set up the environment the first time:

    # create the conda environment
    conda env create -f environment.yml

Source the environment to run the notebook:

    # activate the environment
    # bash:
    source activate MortgageWorksheet
    # powershell:
    activate.ps1 MortgageWorksheet

    # run the notebook
    jupyter notebook

    # deactivate the environment when finished
    deactivate

Update the environment (e.g. if the prereqs change):

    # update the conda environment
    conda env update -f environment.yml

### Other prerequisites

By default, we use OpenStreetMap.org, which can be used without authentication. If you wish to use Google maps instead, you must procure a [Google Maps API key](https://console.developers.google.com/flows/enableapi?apiid=maps_backend,geocoding_backend,directions_backend,distance_matrix_backend,elevation_backend&keyType=CLIENT_SIDE&reusekey=true), and enter it in the appropriate field in the notebook.

## Defining custom calculations

Items like closing costs and monthly expenditures are highly variable. Some defaults and reasonable general-purpose estimates are provided in hardcoded constants in modules, but it will be possible to specify more precise figures by adding them directly in the workbook (without needing to modify the Python modules).

Use YAML to create new monthly expenditures (and, soon, closing costs). See the YAML cells in the notebook, which precede the report, for examples.

You may want to consider the following monthly expenditures (from TBORPI pp. 100-101):

- Taxes
- Insurance
- Flood Insurance (if needed)
- Vacancy
- Repairs
- Capital expenditures
- Water
- Sewer
- Garbage
- Gas
- Electricity
- HOA (home owner’s association) fees (if applicable)
- Snow removal
- Lawn care
- Property management

Capital expenditures deserve special mention, because they can be broken out into individual items.
You may want to consider the following (from TBORPI p. 103):

- Roof
- Water heater
- Appliances (total)
- Driveway
- HVAC
- Flooring
- Plumbing
- Windows
- Paint
- Cabinets and countertops
- Structure (foundation and framing)
- Components (garage door etc)
- Landscaping

## Notes on recommendations

I get a lot of information from the fantastic [Book on Rental Property Investing](https://www.amazon.com/Book-Rental-Property-Investing-Intelligent/dp/099071179X?&_encoding=UTF8&tag=mrled-20&linkCode=ur2&linkId=3f16a626fa749912a1e1e10bbac44031&camp=1789&creative=9325). (TIA: affiliate link.) I occasionally refer to this as TBORPI for brevity.

## Roadmap

OK, I don't exactly have a roadmap, but I do have this.

WIP:

- Better way to handle multiple sets of closing costs and monthly expenses
    - Currently investigating YAML configuration for this
    - If we go down this route, consider using the voluptuous package to validate them (no external deps except nose!)
      <https://pypi.python.org/pypi/voluptuous/>

More stuff that I want to work on in the near future:

- Denote additional one-time payments
- Track forced appreciation (aka spending money to improve property value, e.g. by remodeling)
- Record various property facts: historical rent in area, historical sell price in area, etc
- Calculate ROI after certain period of time (e.g. closing costs + mortgage payments vs cash when you sell)
- Calculate COCROI (cash-on-cash ROI, aka the return on investment just off monthly cashflow, not including principal or appreciation)
- Show "percent rules" e.g. 1% rule or 3% rule or whatever - what percentage of total loan (or is it principal?) is monthly rent?
- Calculate some numbers for recommended reserve cash on hand - maybe start with a six-month recommendation (per TBORPI)
- UI to show details on "house hack" type properties
- UI for tracking projected rent

Some really nice stuff for later on might be:

- Automatically retrieve historical data about rents/sale prices in the area (from where?)
- Figure out a way to show ranges, e.g. if your mortgage broker gives you options varying in down payment size and
- Maybe something like this could help? https://www.housecanary.com/product-analytics-api#pricing-calculator
- Or perhaps this? https://developer.onboard-apis.com/pricing
- This looks good, and is free: https://www.zillow.com/howto/api/GetDeepSearchResults.htm
- Calculating exact property tax might be doable from this: https://comptroller.texas.gov/taxes/property-tax/rates/index.php
  however I don't know how to determine all the special districts that a property is part of
- This is for regular people, but has the same problem: https://tax-office.traviscountytx.gov/property-tax-estimator
- These pages might have info? http://www.txcip.org/tac/census/CountyProfiles.php
  for instance if I can figure out how to get this page for other counties: http://www.txcip.org/tac/census/districthist.php?FIPS=48439
