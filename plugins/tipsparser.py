"""
Summary
=======

An entry parser for tips.  It's like the regular txt parser, but does
some minor formatting and has an understanding of a "changelog".  A
"tips" entry would be named something like::

   datadir/pyblosxom/tips/mytip.tips

and would look like this::

   title: my favorite tip
   changelog: v.1.0 (26 January 2004) - initial writing
   body:
      <p>
      This is my fantabulous tip.
      </p>
   
      <pre class="code">
          def look_at_code_snippet_here(foo):
              ...
      </pre>
   

Nothing wildly exciting, but it might be a nice example of a simple
entry parser plugin.

No configuration variables need to be set.  You can just drop
this in and it'll work.


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

Copyright 2004 Will Guaraldi

SUBVERSION VERSION: $Id$

Revisions:
2007-07-07 - converted documentation to reST.
2005-11-11 - Pulled into new version control system.
1.5 - (26 October, 2005) pulled into new version control system
1.1 - (15 February 2004) adjustments to datafile handling
1.0 - (26 January 2004) initial writing
"""
__author__ = "Will Guaraldi - willg at bluesock dot org"
__version__ = "$Date$"
__url__ = "http://www.bluesock.org/~willg/pyblosxom/"
__description__ = "Parses .tips files as tips files."


def verify_installation(request):
    return 1

def cb_entryparser(args):
    """
    The args dict here should have file extensions as keys (i.e.
    html, txt, tips, dat, ...) and values are the functions that
    parse those files.
    """
    args['tips'] = parse
    return args

def parse(filename, request):
    """
    This takes in a filename, opens up the file, parses the contents,
    and returns a dict containing some properties like "title" and
    "body".
    """
    config = request.getConfiguration()

    try:
        story = open(filename).readlines()
    except IOError:
        raise IOError

    data = {}

    for mem in story:
        if not mem or mem[0] == "#":
            pass

        if len(mem.strip()) == 0 or mem[0] == " " or mem[0] == "\t" and k:
            data[k] = data[k] + "\n" + mem.rstrip()
            continue

        k, v = mem.split(":", 1)
        data[k] = v.rstrip()

    body = []
    body.append(data["body"])
    body.append("<p><b>changelog</b></p>")
    body.append("<ul><li>%s</ul>" % "<li>".join(data["changelog"].split("\n")))

    entry = { 'title': data["title"], 'body': "\n".join(body) }

    return entry
