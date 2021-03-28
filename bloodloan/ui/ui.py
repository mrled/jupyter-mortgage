#!/usr/bin/env python3

"""Jupyter wrappers for displaying mortgage information"""

import logging
import os

from IPython.display import (
    HTML,
    display,
)
import ipywidgets

from bloodloan import util
from bloodloan.mortgage import closing
from bloodloan.mortgage import costconfig
from bloodloan.mortgage import mmath
from bloodloan.mortgage import schedule
from bloodloan.ui import streetmap
from bloodloan.ui.parameters import Params, ParameterIds
from bloodloan.ui.templ import Templ


logger = logging.getLogger(__name__)  # pylint: disable=C0103


def getlogconfig(
        notebookdir,
        logfile='log.txt',
        fmt='%(levelname)s %(asctime)s %(filename)s:%(lineno)s:%(funcName)s(): %(message)s',
        datefmt='%Y%m%d-%H%M%S',
        maxbytes=10 * 1024 * 1024,  # 10MB
        backupcount=1,
        level='DEBUG'):
    """Get the bloodloan logging configuration

    notebookdir     the location of the Jupyter notebook
    logfile         the filename to use, inside of notebookdir, for the log
    fmt             a valid log format
    datefmt         a valid date format
    maxbytes        maximum size of each log file
    backupcount     number of backups to make; cannot be zero or log will grow forever
    level           a valid log level

    returns         a dict that can be passed to logging.config.dictConfig
    """

    return {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {'mort_formatter': {
            'format': fmt,
            'datefmt': datefmt,
        }},
        'handlers': {
            'mort_file_handler': {
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'mort_formatter',
                'filename': os.path.join(notebookdir, logfile),
                'maxBytes': maxbytes,
                'backupCount': backupcount,
            }
        },
        'root': {
            'level': level,
            'handlers': ['mort_file_handler']
        }
    }


def disablecellscroll():
    """Disable in-cell scrolling"""

    display(HTML('''
        <script>
        IPython.OutputArea.prototype._should_scroll = function(lines) {
            return false;
        }
        </script>
        '''))


def toggleinputcells():
    """Enable toggling input cells"""

    # Enable toggling display of input cells
    display(HTML('''
        <script>
        show_inputs = true;
        function toggleinputs() {
            if (show_inputs){
                $('div.input').hide();
            } else {
                $('div.input').show();
            }
            show_inputs = !show_inputs;
        }
        // Uncomment this to automatically hide input cells when notebook is run:
        //$(document).ready(toggleinputs);
        </script>
        '''))

    # Show title, input code toggle message, and input code toggle button
    display(HTML('''
        <h2>Modifying this notebook</h2>

        <p>Input code for this notebook can be hidden for easier reading (and printing).</p>
        <p>
            For simple inputs, you may not need to view the code;
            you can change values like sale price and interest rate using the GUI widgets.
            For more complex inputs, such as defining a new set of closing costs,
            you will need to enable input code display, and create a list of closing costs in inline Python.
        </p>
        <p><button onclick="toggleinputs()">Toggle input code display</button></p>
        <hr/>
        '''))


def wrap_close(saleprice, interestrate, loanterm, propertytaxes, closingcosts):
    """Show loan amounts and closing costs"""
    monthterm = loanterm * mmath.MONTHS_IN_YEAR
    result = closing.close(saleprice, interestrate, monthterm, propertytaxes, closingcosts)
    display(HTML(Templ.Close.render(closeresult=result)))

    return result


