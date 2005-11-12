"""
I have a books.dat file which is a :: delimited listing of the books I've 
read or am in the process of reading.  This module takes that listing
and converts it into a quick thing for display on my web-site.

Each line in the file is in the form:

START_DATE::COMPLETENESS::NAME::ISBN::AUTHOR::COMMENTS

It's not really designed to keep track of all the books you read, but
rather to keep track of the books on your reading table.  Then maybe
you could write up an entry for when you finished the book with your
more complete thoughts on it.  (shrug)

config variables:

   amazon_store - the amazon store for building the urls


It creates the variable $booklist for your main page.  It will list
the top five books (sorted by completeness--i.e. how much of the book
you've completed [I use % like 50%, 60%, done...]).  Then it'll have
a "more..." link which will link to a complete listing of all the books
stored ("/booklist/").  The listing of books uses your regular flavour 
taste (html, rss, whatever...).  It uses the "booklist" template to 
render each booklist entry.  My booklist.html file looks like this:

%<-------------------------- booklist.html -------------
<p>
   <img src="$img_isbn">
</p>
<p>
   <u>$title</u>, by $author<br />
   ISBN: $isbn <font size=-1><a href="$amazon_link">Buy at Amazon</a></font><br />
   <br />
   Started reading: $start_date ($completeness)<br />
   Comments: $comments<br />
</p>
%<------------------- end of booklist.html -------------

The variable available to booklist entries are as follows:

   $title - the title of the book
   $author - the author of the book
   $isbn - the isbn number
   $comments - your comments
   $start_date - the date that you started reading the book
   $completeness - the amount of the book you've completed

And then there are some composite variables available:

   $img_isbn - a url composed of the isbn number which points to
               amazon's site for the mini-image
   $amazon_link - a link created by the isbn number and the amazon
               store variable you specified in the config file


Hope that helps.


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

SUBVERSION VERSION: $Id$

Revisions:
2005-11-12 - pulled into another new version control system.
1.8 - (26 October, 2005) pulled into a new version control system
1.7 - (09 December, 2004) fixed date_head issue
1.6 - (14 September, 2004) fixed for better comments integration (thanks Brett!)
1.5 - (07 May, 2004) fixed for static rendering
1.4 - adjusted to use a flavour instead of a taste
1.3 - overhauled for templates
1.2 - added ISBN, amazon polling (for images), and amazon links
1.1 - minor adjustments
1.0 - created
"""
__author__ = "Will Guaraldi - willg at bluesock dot org"
__version__ = "$Date$"
__url__ = "http://www.bluesock.org/~willg/pyblosxom/"
__description__ = "Shows information about what books you're reading."

START_DATE = 0
COMPLETENESS = 1
NAME = 2
ISBN = 3
AUTHOR = 4
COMMENTS = 5

TRIGGER = "/booklist"

import time
from Pyblosxom import tools, entries

def verify_installation(request):
    config = request.getConfiguration()
    if not config.has_key("amazon_store"):
        print "Note: you can set 'amazon_store' in your config.py file which "
        print "adds the store to the url."

    return 1

def populate_list(request):
    config = request.getConfiguration()
    datadir = config["datadir"]

    f = open(datadir + "/books.dat", "r")
    lines = f.readlines()
    f.close()

    booklist = []
    for mem in lines:
        # handle comments
        if mem.startswith("#"):
            continue

        # handle blank lines
        if len(mem.strip()) == 0:
            continue

        # handle continuations
        if mem.startswith("\t"):
            mem = " " + mem.rstrip()
            booklist[-1][-1] = booklist[-1][-1] + mem
            continue

        booklist.append(mem.split("::"))

    return booklist

class Booklist:
    def __init__(self, request):
        self._request = request
        self._booklist = None

    def __str__(self):
        if not self._booklist:
            self._booklist = populate_list(self._request)

        listing = self._booklist[:]

        listing.sort(lambda x,y:cmp(x[1], y[1]))

        if len(listing) > 5:
            listing = listing[:5]

        output = []
        for mem in listing:
            output.append("%s::%s<br /><u>%s</u>, by %s<br /><br />" % 
                 (mem[START_DATE], mem[COMPLETENESS], mem[NAME], mem[AUTHOR]))

        pyhttp = self._request.getHttp()
        config = self._request.getConfiguration()
        output.append("<a href=\"" + config["base_url"] + TRIGGER + "\">more...</a><br />")
        return "\n".join(output)

def cb_prepare(args):
    request = args["request"]
    data = request.getData()

    data["booklist"] = Booklist(request)

def generate_entry(request, book, amazon_store):
    """
    Takes a bunch of variables and generates an entry out of it.  It creates
    a timestamp so that conditionalhttp can handle it without getting
    all fussy.
    """
    entry = entries.base.EntryBase(request)

    entry['title'] = book[NAME]
    entry['filename'] = "booklist." + book[NAME]
    entry['file_path'] = "booklist"
    entry._id = "booklist" + "::" + book[NAME]

    entry["absolute_path"] = TRIGGER
    entry["file_path"] = TRIGGER[1:] + "/" + book[ISBN]
    entry["fn"] = book[ISBN]

    entry['isbn'] = book[ISBN]
    entry['author'] = book[AUTHOR]
    entry['start_date'] = book[START_DATE]
    entry['completeness'] = book[COMPLETENESS]
    entry['comments'] = book[COMMENTS]
    entry['amazon_store'] = amazon_store

    # not sure how to do this better....
    if book[ISBN]:
       entry['img_isbn'] = 'http://images.amazon.com/images/P/' + book[ISBN] + '.01.TZZZZZZZ.jpg'
    else:
       entry['img_isbn'] = ''

    if book[ISBN] and amazon_store:
       entry['amazon_link'] = 'http://www.amazon.com/exec/obidos/ASIN/%s/%s' % (book[ISBN], amazon_store)
    else:
       entry['amazon_link'] = ''

    entry["template_name"] = "booklist"

    entry.setTime(time.localtime())
    entry.setData(book[COMMENTS])

    return entry

INIT_KEY = "booklist_static_file_initiated"

def cb_date_head(args):
    request = args["request"]
    data = request.getData()

    if data.has_key(INIT_KEY):
        args["template"] = ""
    return args

def cb_staticrender_filelist(args):
    request = args["request"]
    filelist = args["filelist"]
    flavours = args["flavours"]

    for f in flavours:
        filelist.append((TRIGGER + "/index." + f, ""))

def cb_filelist(args):
    request = args["request"]
    pyhttp = request.getHttp()
    data = request.getData()
    config = request.getConfiguration()
    if not pyhttp["PATH_INFO"].startswith(TRIGGER):
        return

    data["blog_title"] = config.get("blog_title", "") + " - booklist"

    config['num_entries'] = 9999
    data[INIT_KEY] = 1

    booklist = populate_list(request)[:]
    booklist.sort(lambda x,y:cmp(x[1], y[1]))

    if config.has_key("amazon_store"):
        amazon_store = config["amazon_store"]
    else:
        amazon_store = ""

    entrylist = []
    for mem in booklist:
        mem[ISBN] = mem[ISBN].strip()
        entrylist.append(generate_entry(request, mem, amazon_store))

    return entrylist
