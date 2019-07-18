#!/usr/bin/env python
__author__ = 'Samir KHERRAZ'
__copyright__ = '(c) Samir HERRAZ 2018-2019'
__version__ = '1.3.0'
__licence__ = 'GPLv3'
from gi.repository import Gtk, Gdk, GLib
from Core.Libs.Config import Config
from Core.Libs.Lang import Lang
from Core.Libs.Api import Api
from Constants import *
from Core.Dialogs.GtkAsk import GtkAsk
import hashlib
class GtkUsers(Gtk.Dialog):
    def prepare(self):
        self._fields = dict()
        self.set_title(Lang.getInstance().get("gtk.users.title"))
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.set_default_size(800, 300)
        self.root = Gtk.VBox(expand=True, margin=12)
        swin = Gtk.ScrolledWindow()
        swin.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        swin.add_with_viewport(self.root)
        self.get_content_area().add(swin)

    def build(self):
        users = Api.getInstance().get(DB_USERS)
        self.grid = Gtk.Table(len(users)+1, 7, False)
        self.grid.set_row_spacings(12)
        i = 0
        self._fields = dict()
        j = 0
        lbl = Gtk.Label(Lang.getInstance().get("gtk.users.username"),margin=3)
        self.grid.attach(lbl, j, j+1, i, i+1)
        j += 1
        lbl = Gtk.Label(Lang.getInstance().get("gtk.users.firstname"),margin=3)
        self.grid.attach(lbl, j, j+1, i, i+1)
        j += 1
        lbl = Gtk.Label(Lang.getInstance().get("gtk.users.lastname"),margin=3)
        self.grid.attach(lbl, j, j+1, i, i+1)
        j += 1
        lbl = Gtk.Label(Lang.getInstance().get("gtk.users.password"),margin=3)
        self.grid.attach(lbl, j, j+1, i, i+1)
        j += 1
        lbl = Gtk.Label(Lang.getInstance().get("gtk.users.edit"),margin=3)
        self.grid.attach(lbl, j, j+1, i, i+1)
        j += 1
        lbl = Gtk.Label(Lang.getInstance().get("gtk.users.manage"),margin=3)
        self.grid.attach(lbl, j, j+1, i, i+1)
        j += 1
        lbl = Gtk.Label(Lang.getInstance().get("gtk.users.terminal"),margin=3)
        self.grid.attach(lbl, j, j+1, i, i+1)
        j +=1
        btn = Gtk.Button(Lang.getInstance().get("gtk.users.create"), margin=3)
        btn.connect("clicked", self.create_user)
        self.grid.attach(btn, j, j+1, i, i+1)
        i+=1
        for key in users:
                j = 0
                self._fields[key] = Gtk.Label(key, margin=3)
                self.grid.attach(self._fields[key], j, j+1, i, i+1)
                j +=1
                for k in ["firstname", "lastname"]:
                    self._fields[key+"-"+k] = Gtk.Entry(margin=3)
                    self._fields[key+"-"+k].set_text(users[key][k] if k in users[key] else "")
                    self.grid.attach(self._fields[key+"-"+k], j, j+1, i, i+1)
                    j +=1
                self._fields[key+"-password"] = Gtk.Entry(visibility=False , margin=3)
                self.grid.attach(self._fields[key+"-password"], j, j+1, i, i+1)
                j +=1
                self._fields[key+"-privilege-edit"] = Gtk.CheckButton(margin=3)
                self._fields[key+"-privilege-edit"].set_active(bool(users[key]["privilege"]["edit"]) if "privilege" in users[key] and "edit" in users[key]["privilege"]  else "")
                self.grid.attach(self._fields[key+"-privilege-edit"], j, j+1, i, i+1)
                j +=1
                self._fields[key+"-privilege-manage"] = Gtk.CheckButton(margin=3)
                self._fields[key+"-privilege-manage"].set_active(bool(users[key]["privilege"]["manage"]) if "privilege" in users[key] and "manage" in users[key]["privilege"]  else "")
                self.grid.attach(self._fields[key+"-privilege-manage"], j, j+1, i, i+1)
                j +=1
                self._fields[key+"-privilege-terminal"] = Gtk.CheckButton(margin=3)
                self._fields[key+"-privilege-terminal"].set_active(bool(users[key]["privilege"]["terminal"]) if "privilege" in users[key] and "terminal" in users[key]["privilege"]  else "")
                self.grid.attach(self._fields[key+"-privilege-terminal"], j, j+1, i, i+1)
                j +=1
                self._fields[key+"-delete"] = Gtk.ToggleButton(Lang.getInstance().get("gtk.users.delete"), margin=3)
                self.grid.attach(self._fields[key+"-delete"], j, j+1, i, i+1)
                j +=1
                i += 1
        
        
        self.root.forall(self.root.remove)
        self.root.pack_start(self.grid, False, False, 0)
        self.show_all()

    def create_user(self, _):
        u = GtkAsk(None, Lang.getInstance().get("gtk.users.username"),
                    Lang.getInstance().get("gtk.users.askusername"))
        if u.is_ok():
            p = GtkAsk(None, Lang.getInstance().get("gtk.users.password"),
                    Lang.getInstance().get("gtk.users.askpassword"))
            if p.is_ok():
                Api.getInstance().set(DB_USERS, u.getResponse(), data={ "password": hashlib.sha256(p.getResponse().encode()).hexdigest() } )
                self.build()

    def set_field(self, id, value):
        try:
            self._fields[id].set_text(value)
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
            elif type(self._fields[id]) is Gtk.ToggleButton:
                ret = self._fields[id].get_active()

            return ret
        except:
            return None

    def __init__(self, parent):
        Gtk.Dialog.__init__(self, Lang.getInstance().get("gtk.users.title"), parent, flags=Gtk.DialogFlags.MODAL,
                            buttons=(Gtk.STOCK_OK, Gtk.ResponseType.OK,
                                     Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
        self.prepare()
        self.build()
        self.show_all()
        result = self.run()
        if result == Gtk.ResponseType.OK:
            keys = Api.getInstance().get(DB_USERS).keys()
            for key in keys :
                if self.get_field(key+"-delete"):
                    Api.getInstance().rm(DB_USERS, key)
                else:
                    Api.getInstance().set(DB_USERS, key, "firstname", data=self.get_field(key+"-firstname"))
                    Api.getInstance().set(DB_USERS, key, "lastname", data=self.get_field(key+"-lastname"))
                    Api.getInstance().set(DB_USERS, key, "privilege","terminal", data=self.get_field(key+"-privilege-terminal"))
                    Api.getInstance().set(DB_USERS, key, "privilege","manage",data=self.get_field(key+"-privilege-manage"))
                    Api.getInstance().set(DB_USERS, key, "privilege","edit",data=self.get_field(key+"-privilege-edit"))
                    passwd = self.get_field(key+"-password")
                    if passwd != "":
                        Api.getInstance().set(DB_USERS, key, "password",data=hashlib.sha256(passwd.encode()).hexdigest())
        self.destroy()
        Api.getInstance().reset()


