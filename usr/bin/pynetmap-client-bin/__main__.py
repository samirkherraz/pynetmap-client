#!/usr/bin/env python
__author__ = 'Samir KHERRAZ'
__copyright__ = '(c) Samir HERRAZ 2018-2018'
__version__ = '1.1.0'
__licence__ = 'GPLv3'

import os
import signal
import time
from threading import Event, Lock, Thread
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf


from api import API
from configstore import ConfigStore
from const import *
from database import Database
from dialog import Add, Ask, AskConfirmation, Edit, Error, Notify
from export import Export
from graph import Graph
from langstore import LangStore
from terminal import Terminal

GLib.threads_init()
Gdk.threads_init()
signal.signal(signal.SIGINT, signal.SIG_DFL)
""" ameliorer search"""
class TrayIcon(Gtk.StatusIcon):
    def __init__(self, main):
        Gtk.StatusIcon.__init__(self)
        self.main = main
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size("/usr/share/pynetmap/icon.png",48,48)
        self.set_from_pixbuf(pixbuf)
        #self.set_tooltip('PyNetMap')
        self.set_visible(True)

        self.menu = menu = Gtk.Menu()

        reload_item = Gtk.MenuItem("Reload")
        reload_item.connect("activate", self.reload)
        menu.append(reload_item)

        window_item = Gtk.MenuItem("Show Window")
        window_item.connect("activate", self.show_window)
        menu.append(window_item)

        quit_item = Gtk.MenuItem("Quit")
        quit_item.connect("activate", self.quit)
        menu.append(quit_item)

        menu.show_all()

        self.connect("activate", self.show_window)
        self.connect('popup-menu', self.icon_clicked)

    def show_window(self, widget, event=None):
        self.main.present()    

    def icon_clicked(self, status, button, time):
        self.menu.popup(None, None, None, button, time)

    def reload(self, widget,event=None):
        self.main.refresh()

    def quit(self, widget, event=None):
        self.main.hide()
        self.main.exit()
        Gtk.main_quit()

