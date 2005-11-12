"""
Provides me with a $urlencodedtitle which is better for the Google link.
It's a urlencoded title.

There's no configuration needed--you can drop this plugin into your
plugin dir and it'll work just fine.


NOTE: This plugin is not required if you're using PyBlosxom 1.3 and
later.


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

Copyright 2002-2005 Will Guaraldi

SUBVERSION VERSION: $Id$

Revisions:
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
