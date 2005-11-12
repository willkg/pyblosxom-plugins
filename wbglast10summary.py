"""
Thrown-together plugin to summarize all entries after the first five
in the html flavour.

This uses the summary template.  So make sure to build a summary template 
file.  Also, you should probably fiddle with the values in this plugin to 
get it to meet your special needs.

This code is placed in the public domain.  Do with it as you will.

SUBVERSION VERSION: $Id$
"""

__author__ = "Will Guaraldi - willg at bluesock dot org"
__version__ = "$Date$"
__url__ = "http://www.bluesock.org/~willg/pyblosxom/"
__description__ = "Summarizes old posts."


def cb_prepare(args):
    request = args["request"]
    data = request.getData()

    flavour = data.get("flavour", "html")

    # we don't want to do anything if the flavour isn't html
    if not flavour in ["html"]:
        return

    # grab the entry list
    entry_list = data["entry_list"]

    # for all the entries after the 5th one, we set the template_name
    # to summary.
    i = 5
    while i < len(entry_list):
        if entry_list[i].get("template_name", "story") == "story":
            entry_list[i]["template_name"] = "summary"
        i = i + 1
