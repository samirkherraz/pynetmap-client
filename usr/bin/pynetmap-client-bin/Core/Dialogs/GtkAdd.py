#!/usr/bin/env python
__author__ = 'Samir KHERRAZ'
__copyright__ = '(c) Samir HERRAZ 2018-2019'
__version__ = '1.3.0'
__licence__ = 'GPLv3'
from gi.repository import Gtk, Gdk, GLib
from Core.Dialogs.GtkForm import GtkForm
from Core.Libs.Api import Api
from Core.Libs.Lang import Lang
from Constants import *


class GtkAdd(GtkForm):
    def __init__(self, parent):
        GtkForm.__init__(self, Lang.getInstance().get("gtk.add.title"), parent)
        self.show_all()
        result = self.run()
        if result == Gtk.ResponseType.OK:
            if self._has_parent:
                newid = Api.getInstance().create(self.get_parent())
            else:
                newid = Api.getInstance().create()
            Api.getInstance().set(DB_BASE, newid, data=self.get_fields())

        self.destroy()
