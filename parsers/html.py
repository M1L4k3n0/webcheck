
# html.py - parser functions for html content
#
# Copyright (C) 1998, 1999 Albert Hopkins (marduk) <marduk@python.net>
# Copyright (C) 2002 Mike W. Meyer <mwm@mired.org>
# Copyright (C) 2005 Arthur de Jong <arthur@tiefighter.et.tudelft.nl>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA

"""Parser functions for processing HTML content."""

import htmllib
import string
import debugio
import formatter
import sgmllib
import urlparse

mimetypes = ('text/html', 'application/xhtml+xml', 'text/x-server-parsed-html')

# TODO: switch to using HTMLParser (not from htmllib)

class _MyHTMLParser(htmllib.HTMLParser):

    def __init__(self,formatter):
        self.imagelist = []
        self.title = None
        self.author = None
        self.base = None
        htmllib.HTMLParser.__init__(self,formatter)

    # override handle_image()
    def handle_image(self,src,alt,*stuff):
        if src not in self.imagelist:
            self.imagelist.append(src)

    def do_frame(self,attrs):
        for name, val in attrs:
            if name=="src":
                self.anchorlist.append(val)

    def save_bgn(self):
        self.savedata = ''

    def save_end(self):
        data = self.savedata
        self.savedata = None
        return data

    def start_title(self, attrs):
        self.save_bgn()

    def end_title(self):
        #if not self.savedata:
        #    self.title = None
        #    return
        self.title = string.join(string.split(self.save_end()))

    def do_meta(self,attrs):
        fields={}
        for name, value in attrs:
            fields[name]=value
        if fields.has_key('name'):
            if string.lower(fields['name']) == 'author':
                if fields.has_key('content'):
                    self.author = fields['content']

    # stylesheet links
    def do_link(self,attrs):
        for name, val in attrs:
            if name=="href":
                if val not in self.anchorlist:
                    self.anchorlist.append(val)

    # <AREA> for client-side image maps
    def do_area(self,attrs):
        for name, val in attrs:
            if name=="href":
                if val not in self.anchorlist:
                    self.anchorlist.append(val)

    def do_base(self,attrs):
        for name,val in attrs:
            if name=="href":
                self.base = val

def parse(content, link):
    """Parse the specified content and extract an url list, a list of images a
    title and an author. The content is assumed to contain HMTL."""
    # parse the file
    parser = _MyHTMLParser(formatter.NullFormatter())
    try:
        parser.feed(content)
        parser.close()
    except sgmllib.SGMLParseError, e:
        debugio.warn('problem parsing html: %s' % (str(e)))
        link.add_problem('problem parsing html: %s' % (str(e)))
    # flag that the link contains a valid page
    link.ispage = True
    # figure out a base url to use for creating absolute urls
    base = link.url
    if parser.base is not None:
        base = parser.base
    # save the title
    if parser.title is not None:
        link.title = parser.title
    # save the author
    if parser.author is not None:
        link.author = parser.author
    # if the link is external we are not interested in the rest
    if not link.isinternal:
        return
    # save the list of children (make links absolute)
    for anchor in parser.anchorlist:
        link.add_child(urlparse.urljoin(base,anchor))
    # save list of images (make links absolute)
    for image in parser.imagelist:
        # create absolute url based on <base> tag
        link.add_embed(urlparse.urljoin(base,image))