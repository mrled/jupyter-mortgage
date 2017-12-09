"""Parameters for the mortgage worksheet
"""

import ipywidgets


class Params:
    """Parameter widgets for the mortgage worksheet
    """

    def __init__(self, cost_config_names=None):

        self.widgets_box = ipywidgets.Box(layout=ipywidgets.Layout(
            display='flex',
            flex_flow='column',
            align_items='stretch',
            width='70%'))

        self.interestrate = Params._label_widget(
            "Interest rate", self.widgets_box, ipywidgets.BoundedFloatText(
                value=3.75,
                min=0.01,
                step=0.25))
        self.saleprice = Params._label_widget(
            "Sale price", self.widgets_box, ipywidgets.BoundedFloatText(
                value=250_000,
                min=1,
                max=1_000_000_000,
                step=1000))
        self.rent = Params._label_widget(
            "Project rent", self.widgets_box, ipywidgets.BoundedIntText(
                value=0,
                min=0,
                max=10_000))
        self.years = Params._label_widget(
            "Loan term in years", self.widgets_box, ipywidgets.Dropdown(
                options=[15, 20, 25, 30],
                value=30))
        self.overpayment = Params._label_widget(
            "Monthly overpayment amount", self.widgets_box, ipywidgets.BoundedIntText(
                value=50,
                min=0,
                max=1_000_000,
                step=5))
        self.appreciation = Params._label_widget(
            "Yearly appreciation", self.widgets_box, ipywidgets.BoundedFloatText(
                value=0.5,
                min=-20.0,
                max=20.0,
                step=0.5))
        self.propertytaxes = Params._label_widget(
            "Yearly property taxes", self.widgets_box, ipywidgets.BoundedIntText(
                value=5500,
                min=0,
                max=1_000_000,
                step=5))
        self.address = Params._label_widget(
            "Property address", self.widgets_box, ipywidgets.Textarea(
                value="1600 Pennsylvania Ave NW, Washington, DC 20500"))
        self.google_api_key = Params._label_widget(
            "Google API key (optional)", self.widgets_box, ipywidgets.Text(
                value=""))
        self.costs = Params._label_widget(
            "Cost configurations", self.widgets_box, ipywidgets.SelectMultiple(
                options=cost_config_names or []))

    @staticmethod
    def _label_widget(label, container, widget):
        """Create a non-fixed-width label for a widget

        Unlike the description= argument that can be passed to widgets, the label should expand in
        size to meet the width of the container

        label       text for a new ipywidgets.Label for the widget
        container   a pre-created ipywidgets.Box to which the label and widget will be added
                    (NOTE: this function does not display this container)
                    for example:
        widget      a pre-created widget

        Example:
            widgets_box = ipywidgets.Box(layout=ipywidgets.Layout(
                display='flex', flex_flow='column', align_items='stretch', width='70%'))
            propertytaxes = label_widget(
                "Yearly property taxes", widgets_box, ipywidgets.BoundedIntText(
                    value=5500, min=0, max=1_000_000, step=5))
        """
        box = ipywidgets.Box()
        box.children = [ipywidgets.Label(label), widget]
        container.children += (box,)
        box.layout = ipywidgets.Layout(
            display='flex',
            flex_flow='row',
            justify_content='space-between')
        return widget
