"""
This plugin keeps a cache of things so that we don't re-render
things we've rendered before and have cached.

It requires a "cachedir" config property which should be an absolute
directory name for the cache that we read from and write to.


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

Revisions:
1.0 - (24 April 2004) initial writing
"""
__author__ = "Will Guaraldi - willg at bluesock dot org"
__version__ = "1.0 (24 April 2004)"
__url__ = "http://www.bluesock.org/~willg/pyblosxom/"
__description__ = "Caches pages for a day."

import string, StringIO, os, os.path, time, sys
from pyblosxom.renderers import base

goodstuff = string.ascii_letters + string.digits + "."

class RendererDecorator(base.RendererBase):
    def __init__(self, renderer):
        self._renderer = renderer
        self._buffer = StringIO.StringIO()

    def write(self, data):
        self._renderer.write(data)

    def addHeader(self, *args):
        self._renderer.addHeader(args)

    def setContent(self, content):
        self._renderer.setContent(content)

    def needsContentType(self, flag):
        self._renderer.needsContentType(flag)

    def showHeaders(self):
        self._renderer.showHeaders()

    def render(self, header=1):
        self._renderer.render(header)

def fix_filename(filename):
    def fix(m):
        if m in goodstuff:
            return m
        return "_"

    return "".join([fix(m) for m in filename])
    

def cb_handle(args):
    request = args["request"]
    pyhttp = request.getHttp()
    config = request.getConfiguration()

    cachedir = config.get("cachedir", "./cache/")
    if cachedir[-1] != os.sep: cachedir = cachedir + os.sep

    filename = cachedir + fix_filename(pyhttp["PATH_INFO"])

    filename = os.path.normpath(filename)

    expired = time.time() - (60 * 60 * 24)

    # if the file is cached, we return that--and by file, we're actually
    # talking about the full http response
    if os.path.isfile(filename + ".cached") and os.path.getmtime() > expired:
        f = open(filename + ".cached", "r")
        lines = f.readlines()
        f.close()
        print "".join(lines)
        return 1

    buffer = StringIO.StringIO()

    data = request.getData()
    data["cache_this_file_as"] = filename + ".cached"
    data["old_sys_stdout"] = sys.stdout

    sys.stdout = buffer

def cb_end(args):
    req = args["request"]
    config = req.getConfiguration()
    data = req.getData()

    cachedir = config.get("cachedir", "./cache/")
    if cachedir[-1] != os.sep: cachedir = cachedir + os.sep

    filename = data.get("cache_this_file_as", "")
    if filename:
        if not os.path.isdir(cachedir):
            os.makedirs(cachedir)
        buffer = sys.stdout
        sys.stdout = data["old_sys_stdout"]

        f = open(filename, "w")
        f.write(buffer.getvalue())
        f.close()

        print buffer.getvalue()
