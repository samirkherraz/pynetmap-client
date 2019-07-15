#!/usr/bin/env python
__author__ = 'Samir KHERRAZ'
__copyright__ = '(c) Samir HERRAZ 2018-2019'
__version__ = '1.2.0'
__licence__ = 'GPLv3'
from gi.repository import Gtk, Gdk, GLib



try:
    import notify2
    notify2.init("PyNetMAP")
except:
    pass


class GtkNotify:
    def __init__(self, title, message):
        try:
            notify2.Notification(title,
                                 message,
                                 "/usr/share/pynetmap/icon.png"
                                 ).show()
        except:
            pass
