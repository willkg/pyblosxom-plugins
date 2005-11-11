"""
This plugin handles displaying a file registry, submitting new entries
to a registry, and comments for existing entries.  A registry 
is a series of .txt files which provide information about a given series 
of things which are registered.  They are organized into categories by 
the directory structure.  

The registry plugin uses the entryparser for .txt files which parses
entries that look like this:

%<-------------------------
title of plugin
#name value
#name value
#name value
#name value
description of plugin
%<-------------------------

The registry plugin can use entries parsed by other entry parsers so long
as they support meta information.  It supports preformatters and 
postformatters and all that stuff because it uses the regular entry parsers.

The registry requires several templates in your data directory:

  - registry-summary - used for an entry summary line
  - registry-story   - used for a complete single entry
  - registry-index   - used to hold a bunch of summaries

The registry plugin requires a registry-summary template in your data
directory.  This is used to provide a summary of a given registry
entry.

The registry will support the following urls:

    /registry                 -- listing by date (mtime)
    /registry?sortby=category -- listing by category
    /registry?sortby=input    -- listing by any input (author, name, ...)
    /registry/category        -- prints contents in a category
    /registry/path/to/item    -- prints full contents of specific item
    /registry_submit          -- prints the form to submit a new entry
    /registry_queue           -- shows all the pending submissions

The registry plugin requires the following variables to be set in
your config.py file:

    registry_dir    - the directory holding your registry entries
    registry_edit   - whether (1) or not (0) you allow people to submit
                      new entries
    registry_default_flavour - the default flavour to use for the registry
                      if none are requested--defaults to "html"


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

Copyright 2002-2004 Will Guaraldi

CVSVERSION: $Id: registry.py,v 2.2 2005/10/27 02:08:49 willg Exp $

Revisions:
2.2 - (26 October, 2005) pulled into new VCS
2.1 - (13 December, 2004) fixed date_head template issue
2.0 - (05 May, 2004) total overhaul--literally
1.4 - (17 March, 2004) bug fixes
1.3 - (17 Feb, 2004) added the ability to see the queue
1.2 - (31 Dec, 2003) complete overhaul for registry submission, updates,
      code refactoring, adjustments for making it easier to adjust, and
      a bunch of other stuff.
1.1 - (3 May, 2003) Minor changes.
1.0 - Created.
"""
import time, re, os.path, os, string
from Pyblosxom.entries import fileentry, base
from Pyblosxom import tools

__author__ = "Will Guaraldi - willg at bluesock dot org"
__version__ = "$Revision: 2.2 $ $Date: 2005/10/27 02:08:49 $"
__url__ = "http://www.bluesock.org/~willg/pyblosxom/"
__description__ = "Handles editing and display of a tree of data files like entries or whatever."

# this is the url that will trigger this plugin into action
TRIGGER = "/registry"
SUBMITTRIGGER = "/registry_submit"
QUEUETRIGGER = "/registry_queue"
INIT_KEY = "registry_file_initiated"

REGISTRY_SUMMARY = """<li><a href="$base_url/$trigger/$file_path">$name</a>: $briefdesc</li>"""

REGISTRY_STORY = """
<div class="registry_item">
<div class="registry_item_title">$title</div>
<table>
<tr><td class="blosxomRegistryHeader">name:</td><td>$name</td></tr>
<tr><td class="blosxomRegistryHeader">version:</td><td>$version</td></tr>
<tr><td class="blosxomRegistryHeader">author:</td><td>$author</td></tr>
<tr><td class="blosxomRegistryHeader">description:</td><td>$description</td></tr>
<tr><td class="blosxomRegistryHeader">category:</td><td>$category</td></tr>
<tr><td class="blosxomRegistryHeader">url:</td><td>$url</td></tr>
<tr><td class="blosxomRegistryHeader">download:</td><td>$download</td></tr>
<tr><td class="blosxomRegistryHeader">last edited:</td><td>$date</td></tr>
</table>
</div>
"""

