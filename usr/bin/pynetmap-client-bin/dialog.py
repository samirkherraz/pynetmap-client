#!/usr/bin/env python
__author__ = 'Samir KHERRAZ'
__copyright__ = '(c) Samir HERRAZ 2018-2018'
__version__ = '1.1.0'
__licence__ = 'GPLv3'

import gobject
import gtk
import notify2

from const import *

try:
    notify2.init("PyNetMAP")
except:
    pass


class Config(gtk.Dialog):
    def prepare(self):
        self._fields = dict()
        self.set_title("Configuration")
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_default_size(600, 400)

    def build(self, keylist):
        self.container = gtk.VBox()
        swin = gtk.ScrolledWindow()
        swin.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        swin.add_with_viewport(self.container)
        self.vbox.add(swin)
        self.grid = gtk.Table(len(keylist)+1, 2, False)
        i = 0
        self._fields = dict()
        for (key, _) in keylist:
            label = gtk.Label(self.ui.lang.get(key))
            label.set_alignment(0, 0.5)
            self.grid.attach(label, 0, 1, i, i+1)
            self._fields[key] = gtk.Entry()
            self.grid.attach(self._fields[key], 1, 2, i, i+1)
            i += 1
        self.container.pack_start(self.grid, False, False, 0)
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
        gtk.Dialog.__init__(self, "Configuration", None, flags=gtk.DIALOG_MODAL,
                            buttons=(gtk.STOCK_OK, gtk.RESPONSE_OK,
                                     gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
        self.ui = ui
        self.prepare()
        self.build(self.ui.config.configuration.items("GLOBAL"))
        self.show_all()


class Form(gtk.Dialog):

    def prepare(self):
        self._sfields = [KEY_TYPE, "parent"]
        self._fields = dict()
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_default_size(600, 400)

    def build(self, template=None):
        self._fields[KEY_TYPE] = gtk.ComboBox()
        cell = gtk.CellRendererText()
        self._fields[KEY_TYPE].pack_start(cell)
        self._fields[KEY_TYPE].add_attribute(cell, 'text', 0)

        store = gtk.ListStore(gobject.TYPE_STRING)
        for key in self.ui.store.get_table("schema"):
            store.append([key])
        self._fields[KEY_TYPE].set_model(store)
        self._fields[KEY_TYPE].connect('changed', self.on_changed)

        toolbar = gtk.HBox()
        toolbar.add(self._fields[KEY_TYPE])
        self.container = gtk.VBox()
        self.vbox.pack_start(toolbar, False, True, 0)
        swin = gtk.ScrolledWindow()
        swin.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        swin.add_with_viewport(self.container)
        self.vbox.add(swin)
        self._fields[KEY_TYPE].set_active(0)

    def get_fields(self):
        ret = dict()
        for d in self._fields:
            # if d.startswith(""):
            ret[d] = self.get_field(d)
        return ret

    def set_field(self, id, value):
        try:
            if type(self._fields[id]) is gtk.Entry:
                self._fields[id].set_text(value)
            elif type(self._fields[id]) is gtk.TextBuffer:
                self._fields[id].set_text(value, len(value))
            elif type(self._fields[id]) is gtk.ComboBox:
                i = 0
                self._fields[id].set_active(i)
                while self._fields[id].get_active_text() != value and self._fields[id].get_active_text() != None:
                    self._fields[id].set_active(i)
                    i += 1
        except:
            pass

    def get_field(self, id):
        try:
            if type(self._fields[id]) is gtk.Entry:
                ret = self._fields[id].get_text()
            elif type(self._fields[id]) is gtk.TextBuffer:
                start_iter = self._fields[id].get_start_iter()
                end_iter = self._fields[id].get_end_iter()
                ret = self._fields[id].get_text(
                    start_iter, end_iter, True)
            elif type(self._fields[id]) is gtk.ComboBox:
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
        for d in self._fields.keys():
            if d not in self._sfields:
                del self._fields[d]

    def form(self, template):
        self.cleanup_fields()
        if template != None:
            self.container.forall(self.container.remove)
            self.grid = gtk.Table(len(template["Fields"])+1, 2, False)
            i = 0
            elms = self.ui.store.find_by_schema(
                template["Parents"]) if template["Parents"] != None else []
            if len(elms) > 0:
                self._has_parent = True
                self._fields["parent"] = gtk.ComboBox()
                store = gtk.ListStore(str, str)
                cell = gtk.CellRendererText()
                self._fields["parent"].pack_start(cell)
                self._fields["parent"].add_attribute(cell, 'text', 1)
                for el in elms:
                    store.append(
                        [el, self.ui.store.get_attr("base", el, KEY_NAME)])
                self._fields["parent"].set_model(store)
                self._fields["parent"].set_active(0)

                if template["Build"] == "MANUAL":
                    label = gtk.Label(self.ui.lang.get("gtk.field.parent"))
                    label.set_alignment(0, 0.5)
                    self.grid.attach(label, 0, 1, 0, 1)
                    self.grid.attach(self._fields["parent"], 1, 2, i, i+1)
                    i += 1
            else:
                self._has_parent = False

            keylist = template["Fields"].keys()
            keylist.sort()
            for key in keylist:
                label = gtk.Label(self.ui.lang.get(key))
                label.set_alignment(0, 0.5)
                self.grid.attach(label, 0, 1, i, i+1)
                if template["Fields"][key] == "LONG":
                    textview = gtk.TextView()
                    textview.set_left_margin(5)
                    scrolledwindow = gtk.ScrolledWindow()
                    scrolledwindow.set_policy(
                        gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
                    scrolledwindow.add_with_viewport(textview)
                    scrolledwindow.set_size_request(-1, 150)
                    self.grid.attach(scrolledwindow, 1, 2, i, i+1)
                    self._fields[key] = textview.get_buffer()
                elif template["Fields"][key] == "SHORT":
                    self._fields[key] = gtk.Entry()
                    self.grid.attach(self._fields[key], 1, 2, i, i+1)
                elif type(template["Fields"][key]) is list:
                    self._fields[key] = gtk.ComboBox()
                    cell = gtk.CellRendererText()
                    self._fields[key].pack_start(cell)
                    self._fields[key].add_attribute(cell, 'text', 0)
                    store = gtk.ListStore(gobject.TYPE_STRING)
                    for lk in template["Fields"][key]:
                        store.append([lk])
                    self._fields[key].set_model(store)
                    self.grid.attach(self._fields[key], 1, 2, i, i+1)

                i += 1
            self.container.pack_start(self.grid, False, False, 0)
            self.show_all()

    def on_changed(self, widget):
        self.form(self.ui.store.get("schema", widget.get_active_text()))

    def __init__(self, name, parent):
        gtk.Dialog.__init__(self, name, parent, flags=gtk.DIALOG_MODAL,
                            buttons=(gtk.STOCK_OK, gtk.RESPONSE_OK,
                                     gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
        self.ui = parent
        self.prepare()
        self.build()


class Edit(Form):
    def __init__(self, parent):
        Form.__init__(self, parent.lang.get(
            "gtk.edit.dialog.title"), parent)
        if len(self.ui.selection) > 0:
            self._fields[KEY_TYPE].set_sensitive(False)
            self.set_fields(self.ui.store.get("base", self.ui.selection[0]))
            if len(self.ui.selection) > 1:
                self.set_field("parent", self.ui.selection[1])
            self.show_all()
            result = self.run()
            if result == gtk.RESPONSE_OK:
                for key in self.get_fields():
                    self.ui.store.set_attr(
                        "base", self.ui.selection[0], key, self.get_field(key))
                if len(self.ui.selection) > 1 and self.ui.selection[1] != self.get_field("parent"):
                    self.ui.store.move(
                        self.ui.selection[0], self.get_field("parent"))

        self.destroy()


class Add(Form):
    def __init__(self, parent):
        Form.__init__(self, parent.lang.get(
            "gtk.add.dialog.title"), parent)
        self.show_all()
        result = self.run()
        if result == gtk.RESPONSE_OK:
            if self._has_parent:
                newid = self.ui.store.create(self.get_field("parent"))
            else:
                newid = self.ui.store.create()
            self.ui.store.set(
                "base", newid, self.get_fields())

        self.destroy()


class Ask(gtk.Dialog):

    def getResponse(self):
        return self.response

    def is_ok(self):
        return self.status

    def __init__(self, parent, title, message, visibility=True):
        self.status = False
        gtk.Dialog.__init__(self, title, parent, flags=gtk.DIALOG_MODAL,
                            buttons=(gtk.STOCK_OK, gtk.RESPONSE_OK,
                                     gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
        self.set_default_size(300, 200)
        self.set_position(gtk.WIN_POS_CENTER)
        self.vbox.add(gtk.Label(message))
        field = gtk.Entry()
        field.set_visibility(visibility)
        field.connect("activate",
                      lambda ent, dlg, resp:
                          dlg.response(resp),
                          self,
                          gtk.RESPONSE_OK)
        self.vbox.add(field)
        self.show_all()
        if self.run() == gtk.RESPONSE_OK:
            self.status = True
            self.response = field.get_text()
        self.destroy()


class AskConfirmation(gtk.MessageDialog):

    def __init__(self, parent, question):
        gtk.MessageDialog.__init__(self, parent,
                                   gtk.DIALOG_MODAL, gtk.MESSAGE_INFO,
                                   gtk.BUTTONS_YES_NO, question)
        self.result = self.run()
        self.destroy()

    def is_ok(self):
        return (self.result == gtk.RESPONSE_YES)


class Error(gtk.MessageDialog):
    def __init__(self, parent, msg):
        gtk.MessageDialog.__init__(self, parent,
                                   gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR,
                                   gtk.BUTTONS_CLOSE, msg)
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
