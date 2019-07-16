#!/usr/bin/env python
__author__ = 'Samir KHERRAZ'
__copyright__ = '(c) Samir HERRAZ 2018-2019'
__version__ = '1.3.0'
__licence__ = 'GPLv3'
from gi.repository import Gtk, Gdk, GLib


class GtkError(Gtk.MessageDialog):
    def __init__(self, parent, msg):
        Gtk.MessageDialog.__init__(self, parent,
                                   Gtk.DialogFlags.MODAL, Gtk.MessageType.ERROR,
                                   Gtk.ButtonsType.OK, msg)
        self.run()
        self.destroy()