REGISTRY_FORM = """
<div class="registry_item">
<form action="$base_url/registry_submit" method="POST">
<table>
<tr>
   <td valign="top"><b>name:</b></td>
   <td valign="top"><input type="text" name="name" value="$name"></td>
</tr>
<tr>
   <td valign="top"><b>version:</b></td>
   <td valign="top"><input type="text" name="version" value="$version"></td>
</tr>
<tr>
   <td valign="top"><b>author:</b></td>
   <td valign="top"><input type="text" name="author" value="$author"></td>
</tr>
<tr>
   <td valign="top"><b>category:</b></td>
   <td valign="top"><select name="category">
<option name="archives">archives</option>
<option name="authentication">authentication</option>
<option name="author">author</option>
<option name="browser">browser</option>
<option name="calendar">calendar</option>
<option name="category">category</option>

<option name="date">date</option>
<option name="debug">debug</option>
<option name="display">display</option>
<option name="display/graphics">display/graphics</option>
<option name="edit">edit</option>
<option name="files">files</option>
<option name="filtering">filtering</option>
<option name="general">general</option>
<option name="headers">headers</option>

<option name="hosting">hosting</option>
<option name="images">images</option>
<option name="include">include</option>
<option name="indexing">indexing</option>
<option name="input">input</option>
<option name="integration">integration</option>
<option name="interpolate">interpolate</option>
<option name="link">link</option>
<option name="link/amazon">link/amazon</option>

<option name="link/google">link/google</option>
<option name="logs">logs</option>
<option name="macros">macros</option>
<option name="meta">meta</option>
<option name="output">output</option>
<option name="programming">programming</option>
<option name="search">search</option>
<option name="silly">silly</option>
<option name="sort">sort</option>

<option name="syndication">syndication</option>
<option name="text">text</option>
<option name="xmlrpc">xmlrpc</option>
</select></td>
</tr>

<tr>
   <td valign="top"><b>maturity:</b></td>
   <td valign="top"><select name="maturity">
<option name="beta">beta</option>
<option name="stable">stable</option>
<option name="mature">mature</option>
</select></td>
</tr>

<tr>
   <td valign="top"><b>description:</b></td>
   <td valign="top"><textarea cols=80 rows=8 name="description">$description</textarea></td>
</tr>

<tr>
   <td valign="top"><b>url:</b></td>
   <td valign="top"><input type="text" name="url"></td>
</tr>
<tr>
   <td valign="top"><b>download:</b></td>
   <td valign="top"><input type="text" name="download"></td>
</tr>
<tr>
   <td>&nbsp;</td>
   <td><input type="submit" value="Submit entry"><input type="reset"></td>
</tr>
</table>
</form>
</div>
"""

CONTRIB_DESC = """
This used to come in the ./contrib directory of the PyBlosxom tar.gz
download.  As of PyBlosxom 1.1, we no longer distribute contributed
plugins with PyBlosxom.  There are various good reasons for this, though
we do apologize for the inconvenience it causes.

Currently (as of February 23, 2005) you can get the contrib directory
contents (and all scripts and plugins there) at in .tar.gz files at:

https://sourceforge.net/project/showfiles.php?group_id=67445&package_id=145140
"""

def verify_installation(request):
    # FIXME - this plugin is so complicated no man can possibly
    # configure it correctly.  ;)
    # but seriously, i should write this up when i'm done changing
    # the thing.
    return 0

def readonly(config):
    """
    Checks the config map to see if we're in readonly mode or not.
    This defaults to "we're in readonly mode".

    @return: whether (1) or not (0) we're in readonly mode
    """
    if not config.has_key("registry_edit") or config["registry_edit"] != 1:
        return 1
    return 0

def fix(s):
    """
    Fixes up a string so that it at least says "None" if it has no value.

    @param s: the string value to fix up
    @type  s: string

    @returns: the fixed up string converting CR to <br>, removing LFs and
              returning "None" if s is None or empty
    """
    if not s:
        return "None"
    return s.replace("\n", "<br>").replace("\r", "")


def render(request, entry, template):
    """
    Takes a given request and summarizes it given the registry-template
    template for this flavour.
    """
    config = request.getConfiguration()
    data = request.getData()
    flavour = data.get("flavour", "html")
    renderer = data["renderer"]

    entry.update(config)

    output = []
    renderer.outputTemplate(output, entry, "registry-%s" % template)
    return u"".join(output)

URLRE = None

