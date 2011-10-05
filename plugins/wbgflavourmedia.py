"""
Summary
=======

This intercepts paths like ``/flavour/flav/xyz.css`` and serves up the file 
``xyz.css`` for the flavour ``flav`` located in the flavour dir.  This allows 
flavour packs to be completely self-contained.

wbgflavourmedia only serves up files of the following types:

 * .css - text/css
 * .gif, .jpg, .jpeg, .png - image/...

FIXME - add more types

This plugin is maintained at::

   http://www.bluesock.org/~willg/pyblosxom/

Check that URL for new versions, better documentation, and submitting bug 
reports and feature requests.


Configuration
=============

There is no configuration that needs to be done.  This plugin pretty much 
works right out of the box.

FIXME - add ability to specify additional extensions and mimetypes.

----

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

Copyright 2007 Will Guaraldi

SUBVERSION VERSION: $Id$

Revisions:
2007-11-29 - created it
"""

__author__ = "Will Guaraldi - willg at bluesock dot org"
__version__ = "$Date: 2006-10-01 10:53:20 -0500 (Sun, 01 Oct 2006) $"
__url__ = "http://www.bluesock.org/~willg/pyblosxom/"
__description__ = "Grabs media files from flavour directories allowing flavour packs to be self-contained"

import mimetypes
import os
import os.path
import stat
import urllib
from Pyblosxom import tools

def verify_installation(req):
    cfg = req.config
    if not cfg.get("flavourdir", None):
        print "You must set 'flavourdir' in your config.py file for wbgflavourmedia to work."
        return 0

    return 1

def is_piece_safe(piece):
    if os.sep in piece or piece == "." or piece == "..":
        return False
    return True

def cb_handle(args):
    req = args["request"]
    pyhttp = req.http
    pathinfo = pyhttp.get("PATH_INFO", "")

    logger = tools.getLogger()

    # breaks the pathinfo into nice pieces
    pieces = [ urllib.unquote(p) for p in pathinfo.split("/") if p ]

    logger.info("%s" % repr(pieces))

    if len(pieces) == 0 or pieces[0] != "flavour":
        return

    cfg = req.config
    response = req.getResponse()

    flavourdir = cfg.get("flavourdir", None)
    if not flavourdir:
        return

    logger.info("checking safety of %s and %s" % (pieces[1], pieces[2]))

    if not is_piece_safe(pieces[1]) or not is_piece_safe(pieces[2]):
        return

    # FIXME - test fn for extensions

    fn = os.path.join(flavourdir, "%s.flav" % pieces[1], pieces[2])
    logger.info("looking at %s" % fn)
    if not os.path.isfile(fn):
        return

    logger.info("looking good....")

    # this is based on the filekicker.py plugin
    contenttype, enc = mimetypes.guess_type(fn)
    logger.info("content-type: %s" % repr(contenttype))
    logger.info("encoding: %s" % repr(enc))

    if contenttype:
        response.addHeader('Content-Type', contenttype)

    if enc:
        response.addHeader('Content-Encoding', enc)

    length = os.stat(fn)[stat.ST_SIZE]
    response.addHeader('Content-Length', str(length))

    logger.info("length: %s" % repr(length))

    f = open(fn, "rb", 4096)
    while True:
        block = f.read(4096)
        if not block:
            break
        response.write(block)

    f.close()
    return 1
