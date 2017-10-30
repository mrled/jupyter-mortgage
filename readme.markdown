# Jupyter Mortgage Calculator

It's a work-in-progress Jupyter notebook for mortgage calculations.

I told Josiah I was doing this:
    
> Writing a mortgage calculator in a Jupyter notebook
>
> Which… might not be a great use of my time
>
> But I decided it was more fun than learning the Excel macro language, so here we are

He was not impressed:

> I’m
>
> Um
>
> It’s Friday night

But still. Here we are.

## Requirements / installation

- Python3
- Python packages:
    - Jupyter
    - gmaps
    - googlemaps
    - namedtupled
- Jupyter packages:
    - widgetsnbextension
- A Google Maps API key ([create one here](https://console.developers.google.com/flows/enableapi?apiid=maps_backend,geocoding_backend,directions_backend,distance_matrix_backend,elevation_backend&keyType=CLIENT_SIDE&reusekey=true) for obtaining one)

You should install Python3 using whatever is normal for your operating system, or directly from <https://python.org>. Once it's installed, you can install the remaining dependencies in a Python virtual environment:

    python3 -m ensurepip
    python3 -m pip install virtualenv
    python3 -m virtualenv venv
    . venv/bin/activate
    pip install jupyter gmaps googlemaps namedtupled
    jupyter nbextension install --py widgetsnbextension --user
    jupyter nbextension enable --py gmaps
    jupyter nbextension enable --py widgetsnbextension

# Running

First, activate the virtual environment. This must be done once per shell, so if you're in the same shell session that you used to install the prereqs, you will not need to do this. That said, it doesn't hurt to do it more than once.

    . venv/bin/activate

Next, set an environment variable to hold your Google Maps API key:

    export GOOGLE_API_KEY=AI...

And then run Jupyter like normal:

    jupyter notebook

Finally, find the Jupyter notebook itself. Click on the `MortgageWorksheet.ipynb` file in the webpage that the previous step should have popped up.

## Roadmap

OK, I don't actually have a roadmap, but here are a few things I would like to support in the future:

- Denote additional one-time payments
- Estimate other monthly expenses (mortgage insurance, homeowners insurance, etc)
- Estimate other expenditures and savings (utilities, saving for capex, etc)
- Estimate closing costs
- Track forced appreciation (aka spending money to improve property value, e.g. by remodeling)
- Track estimated natural appreciation (e.g. allow an assumption that the property will appreciate by X%/year)
- Record various property facts: location, historical rent in area, historical sell price in area, etc
- Calculate ROI after certain period of time (e.g. closing costs + mortgage payments vs cash when you sell)
- Calculate COCROI (cash-on-cash ROI, aka the return on investment just off monthly cashflow, not including principal or appreciation)

Some really nice stuff might be:
- Automatically retrieve historical data about rents/sale prices in the area (from where?)
- Figure out a way to show ranges, e.g. if your mortgage broker gives you options varying in down payment size and 
