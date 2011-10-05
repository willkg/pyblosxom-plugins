"""
Summary
=======

Ultra-uninteresting plugin for converting an ASIN and name into an
amazon store link html thing.

Amazon thingy needs to start at the beginning of the line and be in 
this format::

   AMAZON::asin::title

For example::

   AMAZON::0385418957::Seven Pillars of Wisdom, by T.E. Lawrence

This theoretically works for books as well as other thing.  The html 
template and amazon store are both hardcoded.

This code is placed in the public domain--use it as you so desire.

----

SUBVERSION VERSION: $Id$

Revisions:
2007-07-07 - converted documentation to reST.
2005-11-11 - Pulled into new VCS.
1.4 - (26 October, 2005) pulled into new VCS
1.3 - (August 17, 2004) Fixed the documentation which was wrong and
                        fixed the RSS handling
1.2 - (July 13, 2004) Fixed problems with RSS generation
1.1 - (May 16, 2004) Fixed a bug when creating Amazon links
1.0 - (March 31, 2004) created
"""
__author__ = "Will Kahn-Greene - willg at bluesock dot org"
__version__ = "$Date$"
__url__ = "https://github.com/willkg/pyblosxom-plugins"
__description__ = "Amazon link generator."

AMAZON_STORE = "bluesockorg-20"
TEMPLATE = """
<table>
<tr>
   <td valign="top"><img src="%(img)s" /></td>
   <td>
<p>
<u>%(title)s</u><br />
<b>ASIN:</b> %(asin)s <font size="-1"><a href="%(link)s">Buy at Amazon</a></font><br />
</p>
   </td>
</tr>
</table>
"""

def amazon(line):
  if not line.startswith("AMAZON"):
    return line

  line = line.split("::")
  arg1 = line[1]
  arg2 = line[2]


  a = {"asin": arg1,
       "title": arg2,
       "img": "http://images.amazon.com/images/P/" + arg1 + ".01.TZZZZZZZ.jpg",
       "link": "http://www.amazon.com/exec/obidos/ASIN/%s/%s" % (arg1, AMAZON_STORE) }

  return TEMPLATE % a

def cb_story(args):
  request = args["request"]
  data = request.getData()
  contenttype = data["content-type"]

  entry = args["entry"]
  body = entry["body"]

  entry["body"] = "\n".join([amazon(m) for m in body.splitlines()])
