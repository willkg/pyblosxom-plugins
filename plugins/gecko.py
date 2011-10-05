"""
Summary
=======

This plugin is maintained at:

   http://www.bluesock.org/~willg/pyblosxom/

Check that URL for new versions, better documentation, and submitting
bug reports and feature requests.


Usage
=====

This generates a notice for folks who are not using a Gecko based browser
that they should switch.

The notice will be stored in $gecko_notice .

----

This plugin is placed in the Public Domain.  Do with it as you will.


SUBVERSION VERSION $Id$

Revisions:
2005-11-13 - Placed in the Public Domain.
2005-11-11 - Pulled into another new version control system.
1.5 - (26 October, 2005) pulled into new version control system
1.0 - (08 July, 2004) created
"""
__author__ = "Will Guaraldi - willg at bluesock dot org"
__version__ = "$Date$"
__url__ = "http://www.bluesock.org/~willg/pyblosxom/"
__description__ = "Displays a notice for people who aren't using Gecko-based browsers."

import os

def generate_notice():
    agent = os.environ.get("HTTP_USER_AGENT", "")
    if agent.lower().find("gecko") == -1:
        return """You should be using <a href="http://www.mozilla.org/">Firefox</a>."""
    return ""

def cb_head(args):
    """
    This method gets called in the cb_story callback.  Refer to
    the documentation for that.
    """
    entry = args["entry"]
    entry["gecko_notice"] = generate_notice()

def cb_foot(args):
    return cb_head(args)
