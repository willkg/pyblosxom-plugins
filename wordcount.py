"""
This is a basic plugin that counts the number of words in each entry
and populates the metadata with that count.

It happens in the cb_story callback, so it only runs for entries that
are about to be rendered.

It counts the words from getData so that it can work on any entry type.

It populates the $wc variable with the word count.

There is no config properties to set up--you can drop this plugin in
and it will work fine.


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

Revisions:
1.2 - did some more stuff
1.1 - did some stuff
1.0 - initial writing
"""
__author__ = "Will Guaraldi - willg at bluesock dot org"
__version__ = "1.2"
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
