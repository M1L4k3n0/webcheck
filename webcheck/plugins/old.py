
# old.py - plugin to list old pages
#
# Copyright (C) 1998, 1999 Albert Hopkins (marduk)
# Copyright (C) 2002 Mike W. Meyer
# Copyright (C) 2005, 2006, 2011 Arthur de Jong
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
#
# The files produced as output from the software do not automatically fall
# under the copyright of the software, unless explicitly stated otherwise.

"""Present a list of potentially outdated pages."""

__title__ = "what's old"
__author__ = 'Arthur de Jong'
__outputfile__ = 'old.html'

import time

from webcheck.db import Session, Link
from webcheck import config
import webcheck.plugins


SECS_PER_DAY = 60 * 60 * 24


def generate(site):
    """Output the list of outdated pages to the specified file descriptor."""
    session = Session()
    # the time for which links are considered old
    oldtime = time.time() - SECS_PER_DAY * config.REPORT_WHATSOLD_URL_AGE
    # get all internal pages that are old
    links = session.query(Link).filter_by(is_page=True, is_internal=True)
    links = links.filter(Link.mtime < oldtime).order_by(Link.mtime)
    # present results
    fp = webcheck.plugins.open_html(webcheck.plugins.old, site)
    if not links.count():
        fp.write(
          '   <p class="description">\n'
          '    No pages were found that were older than %(old)d days old.\n'
          '   </p>\n'
          % {'old': config.REPORT_WHATSOLD_URL_AGE})
        webcheck.plugins.close_html(fp)
        return
    fp.write(
      '   <p class="description">\n'
      '    These pages have been modified a long time ago (older than %(old)d\n'
      '    days) and may be outdated.\n'
      '   </p>\n'
      '   <ul>\n'
      % {'old': config.REPORT_WHATSOLD_URL_AGE})
    for link in links:
        age = (time.time() - link.mtime) / SECS_PER_DAY
        fp.write(
          '    <li>\n'
          '     %(link)s\n'
          '     <ul class="problems">\n'
          '      <li>age: %(age)d days</li>\n'
          '     </ul>\n'
          '    </li>\n'
          % {'link': webcheck.plugins.make_link(link),
             'age':  age})
    fp.write(
      '   </ul>\n')
    webcheck.plugins.close_html(fp)