def urlme(req, arg1):
    """
    Takes in the request (I have no idea why) and the argument
    and converts everything in the argument that resembles a url
    into an a href.  Then it returns the converted thing.
    """
    global URLRE
    if not arg1 or arg1.lower() == "none":
        return arg1

    if not URLRE:
        URLRE = re.compile("(http[s]?://[^\\s\\>\\<]+)", re.I)

    sin = arg1
    # FIXME - this could be sped up by using a buffer for "done"
    # pieces.
    mo = URLRE.search(sin)
    while mo:
        s = mo.start()
        e = mo.end()
        if sin[e-1] == "." or sin[e-1] == ",":
            e = e - 1
        newtext = '<a href=\"%s\">%s</a>' % (sin[s:e], sin[s:e])
        sin = '%s%s%s' % (sin[:s], newtext, sin[e:])
        mo = URLRE.search(sin, s + len(newtext))

    return sin

def cb_date_head(args):
    request = args["request"]
    data = request.getData()

    if data.has_key(INIT_KEY):
        args["template"] = ""
    return args

def cb_story(args):
    entry = args["entry"]
    if not entry.has_key("registry_render"):
        entry["registry::url"] = urlme
        return args

    request = args["request"]
    body = entry["registry_render"]
    body = "".join([render(request, m[0], m[1]) for m in body])
    entry.setData(body)
    entry["registry::url"] = urlme

    return args

def generate_entry(request, output, title="Registry", filename="", mtime=None):
    """
    Takes a bunch of text and generates an entry out of it.  It creates
    a timestamp so that conditionalhttp can handle it without getting
    all fussy.
    """
    global CONTRIB_DESC
    entry = base.EntryBase(request)
    registrydir = request.getConfiguration()["registry_dir"]

    entry['title'] = title
    entry['fn'] = filename

    if filename:
        b = TRIGGER[1:]
        f = filename[len(registrydir):-4]
        entry['fn'] = os.path.split(f)[1]
        entry['file_path'] = b + f
        entry['absolute_path'] = b + os.path.split(f)[0]
        entry._id = filename
    else:
        entry["nocomments"] = 1

    if mtime:
        entry.setTime(time.localtime(mtime))
    else:
        entry.setTime(time.localtime())

    entry.setData(output)
    return entry

def fix(s):
    return s.replace("<br>", " ").replace("<", "&lt;").replace(">", "&gt;")

def get_entries(request, registrydir, entries):
    items = [fileentry.FileEntry(request, m, registrydir, registrydir) for m in entries]
    for mem in items:
        desc = mem["body"]
        if len(desc) > 100:
            desc = desc[:100] + "..."

        mem["body"] = fix(mem["body"])
        mem["short_body"] = fix(desc)
    return items
 
def get_entries_by_none(request, registrydir, entries):
    entries  = get_entries(request, registrydir, entries)
    entries.sort(lambda x,y: cmp(y._mtime, x._mtime))
    for mem in entries:
        mem["template_name"] = "registry-summary"
    return entries

def get_entries_by_date(request, registrydir, entries):
    """
    Takes in a list of filenames for all the entries in a registry and
    returns the listing ordered by the mtime of the datafile.
    """
    items = get_entries(request, registrydir, entries)
    items.sort(lambda x,y: cmp(y._mtime, x._mtime))

    entries = []
    output = []

    fn = TRIGGER + ".date"

    mtime_temp = ""
    mtime_working = ""
    mtime = 0
    for mem in items:
        mtime = mem._mtime
        mtime_temp = time.strftime("%a, %d %b %Y", time.localtime(mtime))

        if mtime_working== "":
            mtime_working = mtime_temp

        elif mtime_temp != mtime_working:
            entry = generate_entry(request, "", mtime_working, fn)
            entry["registry_render"] = output
            entry["template_name"] = "registry-index"
            entry["nocomments"] = 1
            entries.append(entry)

            output = []

            output.append( (mem, "summary") )
            mtime_working = mtime_temp
            continue

        output.append( (mem, "summary") )

    if output:
        entry = generate_entry(request, "", mtime_working, fn)
        entry["registry_render"] = output
        entry["template_name"] = "registry-index"
        entry["nocomments"] = 1
        entries.append(entry)

    return entries

