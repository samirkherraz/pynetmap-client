#!/usr/bin/env python
__author__ = 'Samir KHERRAZ'
__copyright__ = '(c) Samir HERRAZ 2018-2019'
__version__ = '1.3.0'
__licence__ = 'GPLv3'

import os
import signal
import time
from threading import Event, Lock, Thread
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf

from Core.Libs.Api import Api
from Core.Libs.Config import Config
from Core.Libs.Lang import Lang
from Core.Libs.MDExport import MDExport
from Constants import *
from Core.Libs.Graph import Graph
from Core.Libs.Terminal import Terminal
from Core.Dialogs.GtkAdd import GtkAdd
from Core.Dialogs.GtkAsk import GtkAsk
from Core.Dialogs.GtkConfirmation import GtkConfirmation
from Core.Dialogs.GtkEdit import GtkEdit
from Core.Dialogs.GtkError import GtkError
from Core.Dialogs.GtkNotify import GtkNotify
from Core.Dialogs.GtkConfig import GtkConfig
from Core.Dialogs.GtkUsers import GtkUsers


class UIObjects():

    def __init__(self):
        self.call_select = True
        self.terminalbox = Terminal()
        self.graph = Graph()
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
        self.TAB_GRAPH = 0
        self.TAB_TERMINAL = 1
        self.TAB_ALERTS = 2


