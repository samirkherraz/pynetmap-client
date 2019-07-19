#!/usr/bin/env python
__author__ = 'Samir KHERRAZ'
__copyright__ = '(c) Samir HERRAZ 2018-2019'
__version__ = '1.2.0'
__licence__ = 'GPLv3'

import os
import signal
import time
from threading import Event, Lock, Thread
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf

from Core.Libs.Api import Api
from Core.Libs.Config import Config
from Core.Libs.Lang import Lang
from Constants import *
from Core.Window.GtkTrayIcon import GtkTrayIcon
from Core.Window.GtkEvents import GtkEvents
class GtkMainWindow(Gtk.Window):

    def build(self):
        self.build_toolbar()
        self.build_tree()
        self.build_notebook()
        self.build_canvas()
        self.build_notebook_graph()
        self.build_notebook_terminal()
        self.build_dash()
        self.build_notebook_alerts()
        self.build_content()
        self.build_root()
        self.show_all()

    def build_content(self):
        self.content = Gtk.HPaned()
        self.content.set_position(300)
        self.content.add(self.tree_content)
        self.content.add(self.notebook)
    
    def build_root(self):
        self.root = Gtk.VBox(False, 2)
        self.root.pack_start(self.toolbar, False, False, 0)
        self.root.add(self.content)
        self.add(self.root)

    def build_notebook_terminal(self):
        if Api.getInstance().get_access("terminal"):
            self.terminal = Gtk.VBox(True, 2)
            self.notebook.append_page(self.terminal, Gtk.Label(Lang.getInstance().get(
                "Gtk.notebook.terminal.title")))

    def build_notebook_graph(self):
        self.notebook.append_page(self.canvas, Gtk.Label(Lang.getInstance().get(
            "Gtk.notebook.graph.title")))


    def build_notebook_alerts(self):
        swin = Gtk.ScrolledWindow()
        swin.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        swin.add_with_viewport(self.dash)
        self.dashTitle = Gtk.Label(Lang.getInstance().get(
            "Gtk.notebook.dash.title").replace("$value", "0"))
        self.notebook.append_page(swin, self.dashTitle)


    def build_notebook(self):
        self.notebook = Gtk.Notebook()
        self.notebook.connect("switch-page", self.event.on_page_change)
       

    def build_tree(self):
        self.treeStore = Gtk.TreeStore(str, str)
        self.tree = Gtk.TreeView(self.treeStore)
        self.tree.set_model(self.treeStore)
        self.tree.set_enable_search(False)
        self.tree.connect("cursor-changed", self.event.on_selection_change)

        tvcolumn = Gtk.TreeViewColumn(Lang.getInstance().get("Gtk.tree.name"))
        cell = Gtk.CellRendererText()
        tvcolumn.pack_start(cell, True)
        tvcolumn.add_attribute(cell, 'text', 1)
        self.tree.append_column(tvcolumn)

        tvcolumn = Gtk.TreeViewColumn(Lang.getInstance().get("Gtk.tree.state"))
        cell = Gtk.CellRendererPixbuf()
        tvcolumn.pack_start(cell, True)
        tvcolumn.add_attribute(cell, 'pixbuf', 2)
        #self.tree.append_column(tvcolumn)
        swin = Gtk.ScrolledWindow()
        swin.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        swin.add_with_viewport(self.tree)
        self.tree_content = Gtk.VBox(True, 2)
        self.tree_content.add(swin)
        

    def build_canvas(self):
        self.canvas = Gtk.DrawingArea()
        self.canvas.modify_bg(Gtk.StateType.NORMAL, Gdk.Color(1,1,1))
        self.canvas.connect("draw", self.event.on_draw_image)
        self.canvas.set_events(self.canvas.get_events()
              | Gdk.EventMask.BUTTON_PRESS_MASK       # mouse down
              | Gdk.EventMask.BUTTON_RELEASE_MASK   # mouse up
              | Gdk.EventMask.LEAVE_NOTIFY_MASK   # mouse up
              | Gdk.EventMask.SCROLL_MASK   # mouse up
              | Gdk.EventMask.POINTER_MOTION_HINT_MASK   # mouse up
              | Gdk.EventMask.POINTER_MOTION_MASK)   # mouse move

        self.canvas.connect("motion_notify_event", self.event.on_drag)
        self.canvas.connect("button_press_event", self.event.on_mouse_on)
        self.canvas.connect("button_release_event", self.event.on_mouse_off)
        self.canvas.connect('scroll-event', self.event.on_scroll)

    def build_dash(self):
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


    def build_toolbar(self):
        self.toolbar = Gtk.Toolbar()
        #toolbar.set_style(Gtk.Toolbar.ICONS)
        toolbar_n = 0
        if Api.getInstance().get_access("edit"):
            newtb = Gtk.ToolButton(Gtk.STOCK_NEW)
            newtb.connect("clicked", self.event.on_new_entry)
            self.toolbar.insert(newtb, toolbar_n)
            toolbar_n += 1

            newtb = Gtk.ToolButton(Gtk.STOCK_EDIT)
            newtb.connect("clicked", self.event.on_edit_entry)
            self.toolbar.insert(newtb, 1)
            toolbar_n += 1

            newtb = Gtk.ToolButton(Gtk.STOCK_DELETE)
            newtb.connect("clicked", self.event.on_delete_entry)
            self.toolbar.insert(newtb, toolbar_n)
            toolbar_n += 1

        if Api.getInstance().get_access("terminal"):
            newtb = Gtk.ToolButton(Gtk.STOCK_MEDIA_PLAY)
            newtb.connect("clicked", self.event.on_open_terminal)
            self.toolbar.insert(newtb, toolbar_n)
            toolbar_n += 1
        
        newtb = Gtk.ToolButton(Gtk.STOCK_FIND)
        newtb.connect("clicked", self.event.on_search)
        self.toolbar.insert(newtb, toolbar_n)
        toolbar_n += 1

        newtb = Gtk.ToolButton(Gtk.STOCK_REFRESH)
        newtb.connect("clicked", self.event.on_open_internal_terminal)
        self.toolbar.insert(newtb, toolbar_n)
        toolbar_n += 1

        newtb = Gtk.ToolButton(Gtk.STOCK_SAVE)
        newtb.connect("clicked", self.event.on_export)
        self.toolbar.insert(newtb, toolbar_n)
        toolbar_n += 1


        if Api.getInstance().get_access("manage"):
            newtb = Gtk.ToolButton(Gtk.STOCK_DIALOG_AUTHENTICATION)
            newtb.connect("clicked", self.event.on_edit_users)
            self.toolbar.insert(newtb, toolbar_n)
            toolbar_n += 1

        newtb = Gtk.ToolButton(Gtk.STOCK_PROPERTIES)
        newtb.connect("clicked", self.event.on_edit_config)
        self.toolbar.insert(newtb, toolbar_n)
        toolbar_n += 1

    def __init__(self):
        super(GtkMainWindow, self).__init__()
        self.set_title(NAME + " - " + VERSION)
        self.set_default_size(1000, 600)
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.event = GtkEvents(self)
        self.tray = GtkTrayIcon(self)
        self.connect("delete_event", self.event.on_delete_event)
        self.connect("key-press-event", self.event.on_key_release)
        if self.event.authentificate():
            self.event.on_start(None)
        else:
            self.event.on_quit(None)
       

