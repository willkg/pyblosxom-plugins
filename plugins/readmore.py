"""
Summary
=======

readmore.py is a plugin that associates a specific string in an entry as a
breakpoint. It will replace that string with another and hide the rest of the
entry text. That new string is a link to viewing the rest of the text.

Configuration
=============

1. copy readmore.py into your plugins directory
2. enable it by adding ``readmore`` to the ``py['load_plugins']`` list 
   variable in your config.py file (probably located in a cgi-bin directory).
3. alter the values of ``py['readmore_breakpoint']`` and 
   ``py['readmore_template']`` in your config.py file.
4. edit an entry and add the value of ``py['readmore_breakpoint']`` to the 
   text between paragraphs at a logical breakpoint.  I insert my breakpoint 
   after the first or second paragraph - or not at all if the entry is short.
5. reload the blog in your browser and test away.
             
This breakpoint text and the assocated replacement text are configured in
config.py with these two values (one a string, the other a string or list of
two strings)::

    py['readmore_breakpoint'] - the breakpoint, default is "B R E A K"
               (just take out the spaces)

    py['readmore_template'] - the replacement text, default is
               ['<br /><br />::<a href="%(url)s">READ MORE</a>',
               '<br /><br /><span style="color: red;">::READ HERE</span>']

In this example (the default case) the breakpoint will be replaced with two
empty lines and ``::READ MORE`` that is a link to the rest of the entry.  In
this example, if you put more than one breakpoint in the second value of
``py['readmore_template']`` the full entry will be returned, but with the 
text of the breakpoints replaced with that second string (by default a red
``::READ HERE``). This gives you some creative freedom with how you would
like to format the output using the breakpoints.

The normal usecase is using only one breakpoint in an entry.

These two values can be changed of course.  Here's a sample configuration::

    py['readmore_breakpoint'] = '<!--B R E A K-->' # again remove the spaces
    py['readmore_template'] = '<p class="readmore"><a href="%(url)s">more &raquo;</a></p>'

It helps to use ``<!--`` and ``-->`` comment strings so if you ever decide 
not to continue using the readmore plugin, the breakpoints won't be visible 
to readers.

In the ``py['readmore_template']`` variable (a string or a list of two 
strings), you can use the following designators:

* ``%(url)s``       - the full path to the story
* ``%(base_url)s``  - base_url
* ``%(flavour)s``   - the flavour selected now
* ``%(file_path)s`` - path to the story (without extension)


Note from Will Kahn-Greene (October 25, 2005)
==========================================

I'm assuming IWS doesn't care about this anymore so I'm going to "fork"
the plugin and take over development and hosting for it.  I've made minor
adjustments to it.


Note regarding readmore and rss2renderer
========================================

This plugin does NOT work with the rss2renderer plugin.


----

SUBVERSION VERSION: $Id$

Revisions:
2007-07-07 - converted documentation to reST.
2006-10-25 - Pulled in lots of changes suggested by Todd Warner, fixed
      the documentation, other minor changes.
2005-11-11 - Pulled into another new version control system.
1.5 - (26 October, 2005) pulled into new version control system
0.5 - (October 25, 2005) Changed the ^L to B R E A K, fixed some instructrions
      and took over hosting.

Original author:    IWS
Current maintainer: Will Kahn-Greene
Contributors:
    Todd Warner
    others....

License: Python or GNU
"""

__author__ = "maintainer: Will Kahn-Greene - willg at bluesock dot org"
__version__ = "$Date$"
__license__ = "python or GNU"
__url__ = "https://github.com/willkg/pyblosxom-plugins"
__description__ = "Breaks a long story at B R E A K (no spaces)."

import re
from Pyblosxom import tools

def cb_story(args):
    logger = tools.getLogger()
    
    pagedelimiter = 'BREAK'
    continue_template = '<br /><br />::<a href="%(url)s">READ MORE</a>'
    continued_template = '<br /><br /><span style="color: red;">::READ HERE</span>'
    entry = args['entry']
    if not entry.has_key('body'):
        return

    # override default breakpoint (pagedelimiter) if applicable from the
    # config.py file.
    if args['entry'].has_key('readmore_breakpoint'):
        readmore_breakpoint = args['entry']['readmore_breakpoint']
        if isinstance(readmore_breakpoint, type('')):
            pagedelimiter = readmore_breakpoint
        else:
            logger.error("py['readmore_breakpoint'] value is not a " + \
                         "string. It's type seems to be: %s" % \
                         type(readmore_breakpoint))

    # find the delimiter in the body of the text                         
    match = re.search(pagedelimiter, entry['body'])

    if match:
        if args['entry'].has_key('readmore_template'):
            readmore_template = args['entry']['readmore_template']
            if isinstance(readmore_template, type('')):
                continue_template = readmore_template
                continued_template = ''
            elif isinstance(readmore_template, type([])):
                if not readmore_template:
                    logger.error("py['readmore_template'] is an empty list.")
                else:
                    continue_template = readmore_template[0]
                    if len(readmore_template) > 1:
                        continued_template = readmore_template[1]
            else:
                logger.error("py['readmore_template'] value is neither " + \
                             "a string nor a list.  It's type seems to " + \
                             "be: %s" % type(readmore_template))

        if entry['bl_type' ] == 'file':
            entry['body'] = re.sub(pagedelimiter,
                                   continued_template,
                                   entry['body'])
        else:
            base_url = entry['base_url']
            file_path = entry['file_path']
            flavour = entry['flavour']
            m = {'url':'%s/%s.%s' % (base_url, file_path, flavour),
                 'base_url':base_url,
                 'file_path':file_path,
                 'flavour':flavour}
            entry['body'] = entry['body'][:match.start()]
            entry['body'] += continue_template % m
