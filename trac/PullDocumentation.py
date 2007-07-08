"""
Summary
=======

This is some half-ass code that pulls text from the target file in
SVN and reproduces it in the wiki.  I use it to make it easier to
maintain documentation for plugins in the docstring of the plugin
and have it show up in the wiki as well.


Usage
=====

Drop it in your ``wiki-macros`` directory and then use the following
macro::

   [[PullDocumentation(/path/to/file)]]


For example, the line for this document is::

   [[PullDocumentation(/trunk/trac/PullDocumentation.py)]]


This plugin finds the first docstring in the file (it assumes Python--if
you want something different, you should take it and edit it), passes
it through the restructured text renderer, and returns the resulting
XHTML which replaces the macro tag.


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
from StringIO import StringIO
from trac.util import escape
import re

def execute(hdf, args, env):
    rep = env.get_repository()

    component = ''
    if args:
        argv = [arg.strip() for arg in args.split(',')]
        if len(argv) > 0:
            component = argv[0]

    node = rep.get_node(component)

    inblock = False
    lines = []

    text = node.get_content().read()

    for line in text.split("\n"):
        if line.startswith('"""'):
            inblock = not inblock
            continue

        if line.startswith('----'):
            break

        if inblock:
            lines.append(line)

    text = "\n".join(lines)

    # grab the req which is in the previous frame (annoyingly)
    import inspect
    req = inspect.currentframe().f_back.f_locals["req"]

    # grab the restructured text mimeview thing which can render
    # the text into an XHTML string which we return.
    from trac.mimeview.api import get_mimetype, Mimeview

    mimetype = get_mimetype("temp.rst", text)
    mview = Mimeview(env)

    renderedtext = mview.render(req, mimetype, text)

    return renderedtext