def wrap_schedule(
        interestrate,
        value,
        principal,
        saleprice,
        years,
        overpayment,
        appreciation,
        monthlycosts,
        rent):
    """Show a loan's mortgage schedule in a Jupyter notebook"""

    term = years * mmath.MONTHS_IN_YEAR
    overpayments = [overpayment for _ in range(term)]

    # Calculate the monthly payments for the mortgage schedule detail,
    # yearly payments for the mortgage schedule summary
    # and monthly payments with no overpayments for comparative analysis in prefacetempl
    months = [month for month in schedule.schedule(
        interestrate, value, principal, saleprice, term,
        overpayments=overpayments, appreciation=appreciation, monthlycosts=monthlycosts,
        monthlyrent=rent)]
    months_no_over = [month for month in schedule.schedule(
        interestrate, value, principal, saleprice, term,
        overpayments=None, appreciation=appreciation,
        monthlyrent=rent)]
    years = [year for year in schedule.monthly2yearly_schedule(months)]

    # Display a preface / summary first
    display(HTML(Templ.SchedulePreface.render(
        interestrate=interestrate,
        principal=principal,
        term=term,
        overpayment=overpayment,
        appreciation=appreciation,
        monthlypayments=months,
        monthlypayments_no_over=months_no_over)))

    # Create new Output objects, and call display(HTML(...)) in them
    # We do this because IPython.display.HTML() has nicer talbles
    # than ipywidgets.HTML(), but only ipywidgets-type widgets can be put
    # into an Accordion.
    summaryout = ipywidgets.Output()
    detailout = ipywidgets.Output()
    with summaryout:
        display(HTML(Templ.Schedule.render(
            principal=principal,
            value=value,
            loanpayments=years,
            paymentinterval_name="Year")))
    with detailout:
        display(HTML(Templ.Schedule.render(
            principal=principal,
            value=value,
            loanpayments=months,
            paymentinterval_name="Month")))

    parentwidg = ipywidgets.Accordion()
    parentwidg.children = [summaryout, detailout]
    parentwidg.set_title(0, 'Yearly summary')
    parentwidg.set_title(1, 'Monthly detail')
    display(parentwidg)

    return months


def wrap_monthly_expense_breakdown(costs, rent, mortgagepmt):
    """Show monthly expense breakdown

    costs           list of monthly costs
    rent            projected monthly rent
    mortgagepmt     regular mortgage payment amount
    """
    display(HTML(Templ.MonthlyCosts.render(costs=costs, rent=rent, mortgagepmt=mortgagepmt)))


def get_displayable_geocode(geocode, title):
    """Retrieve display()-able streetmap and property information for a list of geocodes

    geocodes    list of GeocodeResult objects
    title       value for an <h3> element

    return      an OutputChildren, for adding to the .children property of an ipywidgets.Box
    """
    result = util.OutputChildren()

    result.display(HTML(f"<h3>{title}</h3>"))
    result.display(HTML(f"<p><em>{geocode.displayname}</em></p>"))

    property_info = ipywidgets.Box(layout=ipywidgets.Layout(
        display='flex',
        flex_flow='column',
        align_items='stretch',
        width='20em'))

    def info_row(label, value):
        """Return an informational row for displaying property info"""
        return ipywidgets.Box(
            children=(
                ipywidgets.Label(label),
                ipywidgets.Label(value)),
            layout=ipywidgets.Layout(
                display='flex',
                flex_flow='row',
                justify_content='space-between'))

    property_info.children = (
        info_row("County", geocode.county),
        info_row("Neighborhood", geocode.neighborhood),
        info_row("Latitude", geocode.coordinates[0]),
        info_row("Longitude", geocode.coordinates[1]))

    result.display(property_info)
    result.display(geocode.figure)

    return result


def wrap_streetmap(address):
    """Show street maps and property information"""

    logger.debug("Instantiating mapper...")
    mapper = streetmap.OpenStreetMapper()
    logger.debug("Getting geocode...")
    geocodes = mapper.geocode(address)
    logger.debug(f"Got geocode: {geocodes}")

    result = util.OutputChildren()
    result.display(util.html_hbox(f"Using {mapper} for maps", "info"))
    result.display(HTML(f"<h2>Map & property information</h2>"))

    if len(geocodes) < 1:
        result.display(
            util.html_hbox(f"Could not find property at {address}", "danger"))
    elif len(geocodes) > 1:
        result.display(
            util.html_hbox(f"{len(geocodes)} matches returned for {address}", "warning"))

    for idx, geocode in enumerate(geocodes):
        if len(geocodes) != 1:
            maptitle = f"Property {idx + 1}</h3>"
        else:
            maptitle = "Property information"
        result += get_displayable_geocode(geocode, maptitle)

    return result