class GtkEvents(Thread):

    def _exec(self, fn, *args):
        GLib.idle_add(fn, args=args,
                      priority=GLib.PRIORITY_LOW)

    def __init__(self, window):
        Thread.__init__(self)
        self.win = window
        self.obj = UIObjects()

    def on_delete_event(self, widget, event):
        self._exec(self.win.hide)
        return True

    def on_open_terminal(self, _=None):
        if Api.getInstance().get_access("terminal"):
            if len(self.obj.selection) > 0:
                self.obj.terminalbox.external(self.obj.selection[0])

    def on_open_internal_terminal(self, e=None):
        if Api.getInstance().get_access("terminal"):
            self.win.terminal.forall(self.win.terminal.remove)
            term = self.obj.terminalbox.internal(
                self.obj.selection[0], e != None)
            if term != None:
                self.win.terminal.add(term)
            else:
                img = Gtk.Image()
                img.set_from_pixbuf(self.win.render_icon(
                    Gtk.STOCK_DIALOG_AUTHENTICATION, 6))
                self.win.terminal.add(img)
            self._exec(self.win.terminal.show_all)

    def on_edit_users(self, _=None):
        GtkUsers(self.win)

    def on_edit_config(self, _=None):
        GtkConfig(self.win)

    def on_search(self, e=None):
        res = GtkAsk(self.win, Lang.getInstance().get("Gtk.search.title"),
                     Lang.getInstance().get("Gtk.search.text"))
        if res.is_ok():
            keys = Api.getInstance().find(DB_BASE, res.getResponse())
            if len(keys) > 0:
                key = keys[0]
            else:
                return False
            if self.search_function(key, [0]):
                self.on_selection_change(None)

    def search_function(self, key, path):
        self.win.tree.expand_all()
        while True:
            npath = ':'.join(str(x) for x in path)
            try:
                cur = self.win.tree.get_model().get_iter_from_string(npath)

                if key == self.win.treeStore.get_value(cur, 0):
                    self.win.tree.get_selection().select_iter(cur)
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

    def on_refresh(self):
        self._exec(self._updateui)

    def _updateui(self):
        self.obj.call_select = False
        self.win.treeStore.clear()
        self._populate()
        self.win.tree.expand_all()
        if len(self.obj.selection) > 0:
            if self.search_function(self.obj.selection[0], [0]):
                self.on_selection_change(None)
        self.obj.call_select = True

    def _populate(self, names=None, lst=None, parent=None):
        if lst == None:
            lst = Api.getInstance().get(DB_STRUCT)
        if names == None:
            names = Api.getInstance().get(DB_BASE)

        for key in lst.keys():
            row = self.win.treeStore.append(
                parent, [key, names[key][KEY_NAME]])
            self._populate(names, lst[key], row)

    def on_new_entry(self, widget):
        GtkAdd(self.win)
        self.on_refresh()

    def on_edit_entry(self, widget):
        GtkEdit(self.win, self.obj.selection)

    def on_delete_entry(self, widget):
        r = GtkConfirmation(self.win,  Lang.getInstance().get("Gtk.delete.text") +
                            Api.getInstance().get(DB_BASE, self.obj.selection[0], KEY_NAME))
        if r.is_ok():
            if len(self.obj.selection) > 1:
                Api.getInstance().delete(
                    self.obj.selection[1], self.obj.selection[0])
            else:
                Api.getInstance().delete(None, self.obj.selection[0])
            self.on_refresh()

    def on_page_change(self, e, n, v):
        if len(self.obj.selection) > 0:
            if v == self.obj.TAB_GRAPH:
                self.obj.current_doc = self.obj.graph.generate(
                    self.obj.selection)
            elif v == self.obj.TAB_TERMINAL:
                self.on_open_internal_terminal()
            GLib.idle_add(self.win.canvas.queue_draw,
                          priority=GLib.PRIORITY_LOW)

    def on_key_release(self, widget, event, data=None):
        keyval = event.keyval
        keyval_name = Gdk.keyval_name(keyval)
        state = event.state
        ctrl = (state & Gdk.ModifierType.CONTROL_MASK)
        if ctrl and keyval_name == 'f':
            self.on_search()
        elif ctrl and keyval_name == 't':
            self.on_open_terminal()
        elif ctrl and keyval_name == 'q':
            self.on_quit(None)
        elif ctrl and keyval_name == 'r':
            self.on_refresh()
        elif ctrl and keyval_name == 'Left':
            self._exec(self.win.notebook.prev_page)
        elif ctrl and keyval_name == 'Right':
            self._exec(self.win.notebook.next_page)
        elif keyval_name == 'Escape':
            self.win.hide()
        else:
            return False
        return True

    def on_export(self, _):
        MDExport()

    def on_selection_change(self, widget):
        if self.obj.call_select:
            (model, pathlist) = self.win.tree.get_selection().get_selected_rows()
            value = []
            for path in pathlist:
                cur = model.get_iter(path)
                self.obj.selection_cur = cur
                while cur != None:
                    value.append(model.get_value(cur, 0))
                    cur = model.iter_parent(cur)

            if value != None:
                if self.obj.selection != value:
                    changed = True
                    self.obj.scale = 1
                    self.obj.lx = 0
                    self.obj.x = 0
                    self.obj.ly = 0
                    self.obj.y = 0
                    self.obj.selection = value
                else:
                    changed = False

                Thread(target=self.on_draw, args=(value, changed,)).start()

    def on_drag(self, widget, elm):
        curtime = time.time()
        if self.obj.mousedown and curtime > (self.obj.lasttime + 0.025):
            self.obj.dragged = True
            self.obj.lasttime = curtime
            x, y = widget.get_pointer()
            self.obj.x = x/self.obj.scale
            self.obj.y = y/self.obj.scale
            GLib.idle_add(self.win.canvas.queue_draw,
                          priority=GLib.PRIORITY_HIGH)

    def on_mouse_on(self, widget, elm):
        if elm.button == 1:
            self.obj.dragged = False
            self.obj.lasttime = 0
            x, y = widget.get_pointer()
            self.obj.llx = self.obj.lx
            self.obj.lly = self.obj.ly
            self.obj.lx = x/self.obj.scale - (self.obj.x - self.obj.lx)
            self.obj.ly = y/self.obj.scale - (self.obj.y - self.obj.ly)
            self.obj.mousedown = True

    def on_mouse_off(self, widget, elm):
        if elm.button == 1:
            self.obj.mousedown = False
            if not self.obj.dragged:
                self.obj.lx = self.obj.llx
                self.obj.ly = self.obj.lly

    def on_scroll(self, widget, elm):
        if self.obj.current_doc == None:
            return
        w = self.obj.current_doc.get_width()
        h = self.obj.current_doc.get_height()
        t = self._translate(w, h)
        x, y = widget.get_pointer()
        self.obj.lx = x - (self.obj.x - self.obj.lx)
        self.obj.ly = y - (self.obj.y - self.obj.ly)
        self.obj.x = x
        self.obj.y = y
        if elm.direction == Gdk.ScrollDirection.UP and t["width"] < w*0.6:
            self.obj.scale *= 1.12
        elif elm.direction == Gdk.ScrollDirection.DOWN and self.obj.scale > 1:
            self.obj.scale /= 1.12
        else:
            return

        GLib.idle_add(self.win.canvas.queue_draw,
                      priority=GLib.PRIORITY_LOW)

    def _translate(self, p_width, p_height):
        ret = {}
        w = self.win.canvas.get_allocated_width()
        h = self.win.canvas.get_allocated_height()
        scale_w = float(w)/float(p_width)
        scale_h = float(h)/float(p_height)
        ret["scale_w"] = (min(scale_h, scale_w)) * self.obj.scale
        ret["scale_h"] = (min(scale_h, scale_w)) * self.obj.scale
        ret["width"] = int(p_width*ret["scale_w"])
        ret["height"] = int(p_height*ret["scale_h"])
        ret["translate_x"] = int(w/2-ret["width"]/2)
        ret["translate_y"] = int(h/2-ret["height"]/2)
        ret["translate_x"] += int((self.obj.x - self.obj.lx) * self.obj.scale)
        ret["translate_y"] += int((self.obj.y - self.obj.ly) * self.obj.scale)

        return ret

    def on_draw_image(self, e, cr):
        if self.obj.current_doc == None:
            return
        cr.set_source_rgb(1, 1, 1)
        cr.paint()
        translate = self._translate(
            self.obj.current_doc.get_width(), self.obj.current_doc.get_height())
        pixbuf = self.obj.current_doc.scale_simple(
            translate["width"], translate["height"], 0)
        Gdk.cairo_set_source_pixbuf(
            cr, pixbuf, translate["translate_x"], translate["translate_y"])

        cr.paint()

    def on_draw(self, elm, changed):
        if len(elm) > 0:
            ref = False
            if self.win.notebook.get_current_page() == self.obj.TAB_GRAPH:
                self.obj.current_doc = self.obj.graph.generate(
                    self.obj.selection)
                ref = True
            elif self.win.notebook.get_current_page() == self.obj.TAB_TERMINAL and changed == True:
                self.on_open_internal_terminal()
                ref = True

            if ref:
                GLib.idle_add(self.win.canvas.queue_draw,
                              priority=GLib.PRIORITY_LOW)

    def draw_all_map(self, w):
        self.obj.current_doc = self.obj.graph.generate_all_map()
        GLib.idle_add(self.win.canvas.queue_draw,
                      priority=GLib.PRIORITY_LOW)

    def on_auth_gui(self):
        if not Api.getInstance().auth_check():
            u = GtkAsk(self.win, Lang.getInstance().get("gtk.login.title"),
                       Lang.getInstance().get("gtk.login.username"))
            if u.is_ok():
                p = GtkAsk(self.win, Lang.getInstance().get("gtk.login.title"),
                           Lang.getInstance().get("gtk.login.password"), False)
                if p.is_ok():
                    Api.getInstance().auth_user(u.getResponse(), p.getResponse())

    def authentificate(self):
        
        if not Api.getInstance().is_server_online():
            GtkError(self.win,  Lang.getInstance().get("gtk.serverdown.text"))
            self.on_edit_config()
            if not Api.getInstance().is_server_online():
                GtkError(self.win,  Lang.getInstance().get(
                    "gtk.serverdown.text"))
                return False

        for _ in range(3):
            self.on_auth_gui()
            if Api.getInstance().auth_check():
                return True
            else:
                retry = GtkConfirmation(
                    self.win,  Lang.getInstance().get("gtk.loginfailed.text")).is_ok()
                if not retry:
                    return False

    def on_show_window(self, widget, event=None):
        self._exec(self.win.present)

    def on_icon_clicked(self, status, button, time):
        self._exec(self.win.tray.menu.show_all)
        self.win.tray.menu.popup(
            None, None, None, Gtk.StatusIcon.position_menu, button, time)

    def on_reload(self, widget, event=None):
        self.win.refresh()

    def on_start(self, widget, event=None):
        self._exec(self.win.build)
        self._exec(self.win.present)
        self._exec(self.on_refresh)

    def on_quit(self, widget, event=None):
        self._exec(self.win.hide)
        self._exec(Gtk.main_quit)