class Boot(Gtk.Window):


    
    def on_delete_event(self, widget, event):
        self.hide()
        return True    



    def prepare(self):
        self.Gtk_threading_lock = Lock()
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
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.connect("delete_event", self.on_delete_event)
        self.connect("key-press-event", self.on_key_release)

        self.tray = TrayIcon(self)


        self.status_icons = dict()
        self.status_icons["alert.memory"] = self.render_icon(
            Gtk.STOCK_DIALOG_INFO, 1)
        self.status_icons["alert.disk"] = self.render_icon(
            Gtk.STOCK_HARDDISK, 1)
        self.status_icons["alert.mounts"] = self.render_icon(
            Gtk.STOCK_HARDDISK, 1)
        self.status_icons["alert.cpu"] = self.render_icon(Gtk.STOCK_EXECUTE, 1)
        self.status_icons["alert.required_fields"] = self.render_icon(
            Gtk.STOCK_EDIT, 1)

        self.status_icons["alert.tunnel"] = self.render_icon(
            Gtk.STOCK_NETWORK, 1)

        self.status_icons["alert.status"] = self.render_icon(Gtk.STOCK_STOP, 1)
        self.status_icons["alert.none"] = self.render_icon("", 1)

    def server_refresh(self):
        while not self._stop.isSet():
            try:
                if not self.api.auth_check():
                    # Notify(self.ui.lang.get("Gtk.notify.connection.lost.title"),
                    #        self.ui.lang.get("Gtk.notify.connection.lost.text"))
                    self.api.auth()
                    raise Exception("AUTH")

                self.store.refresh()
                #self.check_alerts()

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
                img = Gtk.Image()
                img.set_from_pixbuf(self.render_icon(
                    Gtk.STOCK_DIALOG_AUTHENTICATION, 6))
                self.terminal.add(img)
            self.terminal.show_all()

    def build(self):



        self.dashStore = Gtk.ListStore(str, GdkPixbuf.Pixbuf, str, str)
        self.dash = Gtk.TreeView(self.dashStore)
        self.dash.set_grid_lines(True)
        self.dash.set_headers_visible(False)
        self.dash.set_model(self.dashStore)
        self.dash.set_enable_search(False)
        self.dash.get_selection().set_mode(Gtk.SelectionMode.NONE)

        tvcolumn = Gtk.TreeViewColumn()
        self.dash.append_column(tvcolumn)
        cell = Gtk.CellRendererText()
        cell.set_padding(0, 10)
        tvcolumn.pack_start(cell, True)
        tvcolumn.add_attribute(cell, "background", 0)

        tvcolumn = Gtk.TreeViewColumn()
        self.dash.append_column(tvcolumn)
        cell = Gtk.CellRendererPixbuf()
        cell.set_padding(0, 10)
        tvcolumn.pack_start(cell, True)
        tvcolumn.add_attribute(cell, 'pixbuf', 1)

        tvcolumn = Gtk.TreeViewColumn()
        self.dash.append_column(tvcolumn)
        cell = Gtk.CellRendererText()
        cell.set_padding(0, 10)
        tvcolumn.pack_start(cell, True)
        tvcolumn.add_attribute(cell, 'text', 2)

        tvcolumn = Gtk.TreeViewColumn()
        self.dash.append_column(tvcolumn)
        cell = Gtk.CellRendererText()
        cell.set_padding(0, 10)
        tvcolumn.pack_start(cell, True)
        tvcolumn.add_attribute(cell, 'text', 3)

        self.canvas = Gtk.DrawingArea()
        self.canvas.modify_bg(Gtk.StateType.NORMAL, Gdk.Color(1,1,1))
        self.canvas.connect("draw", self.draw_image)
        self.canvas.set_events(self.canvas.get_events()
              | Gdk.EventMask.BUTTON_PRESS_MASK       # mouse down
              | Gdk.EventMask.BUTTON_RELEASE_MASK   # mouse up
              | Gdk.EventMask.LEAVE_NOTIFY_MASK   # mouse up
              | Gdk.EventMask.SCROLL_MASK   # mouse up
              | Gdk.EventMask.POINTER_MOTION_HINT_MASK   # mouse up
              | Gdk.EventMask.POINTER_MOTION_MASK)   # mouse move

        self.canvas.connect("motion_notify_event", self.drag)
        self.canvas.connect("button_press_event", self.mouse_on)
        self.canvas.connect("button_release_event", self.mouse_off)
        self.canvas.connect('scroll-event', self.scroll)

        self.treeStore = Gtk.TreeStore(str, str, GdkPixbuf.Pixbuf)
        self.tree = Gtk.TreeView(self.treeStore)
        self.tree.set_model(self.treeStore)
        self.tree.set_enable_search(False)
        self.tree.connect("cursor-changed", self.selection_changed)

        tvcolumn = Gtk.TreeViewColumn(self.lang.get("Gtk.tree.name"))
        self.tree.append_column(tvcolumn)
        cell = Gtk.CellRendererText()
        tvcolumn.pack_start(cell, True)
        tvcolumn.add_attribute(cell, 'text', 1)

        tvcolumn = Gtk.TreeViewColumn(self.lang.get("Gtk.tree.state"))
        self.tree.append_column(tvcolumn)
        cell = Gtk.CellRendererPixbuf()
        tvcolumn.pack_start(cell, True)
        tvcolumn.add_attribute(cell, 'pixbuf', 2)
        toolbar = Gtk.Toolbar()
        #toolbar.set_style(Gtk.Toolbar.ICONS)
        vBox = Gtk.VBox(False, 2)
        toolbar_n = 0
        if self.api.get_access("users.privilege.edit"):
            newtb = Gtk.ToolButton(Gtk.STOCK_NEW)
            newtb.connect("clicked", self.new_entry)
            toolbar.insert(newtb, toolbar_n)
            toolbar_n += 1

            newtb = Gtk.ToolButton(Gtk.STOCK_EDIT)
            newtb.connect("clicked", self.edit_entry)
            toolbar.insert(newtb, 1)
            toolbar_n += 1

            newtb = Gtk.ToolButton(Gtk.STOCK_DELETE)
            newtb.connect("clicked", self.delete_entry)
            toolbar.insert(newtb, toolbar_n)
            toolbar_n += 1

        if self.api.get_access("users.privilege.terminal"):
            newtb = Gtk.ToolButton(Gtk.STOCK_MEDIA_PLAY)
            newtb.connect("clicked", self.open_terminal)
            toolbar.insert(newtb, toolbar_n)
            toolbar_n += 1

        newtb = Gtk.ToolButton(Gtk.STOCK_FIND)
        newtb.connect("clicked", self.search)
        toolbar.insert(newtb, toolbar_n)
        toolbar_n += 1

        newtb = Gtk.ToolButton(Gtk.STOCK_SAVE)
        newtb.connect("clicked", self.export)
        toolbar.insert(newtb, toolbar_n)
        toolbar_n += 1

        newtb = Gtk.ToolButton(Gtk.STOCK_REFRESH)
        newtb.connect("clicked", self.open_internal_terminal)
        toolbar.insert(newtb, toolbar_n)
        toolbar_n += 1

        newtb = Gtk.ToolButton(Gtk.STOCK_PROPERTIES)
        newtb.connect("clicked", self.edit_config)
        toolbar.insert(newtb, toolbar_n)
        toolbar_n += 1

        vBox.pack_start(toolbar, False, False, 0)
        hBox = Gtk.HPaned()
        hBox.set_position(300)
        swin = Gtk.ScrolledWindow()
        swin.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        swin.add_with_viewport(self.tree)
        vBoxLeft = Gtk.VBox(True, 2)
        vBoxLeft.add(swin)
        self.notebook = Gtk.Notebook()
        self.notebook.connect("switch-page", self.page_change)
        self.notebook.append_page(self.canvas, Gtk.Label(self.lang.get(
            "Gtk.notebook.graph.title")))
        self.TAB_GRAPH = 0
        if self.api.get_access("users.privilege.terminal"):
            self.terminal = Gtk.VBox(True, 2)
            self.notebook.append_page(self.terminal, Gtk.Label(self.lang.get(
                "Gtk.notebook.terminal.title")))
            self.TAB_TERMINAL = 1
        else:
            self.TAB_TERMINAL = None

        swin = Gtk.ScrolledWindow()
        swin.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        swin.add_with_viewport(self.dash)
        self.dashTitle = Gtk.Label(self.lang.get(
            "Gtk.notebook.dash.title").replace("$value", "0"))
        self.notebook.append_page(swin, self.dashTitle)
        self.TAB_ALERTS = 2
        hBox.add(vBoxLeft)
        hBox.add(self.notebook)
        vBox.add(hBox)
        self.add(vBox)

    def edit_config(self, _):
        self.config.check()
        self.api.reset()

    def search(self, e=None):
        res = Ask(self, self.lang.get("Gtk.search.dialog.title"),
                  self.lang.get("Gtk.search.dialog.text"))
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
        GLib.idle_add(self.updateui,
                         priority=GLib.PRIORITY_HIGH)

    def delete_entry(self, widget):
        r = AskConfirmation(self,  self.lang.get("Gtk.delete.dialog.text") +
                            self.store.get_attr("base", self.selection[0], KEY_NAME))
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
            GLib.idle_add(self.canvas.queue_draw,
                             priority=GLib.PRIORITY_HIGH)

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
        if elm.direction == Gdk.ScrollDirection.UP and t["width"] < w*0.6:
            self.scale *= 1.12
        elif elm.direction == Gdk.ScrollDirection.DOWN and self.scale > 1:
            self.scale /= 1.12
        else:
            return

        GLib.idle_add(self.canvas.queue_draw,
                         priority=GLib.PRIORITY_LOW)

    def translate(self, p_width, p_height):
        ret = {}
        w = self.canvas.get_allocated_width()
        h = self.canvas.get_allocated_height()
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

    def draw_image(self, e, cr):
        if self.current_doc == None:
            return
        cr.set_source_rgb(1,1,1)
        cr.paint()
        translate = self.translate(
            self.current_doc.get_width(), self.current_doc.get_height())
        pixbuf = self.current_doc.scale_simple(translate["width"], translate["height"], 0)
        Gdk.cairo_set_source_pixbuf(cr,pixbuf, translate["translate_x"], translate["translate_y"])
        
        cr.paint()
        
    def populate(self, lst=None, parent=None):
        if lst == None:
            lst = self.store.get_table("structure")
        for key in lst.keys():
            alert = self.check_status(key)
            row = self.treeStore.append(
                parent, [key, self.store.get_attr("base", key, KEY_NAME), alert])
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
        msg = ""
        notif = False
        for key in alerts:
            for lkey in alerts[key]:
                if alerts[key][lkey]["severity"] == 0:
                    self.dashStore.append(
                        ["#2396a6", self.status_icons[lkey], self.store.get_attr("base", key, KEY_NAME), str(alerts[key][lkey]["content"])])
                else:
                    self.dashStore.prepend(
                        ["#d03d3c", self.status_icons[lkey], self.store.get_attr("base", key, KEY_NAME), str(alerts[key][lkey]["content"])])
                    fatal += 1
                    if key not in self.alerts:
                        self.alerts[key] = dict()
                    if lkey not in self.alerts[key]:
                        msg += self.store.get_attr("base", key, KEY_NAME)
                        msg += " : " + str(alerts[key][lkey]["content"])
                        msg += "\n"
                        notif = True
                        self.alerts[key][lkey] = True
        if notif:
            Notify("Alerts", msg)
        for key in self.alerts.keys():
            if key not in alerts:
                del self.alerts[key]
            else:
                for lkey in self.alerts[key].keys():
                    if lkey not in alerts[key]:
                        del self.alerts[key][lkey]

        self.dashTitle.set_text(self.lang.get(
            "Gtk.notebook.dash.title").replace("$value", str(fatal)))
        self.dash.show_all()

    def page_change(self, e, n, v):
        if len(self.selection) > 0:
            if v == self.TAB_GRAPH:
                self.current_doc = self.graph.generate()
            elif v == self.TAB_TERMINAL:
                self.open_internal_terminal()
            GLib.idle_add(self.canvas.queue_draw,
                             priority=GLib.PRIORITY_LOW)

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
                GLib.idle_add(self.canvas.queue_draw,
                                 priority=GLib.PRIORITY_LOW)

    def draw_all_map(self, w):
        self.current_doc = self.graph.generate_all_map()
        GLib.idle_add(self.canvas.queue_draw,
                         priority=GLib.PRIORITY_LOW)

    def __init__(self):
        super(Boot, self).__init__()
        self._stop = Event()
        self.alerts = dict()
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

    def on_key_release(self, widget, event, data=None):
        keyval = event.keyval
        keyval_name = Gdk.keyval_name(keyval)
        state = event.state
        ctrl = (state & Gdk.ModifierType.CONTROL_MASK)
        if ctrl and keyval_name == 'f':
            self.search()
        elif ctrl and keyval_name == 't':
            self.open_terminal()
        elif ctrl and keyval_name == 'q':
            self.tray.quit(None)
        elif ctrl and keyval_name == 'r':
            self.refresh()
        elif ctrl and keyval_name == 'Left':
            self.notebook.prev_page()
        elif ctrl and keyval_name == 'Right':
            self.notebook.next_page()
        elif keyval_name == 'Escape':
            self.hide()
        else:
            return False
        return True

    def graph_update(self):
        self.selection_changed(None)

    def export(self, _):
        Export(self)

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
                self.auth_gui()
            except ValueError :
                Error(self,  self.lang.get("gtk.serverdown.dialog.text"))
                exit(0)
            if not self.api.auth_check():
                auth = AskConfirmation(
                    self,  self.lang.get("gtk.loginfailed.dialog.text")).is_ok()
                if not auth:
                    exit(0)

    def auth_gui(self):
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
                print(self.selection)
            else:
                changed = False
            self.draw(value, changed)


if __name__ == '__main__':
    mainBoot = Boot()
    Gtk.main()
    mainBoot.exit()
