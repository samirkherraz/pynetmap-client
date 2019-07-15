#!/usr/bin/env python
__author__ = 'Samir KHERRAZ'
__copyright__ = '(c) Samir HERRAZ 2018-2019'
__version__ = '1.2.0'
__licence__ = 'GPLv3'
from gi.repository import Gtk, Gdk, GLib

class GtkConfirmation(Gtk.MessageDialog):

    def __init__(self, parent, question):
        Gtk.MessageDialog.__init__(self, parent,
                                   Gtk.DialogFlags.MODAL, Gtk.MessageType.INFO,
                                   Gtk.ButtonsType.YES_NO, question)
        self.result = self.run()
        self.destroy()

    def is_ok(self):
        return (self.result == Gtk.ResponseType.YES)
