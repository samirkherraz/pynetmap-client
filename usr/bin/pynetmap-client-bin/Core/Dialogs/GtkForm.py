#!/usr/bin/env python
__author__ = 'Samir KHERRAZ'
__copyright__ = '(c) Samir HERRAZ 2018-2019'
__version__ = '1.3.0'
__licence__ = 'GPLv3'
from gi.repository import Gtk, Gdk, GLib
from Constants import *
from Core.Libs.Api import Api
from Core.Libs.Lang import Lang


class GtkForm(Gtk.Dialog):

    def prepare(self):
        self._sfields = [KEY_TYPE, "parent"]
        self._fields = dict()
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.set_default_size(800, 500)

    def build(self, template=None):
        self._fields[KEY_TYPE] = Gtk.ComboBoxText()
        for key in Api.getInstance().get(DB_SCHEMA):
            self._fields[KEY_TYPE].append_text(key)
        self._fields[KEY_TYPE].connect('changed', self.on_changed)

        toolbar = Gtk.HBox( margin=12)
        toolbar.add(self._fields[KEY_TYPE])
        self.root = Gtk.VBox(expand=True, spacing=12, margin=12)
        self.get_content_area().add(toolbar)
        swin = Gtk.ScrolledWindow()
        swin.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        swin.add_with_viewport(self.root)
        self.get_content_area().add(swin)
        self._fields[KEY_TYPE].set_active(0)
    def set_parent(self, value):
        try:
            self._fields["parent"].set_active_id(value)
        except:
            pass

    def get_parent(self):
        try:
            return self._fields["parent"].get_active_id()
        except:
            pass

    def get_fields(self):
        ret = dict()
        for d in self._fields:
            ret[d] = self.get_field(d)
        return ret

    def set_field(self, id, value):
        try:
            if type(self._fields[id]) is Gtk.Entry:
                self._fields[id].set_text(value)
            elif type(self._fields[id]) is Gtk.TextBuffer:
                self._fields[id].set_text(value, len(value))
            elif type(self._fields[id]) is Gtk.ComboBoxText:
                i = 0
                self._fields[id].set_active(i)
                while self._fields[id].get_active_text() != value and self._fields[id].get_active_text() != None:
                    self._fields[id].set_active(i)
                    i += 1
        except:
            pass

    def get_field(self, id):
        try:
            if type(self._fields[id]) is Gtk.Entry:
                ret = self._fields[id].get_text()
            elif type(self._fields[id]) is Gtk.TextBuffer:
                start_iter = self._fields[id].get_start_iter()
                end_iter = self._fields[id].get_end_iter()
                ret = self._fields[id].get_text(
                    start_iter, end_iter, True)
            elif type(self._fields[id]) is Gtk.ComboBoxText:
                ret = self._fields[id].get_active_text()
            elif type(self._fields[id]) is Gtk.CheckButton:
                ret = self._fields[id].get_active()

            return ret
        except:
            return None

    def set_fields(self, data):
        self.set_field(KEY_TYPE, data[KEY_TYPE])
        for d in data:
            if d not in self._sfields and data[d] != None:
                self.set_field(d, data[d])

    def cleanup_fields(self):
        li = self._fields.keys()
        for d in list(li):
            if d not in self._sfields:
                del self._fields[d]

    def form(self, template):
        self.cleanup_fields()
        if template != None:
            self.root.forall(self.root.remove)
            self.grid = Gtk.Table(len(template["Fields"])+1, 2, False)
            self.grid.set_row_spacings(12)
            i = 0
            elms = Api.getInstance().find(DB_BASE,
                template["Parents"], "type") if template["Parents"] != None else []
            if len(elms) > 0:
                self._has_parent = True
                self._fields["parent"] = Gtk.ComboBoxText()
                base = Api.getInstance().get(DB_BASE)
                for el in elms:
                    self._fields["parent"].append(
                        el, base[el][KEY_NAME])
                self._fields["parent"].set_active(0)

                if template["Build"] == "MANUAL":
                    label = Gtk.Label(
                        Lang.getInstance().get("Gtk.field.parent"))
                    label.set_alignment(0, 0.5)
                    self.grid.attach(label, 0, 1, 0, 1)
                    self.grid.attach(self._fields["parent"], 1, 2, i, i+1)
                    i += 1
            else:
                self._has_parent = False

            keylist = list(template["Fields"].keys())
            keylist.sort()
            for key in keylist:
                label = Gtk.Label(Lang.getInstance().get(key))
                label.set_alignment(0, 0.5)
                self.grid.attach(label, 0, 1, i, i+1)
                if template["Fields"][key] == "LONG":
                    textview = Gtk.TextView()
                    textview.set_left_margin(5)
                    scrolledwindow = Gtk.ScrolledWindow()
                    scrolledwindow.set_policy(
                        Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
                    scrolledwindow.add_with_viewport(textview)
                    scrolledwindow.set_size_request(-1, 150)
                    self.grid.attach(scrolledwindow, 1, 2, i, i+1)
                    self._fields[key] = textview.get_buffer()
                elif template["Fields"][key] == "SHORT":
                    self._fields[key] = Gtk.Entry()
                    self.grid.attach(self._fields[key], 1, 2, i, i+1)
                elif type(template["Fields"][key]) is list:
                    self._fields[key] = Gtk.ComboBoxText()
                    for lk in template["Fields"][key]:
                        self._fields[key].append_text(lk)
                    self.grid.attach(self._fields[key], 1, 2, i, i+1)

                i += 1
            self.root.pack_start(self.grid, False, False, 0)
            self.show_all()

    def on_changed(self, widget):
        active = self._fields[KEY_TYPE].get_active_text()
        self.form(Api.getInstance().get(DB_SCHEMA, active))

    def __init__(self, name, parent):
        Gtk.Dialog.__init__(self, name, parent, flags=Gtk.DialogFlags.MODAL,
                            buttons=(Gtk.STOCK_OK, Gtk.ResponseType.OK,
                                     Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
        self.prepare()
        self.build()
