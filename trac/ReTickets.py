"""
Summary
=======

This produces a list of tickets for a specified component.
Note that *component* in this context refers to Trac tickets.


Usage
=====

Drop the plugin in your ``wiki-macros`` directory and the
macro looks like this::

   [[ReTickets(component)]]


For example, I have a component in my Trac instance called
"ReTickets" and the macro I include is::

   [[ReTickets(ReTickets)]]


Versions
========

This works with Trac 10.4, but hasn't been tested with other versions
of Trac.

----

This is in the public domain--use it as you like.  If you discover
bugs in it, please let me know.

Will Guaraldi - willg at bluesock dot org
Version 1.0:  July 7th, 2007
"""

import time
import re
from StringIO import StringIO

def execute(hdf, args, env):
    db = env.get_db_cnx()
    cursor = db.cursor()

    component = ''
    if args:
        argv = [arg.strip() for arg in args.split(',')]
        if len(argv) > 0:
            component = argv[0]

    cursor.execute( """SELECT id, owner, summary, description 
                       FROM ticket 
                       WHERE component = '%s' 
                       AND status IN ('new', 'assigned', 'reopened') 
                    """ %
                    component )

    buf = StringIO()
    while 1:
        row = cursor.fetchone()
        if row == None:
            break

        buf.write('<a href="%s" title="ticket: %s: %s">[#%s(%s)]</a>' % 
                  (env.href.ticket(row[0]), row[0], row[2].replace("\"", "'"), 
                   row[0], row[1]))

    buf = buf.getvalue()
    if buf:
        return buf

    return "None"
