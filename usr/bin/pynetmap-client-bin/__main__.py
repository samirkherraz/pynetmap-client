#!/usr/bin/python
import os
import gobject
gobject.threads_init()
import gtk
gtk.gdk.threads_init()
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)
import time
from threading import Lock
from database import Database
from dialog import Edit, Add, Ask, AskConfirmation, Error
from graph import Graph
from terminal import Terminal
from api import APIDaemon
from export import Export

from configstore import ConfigStore


class Boot(gtk.Window):

    def prepare(self):
        self.gtk_threading_lock = Lock()
        self.graph = Graph(self.store)
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
        self.set_title("DorRiver Infra")
        self.set_default_size(1000, 600)
        self.set_position(gtk.WIN_POS_CENTER)
        self.connect("delete_event", gtk.main_quit)
        self.connect("key-press-event", self.on_key_release)
        self.status_ram = self.render_icon(gtk.STOCK_DIALOG_INFO, 1)
        self.status_disk = self.render_icon(gtk.STOCK_HARDDISK, 1)
        self.status_cpu = self.render_icon(gtk.STOCK_EXECUTE, 1)
        self.status_ok = self.render_icon(gtk.STOCK_OK, 0)
        self.status_unknown = self.render_icon(gtk.STOCK_EDIT, 1)
        self.status_stop = self.render_icon(gtk.STOCK_STOP, 1)

    def open_terminal(self, _o):
        k = self.store.head()
        for o in reversed(self.selection):
            el = k[o]
            k = el["__CHILDREN__"]
        Terminal(el, self.config)

    def build(self):

        self.treeStore = gtk.TreeStore(str, str, gtk.gdk.Pixbuf)
        self.tree = gtk.TreeView(self.treeStore)

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

        self.tree.set_model(self.treeStore)
        self.tree.set_enable_search(False)
        self.tree.connect("cursor-changed", self.selection_changed)

        tvcolumn = gtk.TreeViewColumn('Infrastructures')
        self.tree.append_column(tvcolumn)
        cell = gtk.CellRendererText()
        tvcolumn.pack_start(cell, True)
        tvcolumn.add_attribute(cell, 'text', 1)
        tvcolumn = gtk.TreeViewColumn('Status')
        self.tree.append_column(tvcolumn)
        cell = gtk.CellRendererPixbuf()
        tvcolumn.pack_start(cell, True)
        tvcolumn.add_attribute(cell, 'pixbuf', 2)
        toolbar = gtk.Toolbar()
        toolbar.set_style(gtk.TOOLBAR_ICONS)
        vBox = gtk.VBox(False, 2)

        newtb = gtk.ToolButton(gtk.STOCK_NEW)
        newtb.connect("clicked", self.new_entry)
        toolbar.insert(newtb, 0)

        newtb = gtk.ToolButton(gtk.STOCK_EDIT)
        newtb.connect("clicked", self.edit_entry)
        toolbar.insert(newtb, 1)

        newtb = gtk.ToolButton(gtk.STOCK_DELETE)
        newtb.connect("clicked", self.delete_entry)
        toolbar.insert(newtb, 2)

        newtb = gtk.ToolButton(gtk.STOCK_MEDIA_PLAY)
        newtb.connect("clicked", self.open_terminal)
        toolbar.insert(newtb, 3)

        newtb = gtk.ToolButton(gtk.STOCK_FIND)
        newtb.connect("clicked", self.search)
        toolbar.insert(newtb, 4)

        newtb = gtk.ToolButton(gtk.STOCK_SAVE)
        newtb.connect("clicked", self.export)
        toolbar.insert(newtb, 5)

        newtb = gtk.ToolButton(gtk.STOCK_REFRESH)
        newtb.connect("clicked", self.reload)
        toolbar.insert(newtb, 6)

        newtb = gtk.ToolButton(gtk.STOCK_PROPERTIES)
        newtb.connect("clicked", self.edit_config)
        toolbar.insert(newtb, 7)

        vBox.pack_start(toolbar, False, False, 0)
        hBox = gtk.HPaned()
        hBox.set_position(300)
        swin = gtk.ScrolledWindow()
        swin.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        swin.add_with_viewport(self.tree)
        vBoxLeft = gtk.VBox()
        vBoxLeft.add(swin)
        hBox.add(vBoxLeft)
        hBox.add(self.canvas)
        vBox.add(hBox)
        self.add(vBox)

    def edit_config(self, _):
        self.config.check()
        self.api.reset()
        self.api.reload()

    def search(self, elm):
        res = Ask(self, "Search", "Type any on object fields value/part")
        if res.is_ok():
            key = self.store.search_in_attr(res.getResponse())
            if key != None:
                key = key["__ID__"]
            else:
                return False
            if self.search_function(key, [0]):
                self.selection_changed(None)

    def search_function(self, key, path):

        while True:
            npath = ':'.join(str(x) for x in path)
            try:
                cur = self.tree.get_model().get_iter_from_string(npath)
                if key == self.treeStore.get_value(cur, 1):
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
        dia = Add(self, self.store)
        result = dia.run()
        if result == gtk.RESPONSE_OK:
            obj = dia.getFields()
            parent_id = dia.getParent()
            self.store.add(parent_id, obj)
            self.api.push_data(self.store)
            self.treeStore.clear()
            self.populate(self.store.head())
            self.tree.expand_all()

        dia.destroy()

    def edit_entry(self, widget):
        k = self.store.head()
        for o in reversed(self.selection):
            el = k[o]
            k = el["__CHILDREN__"]
        dia = Edit(self, self.store)
        dia.setFields(el)
        if len(self.selection) > 1:
            dia.setParent(self.selection[1])
        result = dia.run()
        if result == gtk.RESPONSE_OK:
            obj = dia.getFields()
            parent_id = dia.getParent()
            self.store.edit(parent_id,
                            self.selection[0], obj)
            self.api.push_data(self.store)
            self.treeStore.clear()
            self.populate(self.store.head())
            self.tree.expand_all()

        dia.destroy()

    def reload(self, _):
        self.api.reload()

    def refresh(self):
        self.treeStore.clear()
        self.populate(self.store.head())
        self.tree.expand_all()
        k = self.store.head()
        el = None
        for o in reversed(self.selection):
            el = k[o]
            k = el["__CHILDREN__"]
        if el != None:
            if self.search_function(str(el["__ID__"]), [0]):
                self.selection_changed(None)

    def delete_entry(self, widget):
        k = self.store.head()
        for o in reversed(self.selection):
            el = k[o]
            k = el["__CHILDREN__"]
        r = AskConfirmation(self, "Do You Want to delete " + str(el["__ID__"]))
        if r.is_ok():
            if len(self.selection) > 1:
                self.store.delete(self.selection[1], self.selection[0])
            else:
                self.store.delete(None, self.selection[0])

            self.api.push_data(self.store)
            self.treeStore.clear()
            self.populate(self.store.head())
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

    def populate(self, lst, parent=None):
        for key in lst.keys():
            store = lst[key]
            alert = self.check_status(store)
            row = self.treeStore.append(
                parent, [key, store["__ID__"], alert])
            self.populate(store["__CHILDREN__"], row)

    def check_status(self, elm):
        try:
            if elm["Status"] != "running":
                return self.status_stop
        except:
            """ not concernet """
            return self.status_ok
        try:
            if float(elm["Disk"][len(elm["Disk"])-1].replace("[^0-9.]+", "").replace("%", "")) > 90:
                return self.status_disk
        except:
            return self.status_unknown
        try:
            if float(elm["CPU Usage"][len(elm["CPU Usage"])-1].replace("[^0-9.]+", "").replace("%", "")) > 90:
                return self.status_cpu
        except:
            return self.status_unknown
        try:
            if float(elm["Memory"][len(elm["Memory"])-1].replace("[^0-9.]+", "").replace("%", "")) > 90:
                return self.status_ram
        except:
            return self.status_unknown

        return self.status_ok

    def draw(self, elm):
        if len(elm) > 0:
            self.current_doc = self.graph.generate(elm)
            gobject.idle_add(self.canvas.queue_draw,
                             priority=gobject.PRIORITY_LOW)

    def draw_all_map(self, w):
        self.current_doc = self.graph.generate_all_map()
        gobject.idle_add(self.canvas.queue_draw,
                         priority=gobject.PRIORITY_LOW)

    def __init__(self, store):
        super(Boot, self).__init__()
        self.config = ConfigStore()
        self.config.read()
        self.store = store
        self.prepare()
        self.build()
        self.api = APIDaemon(self)

    def on_key_release(self, widget, ev, data=None):
        if gtk.gdk.keyval_name(ev.keyval) == "Escape":
            self.exit()

    def graph_update(self):
        self.selection_changed(None)

    def export(self, _):
        Export(self.store)

    def exit(self):
        if self.api.is_alive():
            self.api.stop()
            self.api.join()

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
                Error(self, "Server down")
                exit(0)
            if self.api.auth_check():
                self.api.start()
                self.show_all()
            else:
                auth = AskConfirmation(
                    self, "Wrong Login or Password, do you want to retry ?").is_ok()
                if not auth:
                    exit(0)

    def auth_gui(self, _):
        if not self.api.auth_check():
            u = Ask(None, "API AUTH", "Username")
            if u.is_ok():
                p = Ask(None, "API AUTH", "Password", False)
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
                self.scale = 1
                self.lx = 0
                self.x = 0
                self.ly = 0
                self.y = 0
                self.selection = value
            self.draw(value)


if __name__ == '__main__':
    store = Database()
    mainBoot = Boot(store)
    mainBoot.run()
    gtk.main()
    mainBoot.exit()
