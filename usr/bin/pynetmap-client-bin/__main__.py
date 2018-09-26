#!/usr/bin/env python
__author__ = 'Samir KHERRAZ'
__copyright__ = '(c) Samir HERRAZ 2018-2018'
__version__ = '1.1.0'
__licence__ = 'GPLv3'

import os
import gobject
gobject.threads_init()
import gtk
gtk.gdk.threads_init()
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)
import time
from threading import Lock, Event, Thread
from database import Database
from dialog import Edit, Add, Ask, AskConfirmation, Error, Notify
from graph import Graph
from terminal import Terminal
from api import API
from export import Export
from const import NAME, VERSION
from configstore import ConfigStore
from langstore import LangStore
""" ameliorer search"""


class Boot(gtk.Window):

    def prepare(self):
        self.gtk_threading_lock = Lock()
        self.graph = Graph(self)
        self.selection = []
        self.cstx = 0
        self.csty = 0
        self.x = 0
        self.y = 0
        self.ly = 0
        self.lx = 0
        self.mousedown = False
        self.scale = 1
        self.current_doc = None
        self.set_title(NAME + " - " + VERSION)
        self.set_default_size(1000, 600)
        self.set_position(gtk.WIN_POS_CENTER)
        self.connect("delete_event", gtk.main_quit)
        self.connect("key-press-event", self.on_key_release)
        self.status_icons = dict()
        self.status_icons["alert.memory"] = self.render_icon(
            gtk.STOCK_DIALOG_INFO, 1)
        self.status_icons["alert.disk"] = self.render_icon(
            gtk.STOCK_HARDDISK, 1)
        self.status_icons["alert.mounts"] = self.render_icon(
            gtk.STOCK_HARDDISK, 1)
        self.status_icons["alert.cpu"] = self.render_icon(gtk.STOCK_EXECUTE, 1)
        self.status_icons["alert.required_fields"] = self.render_icon(
            gtk.STOCK_EDIT, 1)

        self.status_icons["alert.tunnel"] = self.render_icon(
            gtk.STOCK_NETWORK, 1)

        self.status_icons["alert.status"] = self.render_icon(gtk.STOCK_STOP, 1)
        self.status_icons["alert.none"] = self.render_icon("", 1)

    def server_refresh(self):
        while not self._stop.isSet():
            try:
                if not self.api.auth_check():
                    Notify(self.ui.lang.get("gtk.notify.connection.lost.title"),
                           self.ui.lang.get("gtk.notify.connection.lost.text"))
                    self.api.auth()
                    raise Exception("AUTH")

                self.store.refresh()
                self.check_alerts()

            except:
                pass
            self._stop.wait(int(self.config.get("refresh")))

    def open_terminal(self, _=None):

        if self.api.get_access("users.privilege.terminal"):
            if len(self.selection) > 0:
                self.terminalbox.external(self.selection[0])

    def open_internal_terminal(self, e=None):
        if self.api.get_access("users.privilege.terminal"):
            self.terminal.forall(self.terminal.remove)
            term = self.terminalbox.internal(self.selection[0], e != None)
            if term != None:
                self.terminal.add(term)
            else:
                img = gtk.Image()
                img.set_from_pixbuf(self.render_icon(
                    gtk.STOCK_DIALOG_AUTHENTICATION, 6))
                self.terminal.add(img)
            self.terminal.show_all()

    def build(self):
        self.dashStore = gtk.ListStore(str, gtk.gdk.Pixbuf, str, str)
        self.dash = gtk.TreeView(self.dashStore)
        self.dash.set_grid_lines(True)
        self.dash.set_headers_visible(False)
        self.dash.set_model(self.dashStore)
        self.dash.set_enable_search(False)
        self.dash.get_selection().set_mode(gtk.SELECTION_NONE)

        tvcolumn = gtk.TreeViewColumn()
        self.dash.append_column(tvcolumn)
        cell = gtk.CellRendererText()
        cell.set_padding(0, 10)
        tvcolumn.pack_start(cell, True)
        tvcolumn.add_attribute(cell, "background", 0)

        tvcolumn = gtk.TreeViewColumn()
        self.dash.append_column(tvcolumn)
        cell = gtk.CellRendererPixbuf()
        cell.set_padding(0, 10)
        tvcolumn.pack_start(cell, True)
        tvcolumn.add_attribute(cell, 'pixbuf', 1)

        tvcolumn = gtk.TreeViewColumn()
        self.dash.append_column(tvcolumn)
        cell = gtk.CellRendererText()
        cell.set_padding(0, 10)
        tvcolumn.pack_start(cell, True)
        tvcolumn.add_attribute(cell, 'text', 2)

        tvcolumn = gtk.TreeViewColumn()
        self.dash.append_column(tvcolumn)
        cell = gtk.CellRendererText()
        cell.set_padding(0, 10)
        tvcolumn.pack_start(cell, True)
        tvcolumn.add_attribute(cell, 'text', 3)

        self.canvas = gtk.DrawingArea()
        self.canvas.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color("#ffffff"))
        self.canvas.connect("expose-event", self.draw_image)
        self.canvas.set_events(gtk.gdk.EXPOSURE_MASK
                               | gtk.gdk.LEAVE_NOTIFY_MASK
                               | gtk.gdk.BUTTON_PRESS_MASK
                               | gtk.gdk.POINTER_MOTION_MASK
                               | gtk.gdk.POINTER_MOTION_HINT_MASK
                               | gtk.gdk.BUTTON_RELEASE_MASK
                               )
        self.canvas.connect("motion_notify_event", self.drag)
        self.canvas.connect("button_press_event", self.mouse_on)
        self.canvas.connect("button_release_event", self.mouse_off)
        self.canvas.connect('scroll-event', self.scroll)

        self.treeStore = gtk.TreeStore(str, str, gtk.gdk.Pixbuf)
        self.tree = gtk.TreeView(self.treeStore)
        self.tree.set_model(self.treeStore)
        self.tree.set_enable_search(False)
        self.tree.connect("cursor-changed", self.selection_changed)

        tvcolumn = gtk.TreeViewColumn(self.lang.get("gtk.tree.name"))
        self.tree.append_column(tvcolumn)
        cell = gtk.CellRendererText()
        tvcolumn.pack_start(cell, True)
        tvcolumn.add_attribute(cell, 'text', 1)

        tvcolumn = gtk.TreeViewColumn(self.lang.get("gtk.tree.state"))
        self.tree.append_column(tvcolumn)
        cell = gtk.CellRendererPixbuf()
        tvcolumn.pack_start(cell, True)
        tvcolumn.add_attribute(cell, 'pixbuf', 2)
        toolbar = gtk.Toolbar()
        toolbar.set_style(gtk.TOOLBAR_ICONS)
        vBox = gtk.VBox(False, 2)
        toolbar_n = 0
        if self.api.get_access("users.privilege.edit"):
            newtb = gtk.ToolButton(gtk.STOCK_NEW)
            newtb.connect("clicked", self.new_entry)
            toolbar.insert(newtb, toolbar_n)
            toolbar_n += 1

            newtb = gtk.ToolButton(gtk.STOCK_EDIT)
            newtb.connect("clicked", self.edit_entry)
            toolbar.insert(newtb, 1)
            toolbar_n += 1

            newtb = gtk.ToolButton(gtk.STOCK_DELETE)
            newtb.connect("clicked", self.delete_entry)
            toolbar.insert(newtb, toolbar_n)
            toolbar_n += 1

        if self.api.get_access("users.privilege.terminal"):
            newtb = gtk.ToolButton(gtk.STOCK_MEDIA_PLAY)
            newtb.connect("clicked", self.open_terminal)
            toolbar.insert(newtb, toolbar_n)
            toolbar_n += 1

        newtb = gtk.ToolButton(gtk.STOCK_FIND)
        newtb.connect("clicked", self.search)
        toolbar.insert(newtb, toolbar_n)
        toolbar_n += 1

        newtb = gtk.ToolButton(gtk.STOCK_SAVE)
        newtb.connect("clicked", self.export)
        toolbar.insert(newtb, toolbar_n)
        toolbar_n += 1

        newtb = gtk.ToolButton(gtk.STOCK_REFRESH)
        newtb.connect("clicked", self.open_internal_terminal)
        toolbar.insert(newtb, toolbar_n)
        toolbar_n += 1

        newtb = gtk.ToolButton(gtk.STOCK_PROPERTIES)
        newtb.connect("clicked", self.edit_config)
        toolbar.insert(newtb, toolbar_n)
        toolbar_n += 1

        vBox.pack_start(toolbar, False, False, 0)
        hBox = gtk.HPaned()
        hBox.set_position(300)
        swin = gtk.ScrolledWindow()
        swin.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        swin.add_with_viewport(self.tree)
        vBoxLeft = gtk.VBox()
        vBoxLeft.add(swin)
        self.notebook = gtk.Notebook()
        self.notebook.connect("switch-page", self.page_change)
        self.notebook.append_page(self.canvas, gtk.Label(self.lang.get(
            "gtk.notebook.graph.title")))
        self.TAB_GRAPH = 0
        if self.api.get_access("users.privilege.terminal"):
            self.terminal = gtk.VBox()
            self.notebook.append_page(self.terminal, gtk.Label(self.lang.get(
                "gtk.notebook.terminal.title")))
            self.TAB_TERMINAL = 1
        else:
            self.TAB_TERMINAL = None

        swin = gtk.ScrolledWindow()
        swin.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        swin.add_with_viewport(self.dash)
        self.dashTitle = gtk.Label(self.lang.get(
            "gtk.notebook.dash.title").replace("$value", "0"))
        self.notebook.append_page(swin, self.dashTitle)
        self.TAB_ALERTS = 2
        hBox.add(vBoxLeft)
        hBox.add(self.notebook)
        vBox.add(hBox)
        self.add(vBox)

    def edit_config(self, _):
        self.config.check()
        self.api.reset()

    def search(self, elm):
        res = Ask(self, self.lang.get("gtk.search.dialog.title"),
                  self.lang.get("gtk.search.dialog.text"))
        if res.is_ok():
            keys = self.store.find_by_attr(res.getResponse())
            if len(keys) > 0:
                key = keys[0]
            else:
                return False
            if self.search_function(key, [0]):
                self.selection_changed(None)

    def search_function(self, key, path):

        while True:
            npath = ':'.join(str(x) for x in path)
            try:
                cur = self.tree.get_model().get_iter_from_string(npath)

                if key == self.treeStore.get_value(cur, 0):
                    self.tree.expand_all()
                    self.tree.get_selection().select_iter(cur)
                    return True
                else:
                    cpath = path[:]
                    cpath.append(0)
                    path[len(path)-1] += 1
                    if self.search_function(key, cpath):
                        return True
            except:
                break

        return False

    def new_entry(self, widget):
        Add(self)

    def edit_entry(self, widget):
        Edit(self)

    def reload(self, _):
        self.api.tunnel_relaod()

    def updateui(self):
        self.treeStore.clear()
        self.populate()
        self.tree.expand_all()
        if len(self.selection) > 0:
            if self.search_function(self.selection[0], [0]):
                self.selection_changed(None)

    def refresh(self):
        gobject.idle_add(self.updateui,
                         priority=gobject.PRIORITY_HIGH)

    def delete_entry(self, widget):
        r = AskConfirmation(self,  self.lang.get("gtk.delete.dialog.text") +
                            self.store.get_attr("base", self.selection[0], "base.name"))
        if r.is_ok():
            if len(self.selection) > 1:
                self.store.delete(self.selection[1], self.selection[0])
            else:
                self.store.delete(None, self.selection[0])

            self.treeStore.clear()
            self.populate()
            self.tree.expand_all()

    def drag(self, widget, elm):
        curtime = time.time()
        if self.mousedown and curtime > (self.lasttime + 0.025):
            self.lasttime = curtime
            x, y = widget.get_pointer()
            self.x = x/self.scale
            self.y = y/self.scale
            gobject.idle_add(self.canvas.queue_draw,
                             priority=gobject.PRIORITY_HIGH)

    def mouse_on(self, widget, elm):
        if elm.button == 1:
            self.lasttime = 0
            x, y = widget.get_pointer()
            self.lx = x/self.scale - (self.x - self.lx)
            self.ly = y/self.scale - (self.y - self.ly)
            self.mousedown = True

    def mouse_off(self, widget, elm):
        if elm.button == 1:
            self.mousedown = False

    def scroll(self, widget, elm):
        if self.current_doc == None:
            return
        w = self.current_doc.get_width()
        h = self.current_doc.get_height()
        t = self.translate(w, h)
        x, y = widget.get_pointer()
        self.lx = x - (self.x - self.lx)
        self.ly = y - (self.y - self.ly)
        self.x = x
        self.y = y
        if elm.direction == gtk.gdk.SCROLL_UP and t["width"] < w*0.6:
            self.scale *= 1.12
        elif elm.direction == gtk.gdk.SCROLL_DOWN and self.scale > 1:
            self.scale /= 1.12
        else:
            return

        gobject.idle_add(self.canvas.queue_draw,
                         priority=gobject.PRIORITY_LOW)

    def translate(self, p_width, p_height):
        ret = {}
        w = self.canvas.allocation.width
        h = self.canvas.allocation.height
        scale_w = float(w)/float(p_width)
        scale_h = float(h)/float(p_height)
        ret["scale_w"] = (min(scale_h, scale_w)) * self.scale
        ret["scale_h"] = (min(scale_h, scale_w)) * self.scale
        ret["width"] = int(p_width*ret["scale_w"])
        ret["height"] = int(p_height*ret["scale_h"])
        ret["translate_x"] = int(w/2-ret["width"]/2)
        ret["translate_y"] = int(h/2-ret["height"]/2)
        ret["translate_x"] += int((self.x - self.lx) * self.scale)
        ret["translate_y"] += int((self.y - self.ly) * self.scale)

        return ret

    def draw_image(self, e, f):
        if self.current_doc == None:
            return
        translate = self.translate(
            self.current_doc.get_width(), self.current_doc.get_height())
        pixbuf = self.current_doc.scale_simple(
            translate["width"], translate["height"], gtk.gdk.INTERP_NEAREST)
        self.canvas.window.draw_pixbuf(
            None, pixbuf, 0, 0, translate["translate_x"], translate["translate_y"], translate["width"], translate["height"])

    def populate(self, lst=None, parent=None):
        if lst == None:
            lst = self.store.get_table("structure")
        for key in lst.keys():
            alert = self.check_status(key)
            row = self.treeStore.append(
                parent, [key, self.store.get_attr("base", key, "base.name"), alert])
            self.populate(lst[key], row)

    def check_status(self, elm):
        alerts = self.store.get("alert", elm)
        r = self.status_icons["alert.none"]
        for e in alerts:
            try:
                if alerts[e]["severity"] == 1:
                    r = self.status_icons[e]
            except:
                pass
        for e in alerts:
            try:
                if alerts[e]["severity"] == 0:
                    r = self.status_icons[e]
            except:
                pass
        return r

    def check_alerts(self):
        alerts = self.store.get_table("alert")
        self.dashStore.clear()
        fatal = 0
        for key in alerts:
            for lkey in alerts[key]:
                if alerts[key][lkey]["severity"] == 0:
                    self.dashStore.append(
                        ["#2396a6", self.status_icons[lkey], self.store.get_attr("base", key, "base.name"), str(alerts[key][lkey]["content"])])
                else:
                    self.dashStore.prepend(
                        ["#d03d3c", self.status_icons[lkey], self.store.get_attr("base", key, "base.name"), str(alerts[key][lkey]["content"])])
                    fatal += 1
        self.dashTitle.set_text(self.lang.get(
            "gtk.notebook.dash.title").replace("$value", str(fatal)))
        self.dash.show_all()

    def page_change(self, e, n, v):
        if len(self.selection) > 0:
            if v == self.TAB_GRAPH:
                self.current_doc = self.graph.generate()
            elif v == self.TAB_TERMINAL:
                self.open_internal_terminal()
            gobject.idle_add(self.canvas.queue_draw,
                             priority=gobject.PRIORITY_LOW)

    def draw(self, elm, changed):
        if len(elm) > 0:
            ref = False
            if self.notebook.get_current_page() == self.TAB_GRAPH:
                self.current_doc = self.graph.generate()
                ref = True
            elif self.notebook.get_current_page() == self.TAB_TERMINAL and changed == True:
                self.open_internal_terminal()
                ref = True

            if ref:
                gobject.idle_add(self.canvas.queue_draw,
                                 priority=gobject.PRIORITY_LOW)

    def draw_all_map(self, w):
        self.current_doc = self.graph.generate_all_map()
        gobject.idle_add(self.canvas.queue_draw,
                         priority=gobject.PRIORITY_LOW)

    def __init__(self):
        super(Boot, self).__init__()
        self._stop = Event()
        self.lang = LangStore(self)
        self.lang.read()
        self.config = ConfigStore(self)
        self.config.read()
        self.api = API(self)
        self.run()
        self.store = Database(self)
        self.terminalbox = Terminal(self)
        self.prepare()
        self.build()
        self.runner = Thread(target=self.server_refresh)
        self.runner.start()
        self.show_all()

    def on_key_release(self, widget, ev, data=None):
        if gtk.gdk.keyval_name(ev.keyval) == "Escape":
            self.exit()

    def graph_update(self):
        self.selection_changed(None)

    def export(self, _):
        Export(self.store)

    def exit(self):
        self._stop.set()

    def run(self):
        auth = True
        while auth:
            auth = False
            if not self.api.is_server_online():
                self.config.check()
                self.api.reset()
            try:
                self.auth_gui(None)
            except:
                Error(self,  self.lang.get("gtk.serverdown.dialog.text"))
                exit(0)
            if not self.api.auth_check():
                auth = AskConfirmation(
                    self,  self.lang.get("gtk.loginfailed.dialog.text")).is_ok()
                if not auth:
                    exit(0)

    def auth_gui(self, _):
        if not self.api.auth_check():
            u = Ask(None, self.lang.get("gtk.login.dialog.title"),
                    self.lang.get("gtk.login.dialog.username"))
            if u.is_ok():
                p = Ask(None, self.lang.get("gtk.login.dialog.title"),
                        self.lang.get("gtk.login.dialog.password"), False)
                if p.is_ok():
                    self.api.auth_user(u.getResponse(), p.getResponse())

    def selection_changed(self, widget):
        (model, pathlist) = self.tree.get_selection().get_selected_rows()
        value = []
        for path in pathlist:
            cur = model.get_iter(path)
            self.selection_cur = cur
            while cur != None:
                value.append(model.get_value(cur, 0))
                cur = model.iter_parent(cur)

        if value != None:
            if self.selection != value:
                changed = True
                self.scale = 1
                self.lx = 0
                self.x = 0
                self.ly = 0
                self.y = 0
                self.selection = value
            else:
                changed = False
            self.draw(value, changed)


if __name__ == '__main__':
    mainBoot = Boot()
    gtk.main()
    mainBoot.exit()
