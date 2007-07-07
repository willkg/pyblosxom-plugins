"""
This is a basic plugin that counts the number of words in each entry
and populates the metadata with that count.

It happens in the cb_story callback, so it only runs for entries that
are about to be rendered.

It counts the words from getData so that it can work on any entry type.

It populates the $wc variable with the word count.

There is no config properties to set up--you can drop this plugin in
and it will work fine.


This plugin is released into the public domain.  Do with it as you will.

Revisions:
2005-11-11 - Pulled into new VCS.
1.2 - did some more stuff
1.1 - did some stuff
1.0 - initial writing
"""
__author__ = "Will Guaraldi - willg at bluesock dot org"
__version__ = "$Date$"
__url__ = "http://www.bluesock.org/~willg/pyblosxom/"
__description__ = "Counts how many words are in an entry."


def verify_installation(request):
    """
    This is for verifying that this is installed correctly.
    """
    return 1

def cb_story(args):
    """
    This method gets called in the cb_story callback.  Refer to
    the documentation for that.
    """
    entry = args["entry"]

    story = entry.getData()
    wc = len(story.split())
    entry["wc"] = str(wc)
