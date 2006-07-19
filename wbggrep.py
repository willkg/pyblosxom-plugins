"""
This plugin is a basic search plugin that uses grep.  It's super
ultra basic but it provides for my search needs pretty well.

To install:

  1. toss the plugin in your plugin dir
  2. add to your load_plugins list in your config.py file
  3. add a form to your foot.html or head.html like this:

      <form method="post" action="$base_url/search">
      <input name="query" value="" size=15><br>
      <input type="submit" name="search" value="Search">
      </form>

  4. you can specify the flavour the entry links point to with
     the config.py property "grep_flavour" (defaults to html)
  5. you can specify the story template to use for the search
     results entry with "grep_template" (defaults to "story")
  6. depending on where grep is on your system and what flags
     it supports, you may have to edit the grep command line


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

SUBVERSION VERSION: $Id$

Revisions:
2005-11-11 - Pulled into new VCS.
1.5 - (26 October, 2005) pulled into new VCS
1.1 - (09 December, 2004) fixed date_head issue.
1.0 - (27 May, 2004) Created.
"""
import os, sys, commands, time, string
from Pyblosxom.entries import base

__author__ = "Will Guaraldi - willg at bluesock dot org"
__version__ = "$Date$"
__url__ = "http://www.bluesock.org/~willg/pyblosxom/"
__description__ = "Ultra-basic search plugin that uses grep."

TRIGGER = "/search"
INIT_KEY = "search_initiated"
GREP_CMD_LINE = "/bin/egrep -ir -m 1 \"%s\" %s"

def prepare_text(text):
    text = text.replace(">", "&gt;").replace("<", "&lt;")
    return text

def search(baseurl, datadir, extensions, flavour, s):
    output = []
    s2 = s
    for mem in string.punctuation:
        if mem == ".": continue
        s2 = s2.replace(mem, "")

    s2 = s2.split(" ")
    s2 = [m for m in s2 if m]
    if len(s2) > 1:
        s2 = "(" + "|".join(s2) + ")"
    else:
        s2 = "".join(s2)

    output.append("<p><b>searching for '%s':</b></p>" % s2)

    grep = commands.getstatusoutput(GREP_CMD_LINE % (s2, datadir))

    grep = grep[1]
    if not grep or grep.find("No such file or directory") != -1:
        output.append("<p>There are no search results.</p>")
        return "".join(output)

    grep = grep.splitlines()
    grep.sort()
    for mem in grep:
        line = mem
        f = line[:line.find(":")]

        f = f.replace(datadir, "")
        p = f.rfind(".")
    
        if not f[p+1:] in extensions:
            continue
    
        f = f[:p] + "." + flavour
        text = prepare_text(line[line.find(":")+1:])
    
        output.append("<p><a href=\"%s/%s\">%s</a><br>%s</p>\n" % (baseurl, f, f, text))

    return "".join(output)

def cb_date_head(args):
    req = args["request"]
    data = req.getData()
    if data.has_key(INIT_KEY):
        args["template"] = ""
    return args

def cb_filelist(args):
    request = args["request"]
    config = request.getConfiguration()
    pyhttp = request.getHttp()
    data = request.getData()

    form = pyhttp["form"]
    datadir = config["datadir"]
    baseurl = config["base_url"]

    if not datadir.endswith(os.sep):
        datadir = datadir + os.sep

    if not pyhttp["PATH_INFO"].startswith(TRIGGER) or not form.has_key("query"):
        return

    data[INIT_KEY] = 1
    query = form["query"].value
    extensions = data["extensions"].keys()
    flavour = config.get("grep_flavour", "html")

    output = search(baseurl, datadir, extensions, flavour, query)

    entry = base.EntryBase(request)
    entry["title"] = "Search results...."
    entry["filename"] = "searchresults"
    entry["nocomments"] = "1"
    if config.has_key("grep_template"):
        entry["template_name"] = config["grep_template"]

    entry.setTime(time.localtime())
    entry.setData(output)

    return [entry]
