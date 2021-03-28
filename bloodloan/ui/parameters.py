"""Parameters for the mortgage worksheet
"""

import io
import logging
import os

import ipywidgets
import yaml


logger = logging.getLogger(__name__)  # pylint: disable=C0103


class ParamMetadata:
    """Metadata required to build a parameter widget

    widgetid        a widget's ID (ParameterIds.WIDGET_NAME)
    label           a text label for the widget
    widgetcls       the widget's class, like ipywidgets.BoundedIntText
    widgetkwargs    kwargs to the widget's constructor
    """

    def __init__(self, widgetid, label, widgetcls, widgetkwargs):
        self.widgetid = widgetid
        self.label = label
        self.cls = widgetcls
        self.kwargs = widgetkwargs


class ParameterIds:
    """Parameter names
    """

    INTEREST_RATE = 'interest_rate'
    SALE_PRICE = 'sale_price'
    RENT = 'rent'
    TERM = 'term'
    OVERPAYMENT = 'overpayment'
    APPRECIATION = 'appreciation'
    PROPERTY_TAXES = 'property_taxes'
    ADDRESS = 'address'
    GOOGLE_API_KEY = 'google_api_key'
    COSTS = 'costs'


class Params:
    """Parameter widgets for the mortgage worksheet
    """

    def __init__(self, persist_path=None, cost_config_names=None):

        cost_config_names = cost_config_names or []

        persisted = {}
        self.persist_path = persist_path
        if self.persist_path:

            if not os.path.exists(self.persist_path):
                logger.debug(f"The persisted values path {self.persist_path} did not exist")
                persist_dir, _ = os.path.split(self.persist_path)
                os.makedirs(persist_dir, exist_ok=True)
                with open(self.persist_path, 'w') as ppfile:
                    ppfile.write(yaml.dump({}))
                persisted = {}

            with open(self.persist_path) as ppfile:
                try:
                    persisted = yaml.load(ppfile, Loader=yaml.UnsafeLoader)
                    logger.debug(f"Loaded persisted data from {self.persist_path}: {persisted}")
                except io.UnsupportedOperation as exc:
                    logger.debug(f"Could not load persisted data from {self.persist_path}: {exc}")
                    persisted = {}
            if persisted == {}:
                with open(self.persist_path, 'w') as ppfile:
                    ppfile.write(yaml.dump({}))

        logger.debug(f"When initializing parameters, found persisted values: {persisted}")

        self.params_box = ipywidgets.Box(layout=ipywidgets.Layout(
            display='flex',
            flex_flow='column',
            align_items='stretch',
            width='70%'))

        widgetmds = [
            ParamMetadata(
                ParameterIds.INTEREST_RATE, "Interest rate",
                ipywidgets.BoundedFloatText, {'min': 0.01, 'step': 25, 'value': 3.75}),
            ParamMetadata(
                ParameterIds.SALE_PRICE, "Sale price",
                ipywidgets.BoundedFloatText,
                {'min': 1, 'max': 1_000_000_000, 'step': 1000, 'value': 250_000}),
            ParamMetadata(
                ParameterIds.RENT, "Projected rent",
                ipywidgets.BoundedIntText, {'min': 0, 'max': 10_000, 'step': 25, 'value': 0}),
            ParamMetadata(
                ParameterIds.TERM, "Loan term in years",
                ipywidgets.Dropdown, {'options': [15, 20, 25, 30], 'value': 30}),
            ParamMetadata(
                ParameterIds.OVERPAYMENT, "Monthly overpayment amount",
                ipywidgets.BoundedIntText, {'min': 0, 'max': 10_000, 'step': 25, 'value': 0}),
            ParamMetadata(
                ParameterIds.APPRECIATION, "Yearly appreciation",
                ipywidgets.BoundedFloatText,
                {'min': -20.0, 'max': 20.0, 'step': 0.5, 'value': 0.5}),
            ParamMetadata(
                ParameterIds.PROPERTY_TAXES, "Property taxes",
                ipywidgets.BoundedFloatText,
                {'min': 0.0, 'max': 10.0, 'step': 0.01, 'value': 0.0}),
            ParamMetadata(
                ParameterIds.ADDRESS, "Property address",
                ipywidgets.Textarea, {'value': ""}),
            ParamMetadata(
                ParameterIds.GOOGLE_API_KEY, "Google API key (optional)",
                ipywidgets.Text, {'value': ""}),
            ParamMetadata(
                ParameterIds.COSTS, "Cost configurations",
                ipywidgets.SelectMultiple, {'options': cost_config_names, 'value': []}),
        ]

        for widgetmd in widgetmds:

            # Obtain a persisted default value, if one exists,
            # and add it to the widget constructor kwargs.
            # This means we override any 'value': specified in the metadata.
            # Take care to be able to differentiate between a saved empty value and
            # a nonexistent default value.
            try:
                value = persisted[widgetmd.widgetid]
                widgetmd.kwargs['value'] = value
                logger.debug(f"Found persisted value '{value}' for {widgetmd.widgetid}")
            except KeyError:
                logger.debug(f"Could not find persisted value for {widgetmd.widgetid}")
            except Exception as exc:
                raise Exception(f"Failure working with {widgetmd.widgetid}: {exc}")

            # Create the widget object
            widget = widgetmd.cls(**widgetmd.kwargs)

            # Create a Box to hold widget + label, then place that box in our container
            box = ipywidgets.Box()
            box.children = [ipywidgets.Label(widgetmd.label), widget]
            box.layout = ipywidgets.Layout(
                display='flex',
                flex_flow='row',
                justify_content='space-between')
            self.params_box.children += (box,)

            # Add the widget as a named property to self so we can access it later
            # For instance, to access the costs widget, we could reference self.costs
            setattr(self, widgetmd.widgetid, widget)

    def persist(self, paramid, value):
        """Persist a parameter value to disk
        """
        if not self.persist_path:
            logger.debug(
                f"Cannot persist {paramid} with value '{value}' because persist_path was not set")
            return
        logger.debug(f"Persisting {paramid} with value '{value}'")

        with open(self.persist_path) as ppfile:
            persisted = yaml.load(ppfile, Loader=yaml.UnsafeLoader)
        persisted[paramid] = value
        with open(self.persist_path, 'w') as ppfile:
            ppfile.write(yaml.dump(persisted))
