"""
This plugin is maintained at:

   http://www.bluesock.org/~willg/pyblosxom/

Check that URL for new versions, better documentation, and submitting
bug reports and feature requests.

----

This plugin allows you to include static files outside of the entry
system.  Static files should probably be text files, though this plugin
could be improved to handle php, cgi and all that other non-static file
stuff.

It looks for urls like::

   /static/blah

and pulls up the file "blah" which is located in the path specified in
the config file as "staticdir".  If no staticdir is specified, then we
use the datadir.

If the file is not there, it kicks up a 404.

It formats the page using the static flavour template.  So you need
to add a "static.html" file to your datadir (assuming you're using
the "html" flavour).  This is just like your story flavour template.

pystaticfile handles evaluating python code blocks.  Enclose python
code in <% and %> .  The assumption is that only you can edit your 
static files, so there are no restrictions (security or otherwise).

For example:

<%
print "testing"
%>

<%
x = { "apple": 5, "banana": 6, "pear": 4 }
for mem in x.keys():
   print "<li>%s - %s</li>" % (mem, x[mem])
%>

The request object is available in python code blocks.  Reference it
by "request".  ex:

<%
config = request.getConfiguration()
print "your datadir is: %s" % config["datadir"]
%>


TODO:
 - need better filename sanitization
 - the title should get adjusted as well--it should be the title of the
   file entry (in my opinion)


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

Copyright 2002, 2003, 2004 Will Guaraldi

SUBVERSION VERSION: $Id$

Revisions:
2005-11-11 - Pulled into another new version control system
2.0 (26 October, 2005) - pulled into new version control system
1.9 (22 December, 2004) - Fixed a problem with the code blocks.
1.8 (07 December, 2004) - Minor fix so that comments work again.
1.7 (05 May, 2004) - Bunch of minor fixes.
1.6 (28 April, 2004) - fixed it so it works with comments.
1.5 (05 April, 2004) - added the request to the locals for eval_python_block.
                       fixed stringio for eval_python_block.
1.4 (27 January, 2004) - added handling for python codeblocks
1.3 (22 January, 2004) - adjusted it to use its own flavour
1.2 (21 July, 2003) - quelling of date headers
1.1 (20 July, 2003) - minor adjustments
1.0 (6 July, 2003) - first written
"""
import os, StringIO, sys
from Pyblosxom.entries.fileentry import FileEntry
from Pyblosxom import tools

__author__ = "Will Guaraldi - willg at bluesock dot org"
__version__ = "$Date$"
__url__ = "http://www.bluesock.org/~willg/pyblosxom/"
__description__ = "Allows you to do static files as entries."

TRIGGER = "static"
INIT_KEY = "static_static_file_initiated"

def verify_installation(req):
    config = req.getConfiguration()
    import os.path

    retval = 1

    if not config.has_key("staticdir") or not os.path.isdir(config["staticdir"]):
        print "'staticdir' property is not set in the config file."
        retval = 0

    return retval

 
def cb_date_head(args):
    req = args["request"]
    data = req.getData()
    if data.has_key(INIT_KEY):
        args["template"] = ""
    return args

def cb_date_foot(args):
    return cb_date_head(args)

def eval_python_blocks(req, body):
    localsdict = {"request": req}
    globalsdict = {}

    old_stdout = sys.stdout
    old_stderr = sys.stderr

    try:
        start = 0
        while body.find("<%", start) != -1:
            start = body.find("<%")
            end = body.find("%>", start)    

            if start != -1 and end != -1:
                codeblock = body[start+2:end].lstrip()

                sys.stdout = StringIO.StringIO()
                sys.stderr = StringIO.StringIO()

                try:
                    exec codeblock in localsdict, globalsdict
                except Exception, e:
                    print "ERROR in processing: %s" % e

                output = sys.stdout.getvalue() + sys.stderr.getvalue()
                body = body[:start] + output + body[end+2:]

    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr

    return body
 
def cb_filelist(args):
    req = args["request"]

    pyhttp = req.getHttp()
    data = req.getData()
    config = req.getConfiguration()

    if not pyhttp["PATH_INFO"].startswith("/" + TRIGGER):
        return

    data[INIT_KEY] = 1
    datadir = config["datadir"]
    data['root_datadir'] = config['datadir']
    staticdir = config.get("staticdir", config['datadir'])

    staticdir = staticdir.replace("/", os.sep)
    if not staticdir[-1] == os.sep:
        staticdir = staticdir + os.sep

    page_name = pyhttp["PATH_INFO"][len("/" + TRIGGER)+1:]

    # FIXME - need to do a better job of sanitizing
    page_name = page_name.replace(os.sep, "/")
    if page_name[-1] == os.sep:
        page_name = page_name[:-1]
    if page_name.find("/") > 0:
        page_name = page_name[page_name.rfind("/"):]

    # if the page has a flavour, we use that.  otherwise
    # we default to the static flavour
    page_name, flavour = os.path.splitext(page_name)
    if flavour:
        data["flavour"] = flavour[1:]

    # we build our own config dict for the fileentry to kind of
    # fake it into loading this file correctly rather than
    # one of the entries.
    newdatadir = staticdir
    config["datadir"] = newdatadir

    ext = tools.what_ext(data["extensions"].keys(), staticdir + page_name)

    if not ext:
        return []

    data['root_datadir'] = page_name + '.' + ext
    data['bl_type'] = 'file'
    filename = staticdir + page_name + "." + ext

    fe = FileEntry(req, filename, staticdir)
    # now we evaluate python code blocks
    body = fe.getData()
    body = eval_python_blocks(req, body)
    body = "<!-- STATIC PAGE START -->\n\n" + body + "<!-- STATIC PAGE END -->\n"
    fe.setData(body)

    fe["absolute_path"] = TRIGGER
    fe["fn"] = page_name
    fe["file_path"] = TRIGGER + "/" + page_name
    fe["template_name"] = "static"

    data['blog_title_with_path'] = config.get("blog_title", "") + " : " + fe.get("title_escaped", "")

    # set the datadir back
    config["datadir"] = datadir

    return [fe]
