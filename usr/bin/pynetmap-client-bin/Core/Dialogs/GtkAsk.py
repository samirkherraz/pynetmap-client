#!/usr/bin/env python
__author__ = 'Samir KHERRAZ'
__copyright__ = '(c) Samir HERRAZ 2018-2019'
__version__ = '1.2.0'
__licence__ = 'GPLv3'
from gi.repository import Gtk, Gdk, GLib

class GtkAsk(Gtk.Dialog):

    def getResponse(self):
        return self.response

    def is_ok(self):
        return self.status

    def __init__(self, parent, title, message, visibility=True):
        self.status = False
        Gtk.Dialog.__init__(self, title, parent, flags=Gtk.DialogFlags.MODAL,
                            buttons=(Gtk.STOCK_OK, Gtk.ResponseType.OK,
                                     Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
        self.set_default_size(300, 200)
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.vbox.add(Gtk.Label(message))
        field = Gtk.Entry()
        field.set_visibility(visibility)
        field.connect("activate",
                      lambda ent, dlg, resp:
                          dlg.response(resp),
                          self,
                          Gtk.ResponseType.OK)
        self.vbox.add(field)
        self.show_all()
        if self.run() == Gtk.ResponseType.OK:
            self.status = True
            self.response = field.get_text()
        self.destroy()
