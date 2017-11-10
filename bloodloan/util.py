#!/usr/bin/env python3

"""Utilities for jupyter-mortgage"""

import threading

from IPython.display import display
import ipywidgets

from bloodloan.log import LOG as log


class DelayedExecutor():
    """Manage delayed execution

    Display widgets/outputs after a timer has elapsed
    If .run() is called a second time while the timer is still running,
    cancel the first .run() call and start a new one
    """

    def __init__(self):
        self.container = ipywidgets.VBox()
        self.stopevent = threading.Event()
        self.output = None
        self.thread = None
        self.progresswidget = None

    def run(
            self,
            progress_desc,
            action,
            action_args=None,
            action_kwargs=None,
            timerlength=2.0,
            timerinterval=0.2):
        """Run an action in a thread after a delay and display output to an existing container

        WARNING: widgets can NOT be displayed directly from a non-main thread!
        Ref: https://github.com/jupyter-widgets/ipywidgets/issues/1790
        Instead, we must create a container widget, and then within the thread we can
        update its .children property to contain the items we wish to display

        output              an ipywidgets.Output which the caller is responsible for display()ing
        progress_desc       description for the progress widget
        action              a function to call when the timer elapses
                            it should NOT display widgets directly,
                            but should return a list of widgets/outputs
                            that can be passed to output.append_display_data()
        action_args         a tuple of positional arguments for action
        action_kwargs       a dict of keyword arguments for action
        timerlength         length of delay
        timerinterval       update the progress widget this often
        """

        self.progresswidget = ipywidgets.FloatProgress(
            description=progress_desc, value=0.0, min=0.0, max=timerlength)

        action_args = action_args or ()
        action_kwargs = action_kwargs or {}

        self.stopevent.set()
        if self.thread is not None:
            # block until self.thread terminates (for self.timerinterval secs or shorter)
            log.info("Stopping old thread...")
            self.thread.join()
            log.info("Old thread stopped")
        self.stopevent.clear()

        # Wait to reset value / display the widget until the previous thread is cleaned up
        self.progresswidget.value = 0.0
        display(self.progresswidget)

        self.output = ipywidgets.Output()
        display(self.output)

        self.thread = threading.Thread(target=self.timer, args=(
            timerinterval, timerlength, action, action_args, action_kwargs))
        self.thread.start()

    def timer(self, timerinterval, timerlength, action, action_args, action_kwargs):
        """Start the timer, run the action, and append the results

        timerlength     length of delay
        timerinterval   update the progress widget this often
        action          a function to call when the timer elapses
        action_args     a tuple containing positional arguments to action
        action_kwargs   a dict containing keyword arguments to action
        """

        closed_widget = False

        # .wait() returns True when stopevent.set() is called from a different thread;
        # until then, it will block until updateinterval elapses, at which point it returns False
        while not self.stopevent.wait(timerinterval):

            self.progresswidget.value += timerinterval
            if self.progresswidget.value >= timerlength:
                log.info("Stop event did not fire - calling action()")
                closed_widget = True
                self.progresswidget.close()
                results = action(*action_args, **action_kwargs)
                log.info(f"Got {len(results)} children to display in thread output container")
                for result in results:
                    self.output.append_display_data(result)
                self.stopevent.set() # Stop the loop
                log.info("Sent stop event from within timer() - all done")

        if not closed_widget:
            self.progresswidget.close()


def html_hbox(text, style):
    """Create a styled HBox from a string containing HTML

    text    string containing HTML
    style   a valid box_style value for the HBox
            one of information, success, warning, failure
    """

    hbox = ipywidgets.HBox()
    hbox.children = [ipywidgets.HTML(text)]
    hbox.box_style = style
    return hbox


def label_widget(label, container, widget):
    """Create a non-fixed-width label for a widget

    Unlike the description= argument that can be passed to widgets, the label should expand in size
    to meet the width of the container

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
