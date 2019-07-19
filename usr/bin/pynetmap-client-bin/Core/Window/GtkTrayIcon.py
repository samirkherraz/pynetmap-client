#!/usr/bin/env python
__author__ = 'Samir KHERRAZ'
__copyright__ = '(c) Samir HERRAZ 2018-2019'
__version__ = '1.2.0'
__licence__ = 'GPLv3'

from gi.repository import Gtk, GdkPixbuf

class GtkTrayIcon(Gtk.StatusIcon):
    def __init__(self, main):
        self.main = main
        Gtk.StatusIcon.__init__(self)
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size("/usr/share/pynetmap/icon.png",48,48)
        self.set_from_pixbuf(pixbuf)
        self.set_visible(True)

        self.menu = Gtk.Menu()

        reload_item = Gtk.MenuItem("Reload")
        reload_item.connect("activate", self.main.event.on_refresh)
        self.menu.append(reload_item)

        window_item = Gtk.MenuItem("Show Window")
        window_item.connect("activate", self.main.event.on_show_window)
        self.menu.append(window_item)

        quit_item = Gtk.MenuItem("Quit")
        quit_item.connect("activate", self.main.event.on_quit)
        self.menu.append(quit_item)


        self.connect("activate", self.main.event.on_show_window)
        self.connect('popup-menu', self.main.event.on_icon_clicked)

