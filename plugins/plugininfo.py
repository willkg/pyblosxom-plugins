"""
Summary
=======

This plugin is maintained at::

   http://www.bluesock.org/~willg/pyblosxom/

Check that URL for new versions, better documentation, and submitting
bug reports and feature requests.


Usage
=====

This plugin goes through all the plugins you have installed on your blog
and extracts information about the plugin.

To kick it off, the url starts with ``/plugin_info`` .

If there are plugins you want to run that you don't want showing up,
list them in the ``plugininfo_hide`` property of your ``config.py`` file::

   py["plugininfo_hide"] = ["myplugin", "myotherplugin"]

It takes a list of strings.

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

Copyright 2002-2007 Will Kahn-Greene

SUBVERSION VERSION: $Id$

Revisions:
2007-07-07 - Converted documentation to restructured text.
2007-05-19 - Brushed up the code, fixed documentation, ...
2005-11-11 - Pulled into another new version control system
1.8 - (26 October, 2005) pulled into new version control system
1.7 - (09 December, 2004) fixed date_head issue and stopped showing 
      docstrings
1.6 - (04 May 2004) added comment handling
1.5 - (18 February 2004) added the ability to "hide" plugins so that
      we don't talk about them
1.4 - (17 February 2004) added alphabetical sorting of plugins and fixed
      num_entries issue
1.3 - (14 July 2003) added $plugincount variable
1.2 - (5/27/2003) minor fixes in the build_entry
"""
import Pyblosxom.plugin_utils
import Pyblosxom.entries.base
import time
import os.path

__author__  = "Will Kahn-Greene - willg at bluesock dot org"
__version__ = "$Date$"
__url__     = "https://github.com/willkg/pyblosxom-plugins"
__description__ = "Shows information about plugins that you're running."

TRIGGER = "/plugin_info"

def verify_installation(request):
    config = request.getConfiguration()

    # check to see if the user has specified the "plugininfo_hide" 
    # property
    if not config.has_key("plugininfo_hide"):
        # the user doesn't have the property set, so we let them know
        # they can set it and it prevents specified plugins from showing
        # up.
        print "Note: You can set 'plugininfo_hide' to hide plugins you " + \
              "don't want showing up."

    else:
        # they do have plugininfo_hide set, so we verify that the value
        # is valid-ish.
        val = config["plugininfo_hide"]

        if not type(val) in [ list, tuple ]:
            print "'plugininfo_hide' must be a list of strings."
            return 0

        for mem in val:
            if not type(mem) == str:
                print "'plugininfo_hide' must be a list of strings."
                return 0
    return 1

def build_entry(request, mem):
    """build_entry(Request, plugin) -> PyBlosxom.entries.base.BaseEntry

    Takes a plugin, extracts information from it, and builds a PyBlosxom
    entry from the results.  It returns the BaseEntry object.
    """
    plugindata = []
    plugindata.append("<pre>")

    # previously we pulled __doc__, but more and more people are storing
    # documentation for the plugin as well as license information--which
    # isn't really what we want to show.  we really want the author, version,
    # and url for the plugin.  currently these are stored in __author__,
    # __version__, and __url__ (though those should be changed to something
    # like VERSION, AUTHOR, and URL so as to avoid confusion with Python
    # special things.
    plugindata.append("AUTHOR: " + str(getattr(mem, "__author__", None)) + "\n")
    plugindata.append("VERSION: " + str(getattr(mem, "__version__", None)) + "\n")
    if hasattr(mem, "__url__"):
        plugindata.append("URL: <a href=\"%s\">%s</a>\n" % \
                          (str(mem.__url__), str(mem.__url__)))

    plugindata.append("</pre>")

    # build a dict of the metadata that generate_entry needs
    d = { "title": mem.__name__,
          "absolute_path": TRIGGER[1:],
          "fn": mem.__name__,
          "file_path": TRIGGER[1:] + "/" + mem.__name__ }

    # build the body of the entry
    body = "".join(plugindata)

    entry = Pyblosxom.entries.base.generate_entry(request, d, body, None)
    return entry

def cb_prepare(args):
    request = args["request"]
    data = request.getData()
    config = request.getConfiguration()
    antiplugins = config.get("plugininfo_hide", [])

    plugins = Pyblosxom.plugin_utils.plugins
    plugins = [m for m in plugins if m.__name__ not in antiplugins]

    data["plugincount"] = len(plugins)


INIT_KEY = "plugininfo_initiated"

def cb_date_head(args):
    """
    If we're showing plugins, then we don't want the date_head templates
    kicking in--so we block that.
    """
    request = args["request"]
    data = request.getData()

    if data.has_key(INIT_KEY):
        args["template"] = ""
    return args

def cb_staticrender_filelist(args):
    """
    This is test code--trying to work additional bits into the static
    renderer.
    """
    request = args["request"]
    filelist = args["filelist"]
    flavours = args["flavours"]

    config = request.getConfiguration()

    antiplugins = config.get("plugininfo_hide", [])

    plugins = Pyblosxom.plugin_utils.plugins
    plugins = [m for m in plugins if m.__name__ not in antiplugins]

    if plugins:
        for mem in plugins:
            url = os.path.normpath(TRIGGER + "/" + mem.__name__ + ".")
            for f in flavours:
                filelist.append( (url + f, "") )
        for f in flavours:
            filelist.append( (os.path.normpath(TRIGGER + "/index." + f), "") )

    
def cb_filelist(args):
    request = args["request"]
    pyhttp = request.getHttp()
    data = request.getData()
    config = request.getConfiguration()

    if not pyhttp["PATH_INFO"].startswith(TRIGGER):
        return

    data[INIT_KEY] = 1
    data['root_datadir'] = config['datadir']
    config['num_entries'] = 9999
    entry_list = []

    antiplugins = config.get("plugininfo_hide", [])

    plugins = Pyblosxom.plugin_utils.plugins
    plugins = [m for m in plugins if m.__name__ not in antiplugins]

    pathinfo = pyhttp["PATH_INFO"]

    # if the browser requested the TRIGGER or TRiGGER/index, then we
    # kick in and show plugin information for all plugins.
    if pathinfo == TRIGGER or pathinfo.startswith(TRIGGER + "/index"):
        plugins.sort(lambda x,y: cmp(x.__name__, y.__name__))
        for mem in plugins:
            entry_list.append(build_entry(request, mem))
        return entry_list

    # the browser requested to see information on a specific plugin.

    # we need to pull off the flavour that was requested
    # (if there was one).  FIXME - this is a good candidate for a tools
    # function.
    pathinfo = pathinfo[len(TRIGGER):]

    if pathinfo.startswith("/"): pathinfo = pathinfo[1:]
    if pathinfo.endswith("/"): pathinfo = pathinfo[:-1]

    filename, ext = os.path.splitext(pathinfo)
    if ext[1:]:
        data["flavour"] = ext[1:]

    d = {}
    for mem in plugins:
        d[mem.__name__] = mem

    # if the browser requested to look at a specific plugin, then
    # we only show that one.
    if d.has_key(filename):
        return [build_entry(request, d[filename])]

    # if the plugin the browser requested isn't in the list of
    # plugins, then we return an empty list of entries--PyBlosxom
    # will show a "that doesn't exist" message for that.
    return []

# vim: tabstop=4 shiftwidth=4
