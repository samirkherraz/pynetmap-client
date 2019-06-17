#!/usr/bin/env python
__author__ = 'Samir KHERRAZ'
__copyright__ = '(c) Samir HERRAZ 2018-2018'
__version__ = '1.1.0'
__licence__ = 'GPLv3'
from gi.repository import Gtk, Gdk, GLib

#import notify2

from const import *

try:
    notify2.init("PyNetMAP")
except:
    pass


class Config(Gtk.Dialog):
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
            label = Gtk.Label(self.ui.lang.get(key))
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

    def __init__(self, ui):
        Gtk.Dialog.__init__(self, "Configuration", None, flags=Gtk.DialogFlags.MODAL,
                            buttons=(Gtk.STOCK_OK, Gtk.ResponseType.OK,
                                     Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
        self.ui = ui
        self.prepare()
        self.build(self.ui.config.configuration.items("GLOBAL"))
        self.show_all()


class Form(Gtk.Dialog):

    def prepare(self):
        self._sfields = [KEY_TYPE, "parent"]
        self._fields = dict()
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.set_default_size(600, 400)

    def build(self, template=None):
        self._fields[KEY_TYPE] = Gtk.ComboBoxText()
        for key in self.ui.store.get_table("schema"):
            self._fields[KEY_TYPE].append_text(key)
        self._fields[KEY_TYPE].connect('changed', self.on_changed)

        toolbar = Gtk.HBox()
        toolbar.add(self._fields[KEY_TYPE])
        self.root = Gtk.VBox(expand=True, spacing=12)
        self.vbox.pack_start(toolbar, False, True, 0)
        swin = Gtk.ScrolledWindow()
        swin.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        swin.add_with_viewport(self.root)
        self.vbox.pack_end(swin, False, True, 0)
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
            elif type(self._fields[id]) is Gtk.ComboBox:
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
            elms = self.ui.store.find_by_schema(
                template["Parents"]) if template["Parents"] != None else []
            if len(elms) > 0:
                self._has_parent = True
                self._fields["parent"] = Gtk.ComboBoxText()
                for el in elms:
                    self._fields["parent"].append(el ,self.ui.store.get_attr("base", el, KEY_NAME))
                self._fields["parent"].set_active(0)

                if template["Build"] == "MANUAL":
                    label = Gtk.Label(self.ui.lang.get("Gtk.field.parent"))
                    label.set_alignment(0, 0.5)
                    self.grid.attach(label, 0, 1, 0, 1)
                    self.grid.attach(self._fields["parent"], 1, 2, i, i+1)
                    i += 1
            else:
                self._has_parent = False

            keylist = list(template["Fields"].keys())
            keylist.sort()
            for key in keylist:
                label = Gtk.Label(self.ui.lang.get(key))
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
        self.form(self.ui.store.get("schema", active ))

    def __init__(self, name, parent):
        Gtk.Dialog.__init__(self, name, parent, flags=Gtk.DialogFlags.MODAL,
                            buttons=(Gtk.STOCK_OK, Gtk.ResponseType.OK,
                                     Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
        self.ui = parent
        self.prepare()
        self.build()


class Edit(Form):
    def __init__(self, parent):
        Form.__init__(self, parent.lang.get(
            "Gtk.edit.dialog.title"), parent)
        if len(self.ui.selection) > 0:
            self._fields[KEY_TYPE].set_sensitive(False)
            self.set_fields(self.ui.store.get("base", self.ui.selection[0]))
            if len(self.ui.selection) > 1:
                self.set_parent(self.ui.selection[1])
            self.show_all()
            result = self.run()
            if result == Gtk.ResponseType.OK:
                for key in self.get_fields():
                    self.ui.store.set_attr(
                        "base", self.ui.selection[0], key, self.get_field(key))
                if len(self.ui.selection) > 1 and self.ui.selection[1] != self.get_parent():
                    self.ui.store.move(
                        self.ui.selection[0], self.get_parent())

        self.destroy()


class Add(Form):
    def __init__(self, parent):
        Form.__init__(self, parent.lang.get(
            "Gtk.add.dialog.title"), parent)
        self.show_all()
        result = self.run()
        if result == Gtk.ResponseType.OK:
            if self._has_parent:
                newid = self.ui.store.create(self.get_parent())
            else:
                newid = self.ui.store.create()
            self.ui.store.set(
                "base", newid, self.get_fields())

        self.destroy()


class Ask(Gtk.Dialog):

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


class AskConfirmation(Gtk.MessageDialog):

    def __init__(self, parent, question):
        Gtk.MessageDialog.__init__(self, parent,
                                   Gtk.DialogFlags.MODAL, Gtk.MessageType.INFO,
                                   Gtk.ButtonsType.YES_NO, question)
        self.result = self.run()
        self.destroy()

    def is_ok(self):
        return (self.result == Gtk.ResponseType.YES)


class Error(Gtk.MessageDialog):
    def __init__(self, parent, msg):
        Gtk.MessageDialog.__init__(self, parent,
                                   Gtk.DialogFlags.MODAL, Gtk.MessageType.ERROR,
                                   Gtk.ButtonsType.OK, msg)
        self.run()
        self.destroy()


class Notify:
    def __init__(self, title, message):
        try:
            notify2.Notification(title,
                                 message,
                                 "/usr/share/pynetmap/icon.png"
                                 ).show()
        except:
            pass
