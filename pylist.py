# vim: tabstop=4 shiftwidth=4 expandtab
"""
Pylist takes a plain text file and turns it into a unorderd list that can be
renderd as a part of the blog, for example a list of books you're reading, some
links, a smal image gallery etc.

It is configured with the following variables:

# What lists do we want to render
py['lists'] = ['links','books']

# the linklist consists of entrys on the format:
# <category>::<url>::<title>::<description>
py["lists"] = ["users"]
py['list-users-file']   = "links.dat"       # the filename, relative the blog root
py['list-users-format'] = [["GROUP","SORT"],[],[],[]]   # sort and group the entrys
                                            # acording to the category
py['list-users-output'] = "<a href='%(1)s' title='%(3)s'>%(2)s</a>" # The format of each entry
                                            # the format is used with pythons % operator
py['list-users-max']    = 10                # Number of links to show on in the list
py['list-users-more']   = "More links..."   # Text of the link to show more items


# A basic booklist.
# <category>::<title>::<author>
py['list-books-file']   = "books.dat"
py['list-books-format'] = [["GROUP","SORT"],[],["GROUP"]]
py['list-books-output'] = "%(1)s"
py['list-books-max']    = 10
py['list-books-more']   = ""


The basic idea comes from the booklist plugin by Will Guaraldi

"""
import Pyblosxom, os
from Pyblosxom.Request import Request
from Pyblosxom.renderers.blosxom import BlosxomRenderer
from Pyblosxom.entries.base import EntryBase
from Pyblosxom.pyblosxom import PyBlosxom


class PyblosxomList:
    def __init__(self, request, list):
        self._request = request
        self._listname = list
        self._list = None
        self._output = None

    def __str__(self):
        if not self._output:
            config = self._request.getConfiguration()
            file = config.get("list-%s-file"%self._listname,"")
            format = config.get("list-%s-format"%self._listname,[[]])
            output = config.get("list-%s-output"%self._listname,"")
            max = config.get("list-%s-max"%self._listname,0)
            more = config.get("list-%s-more"%self._listname,"")

            if not self._list:
                self.fill_list(config["datadir"]+"/"+file)


            list = self._list[-max:]

            groupby=[]
            curgroup=map(lambda a:None,range(len(format)))
            for i in range(0,len(format)):
                if "GROUP" in format[i]:
                    groupby.append(i)
                if "SORT" in format[i]:
                    list.sort(lambda a,b:cmp(a[i],b[i]))

            repr = ["<ul>"]
            for a in list:
                for g in groupby:
                    if a[g] <> curgroup[g]:
                        if curgroup[g]:
                            repr.append(" "*g+"</li></ul>")
                for g in groupby:
                    if a[g] <> curgroup[g]:
                        repr.append(" "*g+"<li>%s<ul>"%a[g])
                        curgroup[g] = a[g]

                repr.append(("<li>%s</li>"%output)%dict(map(None,map(str,range(len(a))),a)))
            repr.append("</ul>")
            self._output= "\n".join(repr)
            if len(self._list)>max :
                self._output += '\n<a href="%s/%s">%s</a>\n'%(config.get("base_url",""),file,more)
        return self._output

    def fill_list(self,file):
        f = open(file, "r")
        lines = f.readlines()
        f.close()

        self._list = []
        for line in lines:
            if line and line[1]!="#":
                self._list.append(line.split("::"))

    def page(self):
        config = self._request.getConfiguration()
        file = config.get("list-%s-file"%self._listname,"")
        format = config.get("list-%s-format"%self._listname,[[]])
        output = config.get("list-%s-output"%self._listname,"")
        max = config.get("list-%s-max"%self._listname,0)
        more = config.get("list-%s-more"%self._listname,"")

        if not self._list:
            self.fill_list(config["datadir"]+"/"+file)

        list = self._list

        groupby=[]
        curgroup=map(lambda a:None,range(len(format)))
        for i in range(0,len(format)):
            if "GROUP" in format[i]:
                groupby.append(i)
            if "SORT" in format[i]:
                list.sort(lambda a,b:cmp(a[i],b[i]))

        repr = ["<ul>"]
        for a in list:
            for g in groupby:
                if a[g] <> curgroup[g]:
                    if curgroup[g]:
                        repr.append(" "*g+"</li></ul>")
            for g in groupby:
                if a[g] <> curgroup[g]:
                    repr.append(" "*g+"<li>%s<ul>"%a[g])
                    curgroup[g] = a[g]

            repr.append(("<li>%s</li>"%output)%dict(map(None,map(str,range(len(a))),a)))
        repr.append("</ul>")
        self._output= "\n".join(repr)
        if len(self._list)>max :
            self._output += '\n<a href="%s/%s">%s</a>\n'%(config.get("base_url",""),file,more)

        return self._output


def cb_prepare(args):
    """
    We get the config and then create objects for each list.
    """
    request = args["request"]
    config = request.getConfiguration()
    data = request.getData()

    for list in config.get('lists',""):
        data["%s-list"%list] = PyblosxomList(request,list)


def cb_filelist(args = {'request' : Request()}):
    """
    A callback to generate a list of L{EntryBase} subclasses.

    If C{None} is returned, then the callback chain will try the next plugin in
    the list.

    @param args: A dict containing a L{Request()} object
    @type args: dict
    @returns: None or list of L{EntryBase}.
    @rtype: list
    """
    request = args["request"]
    config = request.getConfiguration()
    data = request.getData()
    pyhttp = request.getHttp()
    for list in config.get('lists',""):
        if pyhttp["PATH_INFO"].startswith("/"+config.get("list-%s-file"%list,"")):
            return data["%s-list"%list].page()
    return
