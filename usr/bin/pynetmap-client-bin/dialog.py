#!/usr/bin/python
import gtk
import gobject
import notify2
notify2.init("PyNetMAP")


class Form(gtk.Dialog):

    def prepare(self):
        self._fields = dict()
        self.set_title("Add / Edit")
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_default_size(600, 400)

    def build(self, template=None):
        self._schema = gtk.ComboBox()
        cell = gtk.CellRendererText()
        self._schema.pack_start(cell)
        self._schema.add_attribute(cell, 'text', 0)

        store = gtk.ListStore(gobject.TYPE_STRING)
        for key in self.store.schema():
            store.append([key])
        self._schema.set_model(store)
        self._schema.connect('changed', self.on_changed)

        toolbar = gtk.HBox()
        toolbar.add(self._schema)
        self.container = gtk.VBox()
        self.vbox.pack_start(toolbar, False, True, 0)
        swin = gtk.ScrolledWindow()
        swin.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        swin.add_with_viewport(self.container)
        self.vbox.add(swin)
        self._schema.set_active(0)

    def getParent(self):
        if self._has_parent:
            return self._parent.get_active_text()
        else:
            return None

    def getschema(self):
        return self._schema.get_active_text()

    def setschema(self, schema):
        i = 0
        while self._schema.get_active_text() != schema and self._schema.get_active_text() != None:
            self._schema.set_active(i)
            i += 1

    def getID(self):
        return self._id.get_text()

    def setID(self, id):
        return self._id.set_text(id)

    def getFields(self):
        ret = dict()
        ret["__SCHEMA__"] = self.getschema()
        ret["__ID__"] = self.getID()
        for d in self._fields:
            if type(self._fields[d]) is gtk.Entry:
                ret[d] = self._fields[d].get_text()
            elif type(self._fields[d]) is gtk.TextBuffer:
                start_iter = self._fields[d].get_start_iter()
                end_iter = self._fields[d].get_end_iter()
                ret[d] = self._fields[d].get_text(start_iter, end_iter, True)
        return ret

    def setParent(self, parent):
        i = 0
        while self._parent.get_active_text() != parent and self._parent.get_active_text() != None:
            self._parent.set_active(i)
            i += 1

    def setFields(self, data):
        self.setschema(data["__SCHEMA__"])
        self.setID(data["__ID__"])
        for d in data:
            if not d.startswith("__") and data[d] != None:
                try:
                    if type(self._fields[d]) is gtk.Entry:
                        self._fields[d].set_text(data[d])
                    elif type(self._fields[d]) is gtk.TextBuffer:
                        self._fields[d].set_text(data[d], len(data[d]))
                except:
                    pass

    def form(self, template):
        if template != None:
            self.container.forall(self.container.remove)
            self.grid = gtk.Table(len(template["Fields"])+1, 2, False)
            elms = self.store.find_by_schema(template["Parents"])
            i = 0
            if len(elms) > 0:
                self._has_parent = True
                self._parent = gtk.ComboBox()
                store = gtk.ListStore(str, str)
                cell = gtk.CellRendererText()
                self._parent.pack_start(cell)
                self._parent.add_attribute(cell, 'text', 1)
                for el in elms:
                    store.append([el, elms[el]["__ID__"]])
                self._parent.set_model(store)
                self._parent.set_active(0)

                if template["Build"] == "MANUAL":
                    label = gtk.Label("Parent")
                    label.set_alignment(0.1, 0.5)
                    self.grid.attach(label, 0, 1, 0, 1)
                    self.grid.attach(self._parent, 1, 2, i, i+1)
                    i += 1
            else:
                self._has_parent = False

            self._id = gtk.Entry()
            if "__ID__" in template["Fields"]:
                label = gtk.Label("Nom")
                label.set_alignment(0.1, 0.5)
                self.grid.attach(label, 0, 1, i, i+1)
                self.grid.attach(self._id, 1, 2, i, i+1)
                i += 1

            self._fields = dict()
            keylist = template["Fields"].keys()
            keylist.sort()
            for key in keylist:
                if key.startswith("__"):
                    continue
                label = gtk.Label(key)
                label.set_alignment(0.1, 0.5)
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
                else:
                    self._fields[key] = gtk.Entry()
                    self.grid.attach(self._fields[key], 1, 2, i, i+1)

                i += 1
            self.container.pack_start(self.grid, False, False, 0)
            self.show_all()

    def on_changed(self, widget):
        self.form(self.store.schema()[
            widget.get_active_text()])

    def __init__(self, name, parent, database):
        gtk.Dialog.__init__(self, name, parent, flags=gtk.DIALOG_MODAL,
                            buttons=(gtk.STOCK_OK, gtk.RESPONSE_OK,
                                     gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
        self.store = database
        self.prepare()
        self.build()
        self.show_all()


class Edit(Form):
    def __init__(self, parent, database):
        Form.__init__(self, "Edit", parent, database)
        self._schema.set_sensitive(False)


class Add(Form):
    def __init__(self, parent, database):
        Form.__init__(self, "Add", parent, database)


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
        notify2.Notification(title,
                             message,
                             "/usr/share/pynetmap/icon.png"
                             ).show()