def propertyinfo(

        # Notebook parameters:
        interestrate,
        saleprice,
        rent,
        years,
        overpayment,
        appreciation,
        propertytaxes,
        address,
        selected_cost_configs,

        # Other data passing:
        cost_configs,
        parameters,
        street_map_executor,
        ):
    """Gather information about a property"""

    parameters.persist(ParameterIds.INTEREST_RATE, interestrate)
    parameters.persist(ParameterIds.SALE_PRICE, saleprice)
    parameters.persist(ParameterIds.RENT, rent)
    parameters.persist(ParameterIds.TERM, years)
    parameters.persist(ParameterIds.OVERPAYMENT, overpayment)
    parameters.persist(ParameterIds.APPRECIATION, appreciation)
    parameters.persist(ParameterIds.PROPERTY_TAXES, propertytaxes)
    parameters.persist(ParameterIds.ADDRESS, address)
    parameters.persist(ParameterIds.COSTS, selected_cost_configs)

    logger.info("Recalculating...")

    interestrate = mmath.percent2decimal(interestrate)
    appreciation = mmath.percent2decimal(appreciation)

    # TODO: split out display and calculation
    #       We're getting values like the 'closed' and 'months' variables from functions that
    #       also display data to the end user;
    #       instead, we should calculated them all at once and then display the results

    costs = cost_configs.get(selected_cost_configs)
    logger.info(costs)
    closed = wrap_close(saleprice, interestrate, years, propertytaxes, costs.closing)

    # TODO: currently assuming sale price is value; allow changing to something else
    months = wrap_schedule(
        interestrate, saleprice, closed.principal_total, saleprice, years, overpayment,
        appreciation, costs.monthly, rent)

    wrap_monthly_expense_breakdown(months[0].othercosts, rent, months[0].regularpmt)

    if address:
        logger.debug(f"Mapping address of {address}")
        streetmap_container = ipywidgets.Box()
        logger.debug("Running the street map executor...")
        street_map_executor.run(
            streetmap_container,
            "Loading maps...",
            wrap_streetmap,
            action_args=(address))
        display(streetmap_container)
    else:
        logger.debug("No address to map")


def main(worksheetdir):
    """Gather information about a property using Jupyter UI elements"""

    display(HTML(Templ.Instructions.render()))

    costconfigs = costconfig.CostConfigurationCollection(
        directory=os.path.join(worksheetdir, 'configs'))
    params = Params(
        persist_path=os.path.join(worksheetdir, '.param_persist'),
        cost_config_names=[config.label for config in costconfigs.configs])
    street_map_executor = util.DelayedExecutor()

    # WARNING: DISABLING ERRORS FOR 'Instance of <class> has no <member> member'
    # FOR REMAINDER OF FILE!
    # (We use setattr() to set the members of the params object, so pylint can't see them)
    # pylint: disable=E1101

    output = ipywidgets.interactive_output(propertyinfo, {

        # Notebook parameters (passed directly)
        'interestrate': params.interest_rate,
        'saleprice': params.sale_price,
        'rent': params.rent,
        'years': params.term,
        'overpayment': params.overpayment,
        'appreciation': params.appreciation,
        'propertytaxes': params.property_taxes,
        'address': params.address,
        'selected_cost_configs': params.costs,

        # Other data passing (must be fixed)
        'cost_configs': ipywidgets.fixed(costconfigs),
        'parameters': ipywidgets.fixed(params),
        'street_map_executor': ipywidgets.fixed(street_map_executor),
    })

    display(params.params_box, output)
