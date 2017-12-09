#!/usr/bin/env python3

"""Utilities for jupyter-mortgage"""

import logging
import threading

from IPython.display import display
import ipywidgets


logger = logging.getLogger(__name__)  # pylint: disable=C0103


class DelayedExecutor():
    """Manage delayed execution

    Display widgets/outputs after a timer has elapsed
    If .run() is called a second time while the timer is still running,
    cancel the first .run() call and start a new one
    """

    def __init__(self):
        self.container = ipywidgets.VBox()
        self.stopevent = threading.Event()
        self.thread = None
        self.progbar_container = None
        self.progresswidget = None

    def run(
            self,
            output_container,
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

        output_container    an ipywidgets.Box which the caller is responsible for displaying
        progress_desc       description for the progress widget
        action              a function to call when the timer elapses
                            it should NOT display widgets directly,
                            but should return a list of widgets/outputs
                            that can be append to output_container.children
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
            logger.info("Stopping old thread...")
            self.thread.join()
            logger.info("Old thread stopped")
        self.stopevent.clear()

        self.progresswidget.value = 0.0

        # Create new containers for our progress bar and thread output,
        # put those in self.container,
        # and append self.container to output_container.children,
        # thereby throwing away existing *_container objects from a previous run()
        # This lets us overwrite the children of self.container,
        # without losing any preexisting children in container
        self.progbar_container = ipywidgets.Box()
        self.container.children = (self.progbar_container,)
        output_container.children += (self.container,)

        self.progbar_container.children = (self.progresswidget,)

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

        # .wait() returns True when stopevent.set() is called from a different thread;
        # until then, it will block until updateinterval elapses, at which point it returns False
        while not self.stopevent.wait(timerinterval):

            self.progresswidget.value += timerinterval
            if self.progresswidget.value >= timerlength:
                logger.info("Stop event did not fire - calling action()")
                self.container.children = ()
                result = action(*action_args, **action_kwargs)
                logger.info(f"Got {len(result)} children to display in thread output container")
                self.container.children = result
                self.stopevent.set() # Stop the loop
                logger.info("Sent stop event from within timer() - all done")

        self.progbar_container.children = ()


class OutputChildren(list):
    """Helper class for building a tuple that can be added to an ipywidgets.Box.children"""

    def display(self, displayable):
        """Display an object to a new ipywidgets.Output(), and add that output to self"""
        output = ipywidgets.Output()
        with output:
            display(displayable)
        self.append(output)

    def tuple(self):
        """Convert the internal list to a tuple, before adding to an ipywidgets.Box.children"""
        return tuple(self)


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