def get_entries_by_item(request, registrydir, entries, sortbyitem):
    """
    Takes in a list of filenames for all the entries in a registry and
    returns the listing ordered by the item.
    """
    items = get_entries(request, registrydir, entries)

    items.sort(lambda x,y: cmp(x.get(sortbyitem, "none") + x.get("title"), y.get(sortbyitem, "none") + x.get("title")))

    entries = []
    output = []
    item = ""
    for mem in items:
        if item == "":
            item = mem.get(sortbyitem, "none")

        elif mem.get(sortbyitem, "none") != item:
            entry = generate_entry(request, "", item, item + "." + sortbyitem)
            entry["registry_render"] = output
            entry["template_name"] = "registry-index"
            entry["nocomments"] = 1
            entries.append(entry)

            output = []
            item = mem.get(sortbyitem, "none")

        output.append( (mem, "summary") )

    if output:
        entry = generate_entry(request, "", item, item + "." + sortbyitem)
        entry["registry_render"] = output
        entry["template_name"] = "registry-index"
        entry["nocomments"] = 1
        entries.append(entry)

    return entries

def handle_registry_queue(args):
    """
    Handles showing all the entries that are in the submission queue
    and all the data involved in each.
    """
    request = args["request"]
    pyhttp = request.getHttp()
    config = request.getConfiguration()
    registrydir = config["registry_dir"]

    entries = tools.Walk(request, registrydir, 0, re.compile(".*\\.[^\\.]+-$"), 0)

    if len(entries) == 0:
        return [generate_entry(request, "<p>No entries in the queue.</p>")]

    # Get our URL and configure the base_url param
    if pyhttp.has_key('SCRIPT_NAME'):
        if not config.has_key('base_url'):
            config['base_url'] = 'http://%s%s' % (pyhttp['HTTP_HOST'], pyhttp['SCRIPT_NAME'])
    else:
        config['base_url'] = config.get('base_url', '')

    config['base_url'] = config['base_url'] + TRIGGER

    output = []
    entries = get_entries(request, registrydir, entries)
    for mem in entries:
        output.append( (mem, "queue-summary") )

    entry = generate_entry(request, "", "queue", "queue")
    entry["registry_render"] = output
    entry["template_name"] = "registry-index"
    entry["nocomments"] = 1

    return [entry]

def handle_registry_submit(args):
    """
    Handles showing the new entry form, editing entries, and submitting
    new entries.
    """
    global SUBMITTRIGGER
    request = args["request"]
    pyhttp = request.getHttp()

    if not pyhttp["PATH_INFO"].startswith(SUBMITTRIGGER):
        return

    config = request.getConfiguration()
    form = pyhttp["form"]
    data = request.getData()

    ending = config.get("registryentryending", ".regdat")

    if readonly(config):
        output = "<p>This registry is read-only--you are not allowed to " + \
                 "submit new entries or edit existing ones.</p>"
        return [generate_entry(request, output, "error")]

    # if they didn't post, then they're looking for the form
    if not pyhttp["REQUEST_METHOD"] == "POST":
        d = {}
        if form.getvalue("edit"):
            d = load_values(config["registry_dir"] + form.getvalue("edit") + ending, item)
            d["title"] = "editing " + form.getvalue("edit")

        else:
            d["title"] = "submit new entry"

        if form.has_key("useform"):
            d["template_name"] = form["useform"].value
        else:
            d["template_name"] = "registry-form"
        d["nocomments"] = "true"
        return [base.generate_entry(request, d, "", None)]

    # we pick up all the data pieces here and fix them up
    name = ""
    body = ""
    category = ""
    props = {}
    for mem in form.keys():
        if mem == "name":
            name = form.getvalue(mem)
            continue
        if mem == "description":
            body = form.getvalue(mem)
            continue
        if mem == "category":
            category = form.getvalue(mem)
            continue

        props[mem] = form.getvalue(mem)

    text = name + "\n"
    for mem in props.keys():
        text += "#%s %s\n" % (mem, props[mem])
    text = text + body

    filename = name

    filename = [mem for mem in filename if mem in string.ascii_letters]
    filename = "".join(filename)

    filename = config["registry_dir"] + os.sep + category + os.sep + filename + ".txt-"

    if os.path.isfile(filename):
        # ERROR - we already have this file.  at the present time
        # we DON'T over-write it, we just tell the user we've already
        # got one.
        output = "<p>There's already a pending submission for that item.</p>"
        return [generate_entry(request, output, "error")]

    # write the file to the filesystem....
    f = open(filename, "w")
    f.write(text)
    f.close()

    # give them a pretty message
    output = """
<p>
   Submission was received.  It may take a couple of days to verify the 
   information and add the entry.  This is the data you provided us:
</p>
<pre>%s</pre>""" % text
    return [generate_entry(request, output, "success!")]

