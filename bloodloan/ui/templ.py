"""Templ: a Temple of Templates
"""

import os

from mako.template import Template


SCRIPTDIR = os.path.dirname(os.path.realpath(__file__))
TEMPL = os.path.join(SCRIPTDIR, 'templ')


class Templ:
    """A list of templates
    """

    Close = Template(filename=os.path.join(TEMPL, 'close.mako'))
    SchedulePreface = Template(filename=os.path.join(TEMPL, 'schedule_preface.mako'))
    Schedule = Template(filename=os.path.join(TEMPL, 'schedule.mako'))
    MonthlyCosts = Template(filename=os.path.join(TEMPL, 'monthlycosts.mako'))
    Instructions = Template(filename=os.path.join(TEMPL, 'instructions.mako'))
