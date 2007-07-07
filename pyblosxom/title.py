"""
Provides me with a $urlencodedtitle which is better for the Google link.
It's a urlencoded title.

There's no configuration needed--you can drop this plugin into your
plugin dir and it'll work just fine.


NOTE: This plugin is not required if you're using PyBlosxom 1.3 and
later.


This plugin is placed in the Public Domain.


SUBVERSION VERSION: $Id$

Revisions:
2005-11-13 - Place into the Public Domain.
2005-11-11 - Pulled into new VCS.
1.3 - (26 October, 2005) pulled into new VCS
1.0 - created
"""
__author__ = "Will Guaraldi - willg at bluesock dot org"
__version__ = "$Date$"
__url__ = "http://www.bluesock.org/~willg/pyblosxom/"
__description__ = "Creates a $urlencodedtitle variable for Google links."

import urllib

def verify_installation(request):
    return 1

def cb_story(args):
    """
    This method gets called in the cb_story callback.  Refer to
    the documentation for that.
    """
    entry = args["entry"]

    if not entry.has_key("title"):
        entry["urlencodedtitle"] = "N/A"
        return

    entry["urlencodedtitle"] = urllib.quote(entry["title"])
