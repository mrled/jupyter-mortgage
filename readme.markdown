# Jupyter Mortgage Calculator

It's a work-in-progress Jupyter notebook for mortgage calculations.

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

I use Python 3.9

```sh
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt

# run the notebook
jupyter notebook
```

### Other prerequisites

By default, we use OpenStreetMap.org, which can be used without authentication. If you wish to use Google maps instead, you must procure a [Google Maps API key](https://console.developers.google.com/flows/enableapi?apiid=maps_backend,geocoding_backend,directions_backend,distance_matrix_backend,elevation_backend&keyType=CLIENT_SIDE&reusekey=true), and enter it in the appropriate field in the notebook.

## Defining custom calculations

Items like closing costs and monthly expenditures are highly variable.
We include some default sets of costs in the configs/ directory;
feel free to add your own.

Cost configs are written in YAML.
See existing cost configs for examples.

At some point, we would like to add the ability to define cost configs elsewhere,
like maybe a [gist](https://gist.github.com) or some other easy way to store text snippets on the web,
and reference them from within the notebook.

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

See [TODO](doc/todo.markdown)
