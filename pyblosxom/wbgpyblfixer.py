"""
Summary
=======

Plugin to help those of us who can never spell PyBloxosom right.


Usage
=====

Drop it in your plugins directory and add ``wbgpyblfixer`` to your
load_plugins list.  Then it'll correct funky spellings of PyBlosxom
to the actual spelling.


----

This code is placed in the public domain--use it as you so desire.

SUBVERSION VERSION: $Id$

Revisions:
2007-07-07 - Converted documentation to reST.
2006-05-11 - First writing to help Carol.
"""
import re

REGEXP = re.compile(r'p[^x\s]+x[^m\s]+m', re.I)

def good_character(c):
   return c.isspace() or c == "."

def filter_text(body):
   r = REGEXP.search(body)
   while r:
      if r.start() == 0 or good_character(r.string[r.start() - 1]):
         if r.end() == len(r.string) or good_character(r.string[r.end()]):
            body = body[:r.start()] + "PyBlosxom" + r.string[r.end():]
      r = REGEXP.search(body, r.end())
   return body

def cb_story(args):
   entry = args["entry"]
   body = entry["body"]

   entry["body"] = filter_text(body)

   return args


# this is for testing to make sure I got the filter_test function
# right.
if __name__ == "__main__":
   def run_test(item):
      print "'" + item + "'", filter_text(item)

   run_test("pyblosxom")
   run_test(" pyblosxom")
   run_test("pyblosxom ")
   run_test("pyblosxomm")
   run_test("dpyblosxom")
   run_test("dpyblosxom pyblosxom")
   run_test("pyblosxom m pyblosxom")
   run_test("pyblosxom m pdyblosxom")
   run_test("still using PyBlosxom to")
   run_test("track PyBlosxom down PyBlosxom issues")
   run_test("track PBosxom down PyBlosxom issues")
