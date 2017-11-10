# Jupyter Mortgage Calculator

It's a work-in-progress Jupyter notebook for mortgage calculations.

You can use [Binder](https://mybinder.org/) to run this notebook online. No installation required!

[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/mrled/jupyter-mortgage/master?filepath=MortgageWorksheet.ipynb)

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

Sse the environment to run the notebook:

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

By default, we use OpenStreetMap.org, which can be used without authentication. If you wish to use Google maps instead, you must procure a ([Google Maps API key](https://console.developers.google.com/flows/enableapi?apiid=maps_backend,geocoding_backend,directions_backend,distance_matrix_backend,elevation_backend&keyType=CLIENT_SIDE&reusekey=true)), and enter it in the appropriate field in the notebook.

## Roadmap

OK, I don't actually have a roadmap, but here are a few things I would like to support in the future:

- Denote additional one-time payments
- Estimate other monthly expenses (mortgage insurance, homeowners insurance, etc)
- Estimate other expenditures and savings (utilities, saving for capex, etc)
- Track forced appreciation (aka spending money to improve property value, e.g. by remodeling)
- Record various property facts: historical rent in area, historical sell price in area, etc
- Calculate ROI after certain period of time (e.g. closing costs + mortgage payments vs cash when you sell)
- Calculate COCROI (cash-on-cash ROI, aka the return on investment just off monthly cashflow, not including principal or appreciation)

Some really nice stuff might be:
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
