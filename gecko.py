"""
This generates a notice for folks who are not using a Gecko based browser
that they should switch.

The notice will be stored in $gecko_notice .


Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify,
merge, publish, distribute, sublicense, and/or sell copies of the
Software, and to permit persons to whom the Software is furnished
to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Copyright 2004 Will Guaraldi

SUBVERSION VERSION $Id$

Revisions:
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
