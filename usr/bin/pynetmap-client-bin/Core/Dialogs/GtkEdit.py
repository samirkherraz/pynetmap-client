#!/usr/bin/env python
__author__ = 'Samir KHERRAZ'
__copyright__ = '(c) Samir HERRAZ 2018-2019'
__version__ = '1.2.0'
__licence__ = 'GPLv3'
from gi.repository import Gtk, Gdk, GLib
from Core.Dialogs.GtkForm import GtkForm
from Core.Libs.Api import Api
from Core.Libs.Lang import Lang
from Constants import *


class GtkEdit(GtkForm):
    def __init__(self, parent, selection):
        GtkForm.__init__(self, Lang.getInstance().get(
            "Gtk.edit.title"), parent)
        if len(selection) > 0:
            self._fields[KEY_TYPE].set_sensitive(False)
            self.set_fields(Api.getInstance().get(
                DB_BASE, selection[0]))
            if len(selection) > 1:
                self.set_parent(selection[1])
            self.show_all()
            result = self.run()
            if result == Gtk.ResponseType.OK:
                for key in self.get_fields():
                    Api.getInstance().set(
                        DB_BASE, selection[0], key, data=self.get_field(key))
                if len(selection) > 1 and selection[1] != self.get_parent():
                    Api.getInstance().move(
                        selection[0], self.get_parent())

        self.destroy()
