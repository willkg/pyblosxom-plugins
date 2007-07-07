"""
=======
wbgwiki
=======

Summary
=======

This plugin allows you read-only wiki-like functionality.  It's read-only
in the sense that it can only be edited on the file-system--not from the
internet.  It's wiki-like in the sense that it recognizes wiki-like
links and expands them with HTML links.

Files can be formatted in whatever formatting markups the rest of your
blog accepts.

I apologize for usurping the word "wiki".  It sort of describes what
this plugin does, but also implies things which aren't necessarily
true.

This plugin is maintained at:

   http://www.bluesock.org/~willg/pyblosxom/

Check that URL for new versions, better documentation, and submitting
bug reports and feature requests.



wikidir Configuration
=====================

Wiki pages are located in the directory specified by ``wikidir`` in your
``config.py`` file.  Example::

   py["wikidir"] = "/home/willg/blog/wiki"


URLs
====

Requests for urls like::

   /wiki/<topic>

will pull up the file for "<topic>.<ext>" where "topic" is the first part
of the filename and "ext" is the extension.  The extension can be any
valid extension for entries on your blog.  For example, if you have the
Textile entryparser installed, then ".txtl" would be a valid file ending.
".txt" will always work.

If the file is not there, it kicks up a 404.


Markup Syntax
=============

Theoretically this won't interfere with the markup of your favorite
entryparser....

Wiki-like link syntax is as follows:

* [[topic]]
* [[topic | shorthand]]

The entire wiki-like link must be on the same line.  The following won't
work::

   <p>
     I do a lot of software development.  You can view my work [[writings |
     here]].
   </p>


Templates
=========

wbgwiki formats the page using the "wiki" template.  If you were using
an "html" flavour, then you'd need to create a "wiki.html" template.
The location of this template depends on how you have flavours set up
on your blog.  If you have your flavours in a specified flavourdir
then you can simply create the "wiki.<flavourname>" template in the
flavour in the flavourdir.

I tend to copy my story flavour templates over and remove the 
date/time-related bits.

If you don't have a "wiki" template, then it'll default to using the
"story" template.



Python code blocks
==================

wbgwiki also handles evaluating python code blocks.  Enclose python
code in <% and %> .  The assumption is that only you can edit your 
wiki files, so there are no restrictions (security or otherwise).

For example::

   <%
   print "testing"
   %>


and::

   <%
   x = { "apple": 5, "banana": 6, "pear": 4 }
   for mem in x.keys():
      print "<li>%s - %s</li>" % (mem, x[mem])
   %>


The request object is available in python code blocks.  Reference it
by "request".  Example::

   <%
   config = request.getConfiguration()
   print "your datadir is: %s" % config["datadir"]
   %>

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

Copyright 2002-2007 Will Guaraldi

SUBVERSION VERSION: $Id$

Revisions:
2007-07-03 - changed name to wbgwiki, added nested directory support,
             added wiki-like linking
2006-10-01 - adjustments to the documentation at the top.
2005-11-13 - now adjusts the $blog_title_with_path variable to include
             the static file title
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
import os, StringIO, sys, re
from Pyblosxom.entries.fileentry import FileEntry
from Pyblosxom import tools

__author__ = "Will Guaraldi - willg at bluesock dot org"
__version__ = "$Date: 2006-10-01 10:53:20 -0500 (Sun, 01 Oct 2006) $"
__url__ = "http://www.bluesock.org/~willg/pyblosxom/"
__description__ = "Wiki-like functionality for your site"

TRIGGER = "wiki"
INIT_KEY = "wiki_file_initiated"

def verify_installation(req):
    config = req.getConfiguration()
    import os.path

    if not config.has_key("wikidir"):
        print "'wikidir' property is not set in the config file."
        return 0

    if not os.path.isdir(config["wikidir"]):
        print "'wikidir' points to a non-existing directory: '%s'" % \
              config["wikidir"]
        return 0

    return 1
 
def cb_date_head(args):
    # this is a hack to wipe out the date_head template when we're
    # showing wiki pages.
    req = args["request"]
    data = req.getData()
    if data.has_key(INIT_KEY):
        args["template"] = ""
    return args

# cb_date_foot should do the exact same thing as cb_date_head
cb_date_foot = cb_date_head

def eval_python_blocks(req, body):
    """
    Evaluate Python blocks in the page.  

    We add "request" -> Request to the locals dictionary so that "request" 
    can be referred to.
    """
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


WIKILINK = re.compile(r"\[\[" + r"([^\]]+)" + r"\]\]")

def connect_links(base_url, extensions, wikidir, body):
    """
    Looks for wiki links in [[topic]] and [[topic | desc]]
    format and expands them.
    """
    if base_url.endswith("/"):
        base_url = base_url[:-1]

    i = 0
    body2 = []

    for match in WIKILINK.finditer(body):
        body2.append(body[i:match.span(0)[0]])
        
        text = match.group(1)

        if "|" in text:
            topic, desc = text.split("|")
            topic = topic.strip()
        else:
            topic, desc = (text, text)

        fn = os.path.join(wikidir, topic)

        ext = tools.what_ext(extensions, fn)
        if not ext:
            body2.append(match.group(0))
            i = match.span(0)[1]
            continue

        body2.append("<a href=\"%s/%s/%s\">%s</a>" % \
                     (base_url, TRIGGER, topic, desc))
        i = match.span(0)[1]

    body2.append(body[i:])
    return "".join(body2)
    
def cb_filelist(args):
    """
    This handles kicking off wbgwiki functionality if we see a
    url that we handle.
    """
    req = args["request"]

    pyhttp = req.getHttp()
    config = req.getConfiguration()
    pathinfo = pyhttp["PATH_INFO"]

    if not pathinfo.startswith("/" + TRIGGER):
        return

    logger = tools.getLogger()

    data = req.getData()
    data[INIT_KEY] = 1
    datadir = config["datadir"]
    data['root_datadir'] = config['datadir']
    wikidir = config.get("wikidir", config['datadir'])

    # convert the / to os.sep so that we can use os.path stuff.
    wikidir = wikidir.replace("/", os.sep)
    if not wikidir.endswith(os.sep):
        wikidir = wikidir + os.sep

    page_name = pathinfo[len("/" + TRIGGER)+1:]

    if not page_name:
        return

    page_name = page_name.replace("/", os.sep)

    if not page_name:
        return

    if page_name.endswith(os.sep):
        page_name = page_name[:-1]

    # if the page has a flavour, we use that.  otherwise
    # we default to the wiki flavour
    page_name, flavour = os.path.splitext(page_name)
    if flavour:
        data["flavour"] = flavour[1:]

    # wikifile should hold the absolute path on the file system to
    # the wiki file we're looking at.  if it's in a parent directory
    # of wikidir, then we abort.  
    wikifile = os.path.normpath(os.path.join(wikidir, page_name))
    if not wikifile.startswith(wikidir):
        logger.info("wiki file requested '%s' is not in wikidir." % wikifile)
        return []

    # we build our own config dict for the fileentry to kind of
    # fake it into loading this file correctly rather than
    # one of the entries.
    newdatadir = wikidir

    ext = tools.what_ext(data["extensions"].keys(), wikifile)

    if not ext:
        logger.info("wiki file '%s' does not exist." % wikifile)
        return []

    data['root_datadir'] = page_name + '.' + ext
    data['bl_type'] = 'file'
    wikifile = wikifile + "." + ext

    if not os.path.isfile(wikifile):
        return []

    fe = FileEntry(req, wikifile, wikidir)

    # now we evaluate python code blocks
    body = fe.getData()
    body = eval_python_blocks(req, body)
    body = "<!-- STATIC PAGE START -->\n\n%s\n<!-- STATIC PAGE END -->\n" % body

    # now we evaluate for wikilinks
    body = connect_links(config["base_url"],
                         data["extensions"].keys(),
                         wikidir,
                         body)

    fe.setData(body)

    fe["absolute_path"] = TRIGGER
    fe["fn"] = page_name
    fe["file_path"] = TRIGGER + "/" + page_name
    fe["template_name"] = "wiki"

    data['blog_title_with_path'] = "%s : %s" % \
                   (config.get("blog_title", ""), fe.get("title_escaped", ""))

    # set the datadir back
    config["datadir"] = datadir

    return [fe]
