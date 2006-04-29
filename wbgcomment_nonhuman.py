"""
This works in conjunction with the comments plugin and allows you to
reduce comment spam by adding a "I am human" checkbox to your form.
Any comments that aren't "from a human" get rejected immediately.

This shouldn't be the only way you reduce comment spam.  It's probably
not useful to everyone, but would be useful to some people as a quick
way of catching some of the comment spam they're getting.

For setup, copy the plugin to your plugins directory and add it to
your load_plugins list in your config.py file.

Then add the following to your comment-form template just above
the submit button:

%<------------------------------------
<input type="checkbox" name="iamhuman" value="yes"> Yes, I am human!
%<------------------------------------

Additionally, the wbgcomments_nonhuman plugin can log when it
rejected a comment.  This is good for statistical purposes.
1 if "yes, I want to log" and 0 (default) if "no, i don't want 
to log".

%<---------------------------------------------------
py["comment_rejected_nonhuman_log"] = 1
%<---------------------------------------------------

And that's it!

The idea came from 

   http://www.davidpashley.com/cgi/pyblosxom.cgi/2006/04/28#blog-spam


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

Copyright 2006 Will Guaraldi

SUBVERSION VERSION $Id$

Revisions:
2006-04-28 - Initial writing.
"""
__author__ = "Will Guaraldi - willg at bluesock dot org"
__version__ = "$Date$"
__url__ = "http://www.bluesock.org/~willg/pyblosxom/"
__description__ = "Rejects comments that aren't from a human."

import os, time

def cb_comment_reject(args):
    r = args["request"]
    c = args["comment"]

    config = r.getConfiguration()

    if not c.has_key("iamhuman"):
        if config.get("comment_rejected_nonhuman_log", 0):
            if config.has_key("logdir"):
                fn = os.path.join(config["logdir"], "nothuman.log")
                f = open(fn, "a")
                f.write("%s\n" % time.ctime(time.time()))
                f.close()
        return (1, "Comment rejected: I don't think you're human.")

    return 0
