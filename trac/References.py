"""
Summary
=======

This macro goes through a wiki page, finds external links, and then
displays them as an unordered list.


Usage
=====

Drop the plugin into your ``wiki-macros`` directory and use the macro
like this::

   [[References()]]

----

This is in the public domain--use it as you like.  If you discover
bugs in it, please let me know.

Will Guaraldi - willg at bluesock dot org
Version 1.0:  August 15th, 2006
"""
from StringIO import StringIO
from trac.util import escape
import re

LINKRE = re.compile(r"\[(http[^\]]+)\]")

def execute(hdf, args, env):
    db = env.get_db_cnx()
    cursor = db.cursor()

    pn = hdf.getValue("wiki.page_name", "")
    pn.replace("'", "''")

    sql = "select text from wiki " + \
          "where version = " + hdf.getValue("wiki.version", "1") + " " + \
          "and name = '" + pn + "'"
    cursor.execute(sql)

    text = cursor.fetchone()[0]

    d = {}
    for line in text.splitlines():
        m = LINKRE.search(line)
        if m:
            link = m.group(1)
            if " " in link:
                url, desc = link.split(" ", 1)
            else:
                url = link
                desc = ""

            if not d.has_key(url) or not d[url]:
                d[url] = desc

    buf = StringIO()
    buf.write("<ul>")

    keys = d.keys()
    keys.sort()

    for k in keys:
       if d[k]:
          buf.write('<li><a href="%s">%s (%s)</a></li>' % (k, d[k], k))
       else:
          buf.write('<li><a href="%s">%s</a></li>' % (k, k))

    buf.write("</ul>")
    
    return buf.getvalue()
