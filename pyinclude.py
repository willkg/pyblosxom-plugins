"""
This plugin allows you to include the contents of a file as a variable.
This has some utility when reading in the output of a cronjob that pulls
data down or some other such thing.

It happs in cb_head and cb_foot--so you can use this variable in either
place.

To insert a file in your head or foot template, do the following::

    $util::include("filename")

where "filename" is replaced by the file name.  In most cases you will
want to provide an absolute path, however pyinclude will handle
relative paths and base them off of the root_datadir.

Examples::

    $util::include("/home/willg/.plan")
    $util::include("desc.dsc")

In the first example, we will pull in the .plan file all the time.  In
the second example, we will pull in the desc.dsc file if there is one
in the root_datadir.  The root_datadir is the category the user is looking
at.  If there isn't such a file in the root_datadir, then this will
return an empty string.


This plugin requires no configuration setup--you can drop it in your
plugin dir and it'll work out of the box.

It also handles evaluating python code blocks.  Enclose them in <% and %>
and use regular python.  The assumption is that only you can edit your 
static files, so there are no restrictions.

For example:

<%
print "testing"
%>

<%
x = { "apple": 5, "banana": 6, "pear": 4 }
for mem in x.keys():
   print "<li>%s - %s</li>" % (mem, x[mem])
%>

To use things in the Request object, the variable name is "request":

<%
config = request.getConfiguration()
print config["datadir"]
%>


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

Copyright 2002, 2003 Will Guaraldi

SUBVERSION VERSION: $Id$

Revisions:
2005-11-11 - Pulled into another new version control system.
1.3 - (26 October, 2005) pulled into new version control system
1.2 - (14 May, 2004) added handling for relative filenames
1.1 - (23 April, 2004) added python script evaluation
1.0 - initial writing
"""
__author__ = "Will Guaraldi - willg at bluesock dot org"
__version__ = "$Date$"
__url__ = "http://www.bluesock.org/~willg/pyblosxom/"
__description__ = "Allows you to include text files."

import sys, StringIO, os, os.path

def verify_installation(request):
    return 1

def include(req, filename):
    """
    This takes in one argument--a filename.  It opens the file, reads
    in the contents, and returns them as the value of this variable.

    (It actually takes in two, but one of them is provided by
    PyBlosxom.)
    """
    if not filename.startswith(os.sep):
        data = req.getData()
        basedir = data["root_datadir"]
        if data.has_key("bl_type") and data["bl_type"] == "file":
            basedir = os.path.dirname(basedir)

        filename = os.path.normpath(basedir + os.sep + filename)

    try:
        f = open(filename, "r")
        lines = "".join(f.readlines())
        f.close()
        return eval_python_blocks(req, lines)
    except:
        return ""

def eval_python_blocks(req, body):
    outputbuffer = []

    localsdict = {"request": req}
    globalsdict = {}

    old_stdout = sys.stdout
    old_stderr = sys.stderr

    sys_stdout = StringIO.StringIO()
    sys_stderr = StringIO.StringIO()
 
    try:
        sys.stdout = sys_stdout
        sys.stderr = sys_stderr

        start = 0
        while body.find("<%", start) != -1:
            start = body.find("<%")
            end = body.find("%>", start)    

            if start != -1 and end != -1:
                codeblock = body[start+2:end].lstrip()

                try:
                    exec codeblock in localsdict, globalsdict
                except Exception, e:
                    print "ERROR in processing: %s" % e

                output = sys_stdout.getvalue() + sys_stderr.getvalue()
                body = body[:start] + output + body[end+2:]

    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr

    return body
 
def cb_head(args):
    """
    This method gets called in the cb_story callback.  Refer to
    the documentation for that.
    """
    entry = args["entry"]
    entry["util::include"] = include

def cb_foot(args):
    return cb_head(args)
