#!/usr/bin/env python3

"""Jupyter wrappers for displaying mortgage information"""

import threading

from IPython.display import (
    HTML,
    display,
)
import ipywidgets
import ipyleaflet

import gmaps
from mako.template import Template

import mortgage
import streetmap


WIDGET_DESC_WIDTH = '10em'


def dollar(amount):
    """Return a string dollar amount from a float

    For example, dollar(1926.2311831442486) => "$1,926.23"

    We aren't too concerned about the lost accuracy;
    this function should only be used for *display* values

    NOTE: I'm not sure why, but I often find that if I don't wrap a dollar()
    call in <span> tags, Jupyter does something really fucked up to my text
    """
    return '${:,.2f}'.format(amount)


def html_hbox(text, style):
    """Create a styled HBox from a string containing HTML"""

    hbox = ipywidgets.HBox()
    hbox.children = [ipywidgets.HTML(text)]
    hbox.box_style = style
    return hbox


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
        $(document).ready(toggleinputs);
        </script>
        '''))

    # Show title, input code toggle message, and input code toggle button
    display(HTML('''
        <h2>Modifying this notebook</h2>

        <p>Input code for this notebook is by default hidden for easier reading.</p>
        <p>
            For simple inputs, you may not need to view the code;
            you can change values like sale price and APR using the GUI widgets.
            For more complex inputs, such as defining a new set of closing costs,
            you will need to enable input code display, and create a list of closing costs in inline Python.
        </p>
        <p>
            Note: If you're reading this message in another notebook frontend
            (for example, a static rendering on GitHub or NBViewer),
            you will not see the rest of the notebook.
            You must run the notebook from Jupyter itself.
        </p>
        <p><button onclick="toggleinputs()">Toggle input code display</button></p>
        <hr/>
        '''))


def wrap_close(saleprice, loanapr, loanterm, propertytaxes):
    """Show loan amounts and closing costs"""
    costs = mortgage.IRONHARBOR_FHA_CLOSING_COSTS
    monthterm = loanterm * mortgage.MONTHS_IN_YEAR
    result = mortgage.close(saleprice, loanapr, monthterm, propertytaxes, costs)

    templ = Template(filename='templ/close.mako')
    display(HTML(templ.render(closeresult=result)))

    return result


def wrap_schedule(apryearly, principal, years, overpayment, appreciation):
    """Show a loan's mortgage schedule in a Jupyter notebook"""

    term = years * mortgage.MONTHS_IN_YEAR
    overpayments = [overpayment for _ in range(term)]
    appreciationpct = appreciation / 100

    # Calculate the monthly payments for the mortgage schedule detail,
    # yearly payments for the mortgage schedule summary
    # and monthly payments with no overpayments for comparative analysis in prefacetempl
    months = [month for month in mortgage.schedule(
        apryearly, principal, term, overpayments=overpayments, appreciation=appreciationpct)]
    months_no_over = [month for month in mortgage.schedule(
        apryearly, principal, term, overpayments=None, appreciation=appreciationpct)]
    years = [year for year in mortgage.monthly2yearly_schedule(months)]

    prefacetempl = Template(filename='templ/schedule_preface.mako')
    schedtempl = Template(filename='templ/schedule.mako')

    # Display a preface / summary first
    display(HTML(prefacetempl.render(
        apryearly=apryearly,
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
        display(HTML(schedtempl.render(
            principal=principal,
            loanpayments=years,
            paymentinterval_name="Year")))
    with detailout:
        display(HTML(schedtempl.render(
            principal=principal,
            loanpayments=months,
            paymentinterval_name="Month")))

    parentwidg = ipywidgets.Accordion()
    parentwidg.children = [summaryout, detailout]
    parentwidg.set_title(0, 'Yearly summary')
    parentwidg.set_title(1, 'Monthly detail')
    display(parentwidg)


class StreetMapGlobalManager():
    """Street map global manager"""

    progress_widget = None
    stopevent = None
    container = None

    def stop(self):
        """Stop execution"""
        if self.progress_widget is not None:
            self.progress_widget.close()
        if self.stopevent is not None:
            self.stopevent.set()
        if self.container is not None:
            self.container.close()

    def reset(self, progwidg):
        """Stop and reset"""
        self.stop()
        self.stopevent = threading.Event()
        self.progress_widget = progwidg
        self.container = ipywidgets.VBox()
        display(self.container)
        self.container.children = [self.progress_widget]

_STREET_MAP_GLOBALS = StreetMapGlobalManager()


def wrap_streetmap(address, google_api_key, timerlength=3.0):
    """Show a streetmap after a timer has elapsed

    Every time this function is called, a global timer is started.
    If this function is called again before the timer elapses, the timer is canceled and restarted.
    When the timer does finally elapse, the street map is shown.

    address         location to display on the map
    google_api_key  a valid Google API key, or None
                    if the API key is valid, use Google maps; otherwise, use OpenStreetMaps
    timerlength     number of seconds to wait before the street map is displayed
    """

    def get_streetmap(address, google_api_key):
        """Show a streetmap"""

        # WARNING: widgets can NOT be displayed directly from a non-main thread!
        # Ref: https://github.com/jupyter-widgets/ipywidgets/issues/1790
        # Instead, we must create a container widget, and update its .children property
        # to contain the items we wish to display
        # To render HTML, we could place an ipywidgets.HTML() into the container, but that loses
        # the normal Jupyter styling for HTML elements - things like tables don't look as nice
        # We instead we render using IPython.display.display(HTML(...)), but we do so into an
        # ipywidgets.Output() which we then add to the container widget's .children

        container_children = []

        preface_html_out = ipywidgets.Output()
        with preface_html_out:
            if google_api_key != "":
                gmaps.configure(api_key=google_api_key)
                geocodes = streetmap.geocode_google(address, google_api_key)
                display(html_hbox("Google API key found - using Google maps", "info"))
            else:
                geocodes = streetmap.geocode_nominatim(address)
                display(html_hbox("Using OpenStreetMap for map data", "info"))

            if len(geocodes) < 1:
                display(html_hbox(f"Could not find property at {address}", "danger"))
            elif len(geocodes) > 1:
                display(html_hbox(f"{len(geocodes)} matches returned for {address}; all are displayed below", "warning"))

        container_children += [preface_html_out]

        for idx, geocode in enumerate(geocodes):
            propertyindex = None
            if len(geocodes) != 1:
                propertyindex = idx + 1

            property_html_out = ipywidgets.Output()
            templ = Template(filename='templ/propertyinfo.mako')
            with property_html_out:
                display(HTML(templ.render(
                    address=geocode.displayname,
                    county=geocode.county,
                    neighborhood=geocode.neighborhood,
                    coordinates=geocode.coordinates,
                    propertyindex=propertyindex)))

            if google_api_key != "":
                property_figure = gmaps.figure(center=geocode.coordinates, zoom_level=14)
                property_figure.add_layer(gmaps.marker_layer([geocode.coordinates]))
            else:
                property_figure = ipyleaflet.Map(center=geocode.coordinates, zoom=14)
                property_figure += ipyleaflet.Marker(location=geocode.coordinates)

            container_children += [property_html_out, property_figure]

        return container_children

    def streetmap_thread(address, google_api_key, timerlength, stopevent, progresswidget, container, updateinterval=0.2):
        """Update the streetmap progress widget"""

        # .wait() returns True when stopevent.set() is called from a different thread;
        # until then, it will block until updateinterval elapses, at which point it returns False
        while not stopevent.wait(updateinterval):

            progresswidget.value += updateinterval
            if progresswidget.value >= timerlength:
                # If the stop event did not fire, then we can execute the map display function
                container.children = get_streetmap(address, google_api_key)
                break

        progresswidget.close()

    global _STREET_MAP_GLOBALS
    _STREET_MAP_GLOBALS.reset(ipywidgets.FloatProgress(
        description='Loading map...', value=0.0, min=0.0, max=timerlength))

    progress_thread = threading.Thread(
        target=streetmap_thread,
        args=(
            address,
            google_api_key,
            timerlength,
            _STREET_MAP_GLOBALS.stopevent,
            _STREET_MAP_GLOBALS.progress_widget,
            _STREET_MAP_GLOBALS.container))
    progress_thread.start()


def propertyinfo():
    """Gather information about a property using Jupyter UI elements"""

    def metawrapper(loanapr, saleprice, years, overpayment, appreciation, propertytaxes, address, google_api_key):
        closed = wrap_close(saleprice, loanapr, years, propertytaxes)
        wrap_schedule(loanapr, closed.principal_total, years, overpayment, appreciation)
        wrap_streetmap(address, google_api_key)

    display(HTML(Template("templ/instructions.mako").render()))

    ipywidgets.interact(
        metawrapper,
        loanapr=ipywidgets.BoundedFloatText(
            value=3.75,
            min=0.01,
            step=0.25,
            description="APR",
            style={'description_width': WIDGET_DESC_WIDTH}),
        saleprice=ipywidgets.BoundedFloatText(
            value=250_000,
            min=1,
            max=1_000_000_000,
            step=1000,
            description="Sale price",
            style={'description_width': WIDGET_DESC_WIDTH}),
        years=ipywidgets.Dropdown(
            options=[15, 20, 25, 30],
            value=30,
            description="Loan term in years",
            style={'description_width': WIDGET_DESC_WIDTH}),
        overpayment=ipywidgets.BoundedIntText(
            value=50,
            min=0,
            max=1_000_000,
            step=5,
            description="Monthly overpayment amount",
            style={'description_width': WIDGET_DESC_WIDTH}),
        appreciation=ipywidgets.BoundedFloatText(
            value=0.5,
            min=-20.0,
            max=20.0,
            step=0.5,
            description="Yearly appreciation",
            style={'description_width': WIDGET_DESC_WIDTH}),
        propertytaxes=ipywidgets.BoundedIntText(
            value=5500,
            min=0,
            max=1_000_000,
            step=5,
            description="Yearly property taxes",
            style={'description_width': WIDGET_DESC_WIDTH}),
        address=ipywidgets.Text(
            value="1600 Pennsylvania Ave NW, Washington, DC 20500",
            description="Address",
            style={'description_width': WIDGET_DESC_WIDTH}),
        google_api_key=ipywidgets.Text(
            value="",
            description="Google API key",
            style={'description_width': WIDGET_DESC_WIDTH}))
