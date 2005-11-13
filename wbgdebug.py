"""
This plugin is triggered by "debug=yes" in the query string.  It'll
change the renderer being used to the Debug renderer.

It makes programming some things _much_ easier.

There's no configuration required for this plugin--you can drop it in
your plugin dir and it'll work just fine.


This plugin is placed in the Public Domain.


SUBVERSION VERSION: $Id$

Revisions:
2004-11-13 - Put into the Public Domain.
2005-11-11 - Pulled into new VCS.
1.5 - (26 October, 2005) pulled into new VCS
1.0 - (26 January 2004) initial writing
"""
__author__ = "Will Guaraldi - willg at bluesock dot org"
__version__ = "$Date$"
__url__ = "http://www.bluesock.org/~willg/pyblosxom/"
__description__ = "Allows for switching on the debug renderer using debug=yes in the querystring."

import sys
from Pyblosxom import tools

def verify_installation(request):
    return 1

def cb_renderer(args):
    request = args["request"]
    config = request.getConfiguration()
    pyhttp = request.getHttp()

    q = pyhttp["QUERY_STRING"].lower()
    if q.find("debug=yes") >= 0:
        return tools.importName("Pyblosxom.renderers", "debug").Renderer(request, config.get("stdoutput", sys.stdout))
    return None

# vim: tabstop=4 shiftwidth=4
