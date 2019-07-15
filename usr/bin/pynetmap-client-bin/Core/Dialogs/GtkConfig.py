#!/usr/bin/env python
__author__ = 'Samir KHERRAZ'
__copyright__ = '(c) Samir HERRAZ 2018-2019'
__version__ = '1.2.0'
__licence__ = 'GPLv3'
from gi.repository import Gtk, Gdk, GLib
from Core.Config import Config
from Core.Lang import Lang
class GtkConfig(Gtk.Dialog):
    def prepare(self):
        self._fields = dict()
        self.set_title("Configuration")
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.set_default_size(600, 400)

    def build(self, keylist):
        self.root = Gtk.VBox(expand=True)
        swin = Gtk.ScrolledWindow()
        swin.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        swin.add_with_viewport(self.root)
        self.vbox.add(swin)
        self.grid = Gtk.Table(len(keylist)+1, 2, False)
        self.grid.set_row_spacings(12)
        i = 0
        self._fields = dict()
        for (key, _) in keylist:
            label = Gtk.Label(Lang.getInstance().get(key))
            label.set_alignment(0, 0.5)
            self.grid.attach(label, 0, 1, i, i+1)
            self._fields[key] = Gtk.Entry()
            self.grid.attach(self._fields[key], 1, 2, i, i+1)
            i += 1
        self.root.pack_start(self.grid, False, False, 0)
        self.show_all()

    def set_field(self, id, value):
        try:
            self._fields[id].set_text(value)
        except:
            pass
    

    def get_field(self, id):
        try:
            return self._fields[id].get_text()
        except:
            return None

    def __init__(self):
        Gtk.Dialog.__init__(self, "Configuration", None, flags=Gtk.DialogFlags.MODAL,
                            buttons=(Gtk.STOCK_OK, Gtk.ResponseType.OK,
                                     Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
        self.prepare()
        self.build(Config.getInstance().configuration.items("GLOBAL"))
        self.show_all()
