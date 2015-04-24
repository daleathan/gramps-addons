#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2013 Nick Hall
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# $Id: Participants.gpr.py 1899 2013-09-12 13:09:22Z vassilii $
#

#------------------------------------------------------------------------
#
# Register Gramplet
#
#------------------------------------------------------------------------
register(GRAMPLET,
         id="AddressPreview",
         name=_("AddressPreview"),
         description = _("Gramplet showing the address of the place"),
         version = '0.2.1',
         gramps_target_version="4.1",
         status = STABLE,
         fname="AddressPreview.py",
         height=200,
         gramplet = 'AddressPreview',
         gramplet_title=_("AddressPreview"),
         navtypes=["Place"],
         )
