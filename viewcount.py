"""
This is a silly plugin to keep track of the number of times a given entry
has been viewed and to populate the metadata for an entry to display
that count.

It populates the $viewcount variable with the number of views of this 
entry.

Because it only figures out the viewcount and updates it when it's asked
for, it's not a huge amount of processing time.  So we don't need to
do any fancy caching or anything.  Though clearly this won't scale
to lots and lots of entries.  Probably on the order of 100s possibly
1000s.

This plugin creates a viewcounts.dat file in your datadir to store
the information in.

No configuration is needed by this plugin--it should just work out
of the box.


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
1.8 (31 March 2004) - fixed it so that the count only goes up when someone hits
    the page directly
1.7 (19 February 2004) - minor adjustments to opening the viewcounts.dat file 
    code
1.6 (15 February 2004) - re-added locking
1.5 (13 February 2004) - removed the locking and changed it to use a r+ file
1.4 (21 January 2004) - rewrote lockfile stuff to use Pyblosxom locking
1.3 (14 July 2003) - fixed lockfile/pickling stuff
1.2 (1 June 2003) - added lockfile support
1.1 - overhauled for new plugin system
1.0 - original code 
"""
__author__ = "Will Guaraldi - willg at bluesock dot org"
__version__ = "1.8 (31 March, 2004)"
__url__ = "http://www.bluesock.org/~willg/pyblosxom/"
__description__ = "Tracks how many times an entry has been viewed."

import pickle, time, os.path
from Pyblosxom import tools

def verify_installation(request):
    config = request.getConfiguration()
    datadir = config["datadir"]
    filename = datadir + "/viewcounts.dat"
    try:
        if os.path.isfile(filename):
            f = open(datadir + "/viewcounts.dat", "r+")
        else:
            f = open(datadir + "/viewcounts.dat", "w")
        f.close()
    except Exception, e:
        print "viewcounts cannot write to the '%s' file." % filename
        print "%s" % e
        return 0

    return 1

def cb_start(args):
    """
    We want to grab the lock file so that we don't lose entries in between.
    """
    request = args["request"]
    data = request.getData()
    config = request.getConfiguration()
    datadir = config["datadir"]

    filename = datadir + "/viewcounts.dat"
    
    try:
        if os.path.isfile(filename):
            f = open(filename, "r+")
            tools.lock(f, tools.LOCK_NB | tools.LOCK_EX)
            p = pickle.load(f)
            f.seek(0, 0)
        else:
            f = open(filename, "w")
            tools.lock(f, tools.LOCK_NB | tools.LOCK_EX)
            p = {}
    except:
        f = None
        p = {}


    data["viewcount_fp"] = f
    data["viewcount_picklefile"] = p
    
def cb_story(args):
    """
    This method gets called in the cb_story callback.  Refer to
    the documentation for that.
    """
    entry = args["entry"]
    request = args["request"]
    data = request.getData()

    config = request.getConfiguration()
    datadir = config["datadir"]
 
    if not hasattr(entry, "getId"):
        entry["viewcount"] = "N/A"
        return

    picklefile = data.get("viewcount_picklefile", None)

    id = entry.getId()
    if not id:
        entry["viewcount"] = "N/A"
        return

    if picklefile == None:
        entry["viewcount"] = "Not available"
        return

    if picklefile.has_key(id):
        count = picklefile[id]
    else:
        count = 1

    if entry["bl_type"] == "file":
        count = count + 1

    picklefile[id] = count

    entry["viewcount"] = str(count) + " view(s)"

def cb_end(args):
    request = args["request"]
    config = request.getConfiguration()
    datadir = config["datadir"]
    data = request.getData()

    f = data["viewcount_fp"]
    p = data["viewcount_picklefile"]

    if f:
        pickle.dump(p, f, 1)
        tools.unlock(f)
        f.close()
