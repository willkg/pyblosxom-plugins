"""
This plugin is triggered by "debug=yes" in the query string.  It'll
change the renderer being used to the Debug renderer.

It makes programming some things _much_ easier.

There's no configuration required for this plugin--you can drop it in
your plugin dir and it'll work just fine.


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

CVSVERSION: $Id: wbgdebug.py,v 1.5 2005/10/26 18:42:13 willg Exp $

Revisions:
1.5 - (26 October, 2005) pulled into new VCS
1.0 - (26 January 2004) initial writing
"""
__author__ = "Will Guaraldi - willg at bluesock dot org"
__version__ = "$Revision: 1.5 $ $Date: 2005/10/26 18:42:13 $"
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