def cb_filelist(args):
    global registrydir, TRIGGER, SUBMITTRIGGER
    request = args["request"]

    pyhttp = request.getHttp()
    data = request.getData()
    config = request.getConfiguration()
    form = pyhttp["form"]

    if not pyhttp["PATH_INFO"].startswith(TRIGGER):
        return

    data[INIT_KEY] = 1

    data['root_datadir'] = config['datadir']

    # Get our URL and configure the base_url param
    if pyhttp.has_key('SCRIPT_NAME'):
        if not config.has_key('base_url'):
            config['base_url'] = 'http://%s%s' % (pyhttp['HTTP_HOST'], pyhttp['SCRIPT_NAME'])
    else:
        config['base_url'] = config.get('base_url', '')

    config['base_url'] = config['base_url'] + TRIGGER

    # if they haven't add a registrydir to their config file, 
    # we pleasantly error out
    if not config.has_key("registry_dir"):
        output = "<p>\"registry_dir\" config setting is not set.  Refer to documentation.</p>"
        return [generate_entry(request, output, "setup error")]

    registrydir = config["registry_dir"]

    # make sure the registrydir has a / at the end
    if registrydir[-1] != os.sep:
        registrydir = registrydir + os.sep

    # if they are doing the queue thing, then we spin them off to queue
    # stuff.
    if pyhttp["PATH_INFO"].startswith(QUEUETRIGGER):
        data["extensions"]["txt-"] = data["extensions"]["txt"]

        return handle_registry_queue(args)

    # if they are doing the submit thing, then we spin them off to
    # the submit stuff.
    if pyhttp["PATH_INFO"].startswith(SUBMITTRIGGER):
        return handle_registry_submit(args)

    # check if we're looking for a listing of all entries
    if pyhttp["PATH_INFO"] == TRIGGER:
        entries = tools.Walk(request, registrydir)

    else:
        dir2 = pyhttp["PATH_INFO"][len(TRIGGER):]
        filename, ext = os.path.splitext(dir2)
        if os.path.isdir(registrydir + filename):
            entries = tools.Walk(request, registrydir + filename)
        else:
            fn = registrydir + filename[1:]
            fext = tools.what_ext(data["extensions"].keys(), fn)
            entries = [fn + "." + fext]


        if ext[1:]:
            data["flavour"] = ext[1:]

    # that entry doesn't exist....
    if len(entries) == 0:
        output = "<p>No entries of that kind registered here.</p>"
        return [generate_entry(request, output)]
        
    # if we're looking at a specific entry....
    if len(entries) == 1:
        try:
            entry = fileentry.FileEntry(request, entries[0], registrydir, registrydir)
            if entries[0].find("flavours") != -1:
                entry["template_name"] = "flavour-story"
            else:
                entry["template_name"] = "registry-story"

            if entry.has_key("contrib"):
                entry["body"] = entry["body"] + CONTRIB_DESC

            return [entry]
        except Exception, e:
            output = "That plugin does not exist."
            return [generate_entry(request, output)]

    # if we're looking at a bunch of entries....
    if form.has_key("sortby"):
        if form["sortby"].value == "date":
            config['num_entries'] = 9999
            return get_entries_by_date(request, registrydir, entries)
        elif form["sortby"].value == "none":
            return get_entries_by_none(request, registrydir, entries)
        else:
            config['num_entries'] = 9999
            return get_entries_by_item(request, registrydir, entries, form["sortby"].value)

    # return get_entries_by_date(request, registrydir, entries)
    return get_entries_by_none(request, registrydir, entries)
