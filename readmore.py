"""
readmore.py - break a long story at B R E A K (with no spaces) in the top page.
the readmore message is formated by py['readmore_template'] in config.py.
In this variable(a string or a list of two string), you can the following
designators:

%(url)s		the full path to the story
%(base_url)s	base_url
%(flavour)s	the flavour selected now
%(file_path)s	path to the story (without extension)

It default value is: 

   '<br /><br />::<a href="%(url)s">READ MORE</a>'

Using the default value, after an empty line, '::READ MORE' is placed 
to navigate to the story.

Note from Will Guaraldi (October 25, 2005):

I'm assuming IWS doesn't care about this anymore so I'm going to "fork"
the plugin and take over development and hosting for it.  I've made minor
adjustments to it.


NOTE: this plugin doesn't work with the rss2renderer plugin.


CVS VERSION: $Id: readmore.py,v 1.5 2005/10/26 18:38:49 willg Exp $

Revisions:
1.5 - (26 October, 2005) pulled into new version control system
0.5 - (October 25, 2005) Changed the ^L to B R E A K, fixed some instructrions
      and took over hosting.
"""

# ORIGINAL AUTHOR
# __author__ = "IWS - iws@iws.dyndns.org"

# CURRENT MAINTAINER
__author__ = "IWS, maintainer: Will Guaraldi - willg at bluesock dot org"
__version__ = "$Revision: 1.5 $ $Date: 2005/10/26 18:38:49 $"
__licence__ = "python or GNU"
__url__ = "http://www.bluesock.org/~willg/pyblosxom/"
__description__ = "Breaks a long story at B R E A K (no spaces)."

import re

def cb_story(args):
    pagedelimiter = 'BREAK'
    continue_template = '<br /><br />::<a href="%(url)s">READ MORE</a>'
    continued_template = '<br /><br /><font color="red">::READ HERE</font>'
    entry = args['entry']
    if not entry.has_key('body'):
        return

    match = re.search(pagedelimiter, entry['body'])

    if match:
        if args['entry'].has_key('readmore_template'):
            readmore_template = args['entry']['readmore_template']
            if isinstance(readmore_template, basestring):
                continue_template = readmore_template
                continued_template = ''
            elif isinstance(readmore_template, list):
                continue_template = readmore_template[0]
                if len(readmore_template) > 1:
                    continued_template = readmore_template[1]
        if entry['bl_type' ] == 'file':
            entry['body'] = re.sub(pagedelimiter,
                                   continued_template,
                                   entry['body'])
        else:
            base_url = entry['base_url']
            file_path = entry['file_path']
            flavour = entry['flavour']
            tuple = {'url':'%s/%s.%s' % (base_url, file_path, flavour),
                     'base_url':base_url,
                     'file_path':file_path,
                     'flavour':flavour}
            entry['body'] = entry['body'][:match.start()]
            entry['body'] += continue_template % tuple
