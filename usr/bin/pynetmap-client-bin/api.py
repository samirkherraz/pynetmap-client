#!/usr/bin/env python
__author__ = 'Samir KHERRAZ'
__copyright__ = '(c) Samir HERRAZ 2018-2018'
__version__ = '1.1.0'
__licence__ = 'GPLv3'


import hashlib
import json
from threading import Thread

import requests

from dialog import Notify


class API:
    def __init__(self, ui):
        self.ui = ui
        self.last_update = -1
        self.cookies = None
        self.session = requests.Session()
        self.session.verify = True
        self.reset()

    def reset(self):
        self.url = self.ui.config.get("server")+"/"

    def tunnel_relaod(self):
        self.session.post(self.url+"core/tunnel/reload",
                          json=json.dumps(self.d))

    def auth_user(self, username, password):
        self.d = dict()
        self.d["username"] = username
        self.d["password"] = hashlib.sha256(password.encode()).hexdigest()
        return self.auth()

    def is_server_online(self):
        try:
            self.session.post(self.url, timeout=1)
            return True
        except ValueError as e:
            print(e)
            return False

    def get_access(self, prop):
        t = self.session.post(self.url+"core/auth/access/"+prop,
                              cookies=self.cookies).json()["content"]
        return t["AUTHORIZATION"]

    def auth(self):
        t = self.session.post(self.url+"core/auth/login",
                              json=json.dumps(self.d)).json()["content"]
        if t["TOKEN"] != None:
            self.cookies = {"TOKEN": t["TOKEN"],
                            "USERNAME": self.d["username"]}
            Notify(self.ui.lang.get("Gtk.notify.connection.success.title"),
                   self.ui.lang.get("Gtk.notify.connection.success.text"))
            return True
        Notify(self.ui.lang.get("Gtk.notify.connection.fail.title"),
               self.ui.lang.get("Gtk.notify.connection.fail.text"))

        return False

    def auth_check(self):

        t = self.session.post(self.url+"core/auth/check",
                              cookies=self.cookies).json()["content"]
        print(t)
        try:
            return t["AUTHORIZATION"]
        except:
            return False

    def get_table(self, table):
        data = self.session.post(self.url+"core/data/get/"+table,
                                 cookies=self.cookies).json()["content"]
        try:
            if not data["AUTHORIZATION"]:
                return None
        except:
            return data

    def get(self, table, id):
        data = self.session.post(self.url+"core/data/get/"+table+"/"+id,
                                 cookies=self.cookies).json()["content"]
        try:
            if not data["AUTHORIZATION"]:
                return None
        except:
            return data

    def set(self, table, id, store):
        self.session.post(self.url+"core/data/set/"+table+"/"+id, json=json.dumps(store),
                          cookies=self.cookies)

    def get_attr(self, table, id, attr):
        data = self.session.post(self.url+"core/data/get/"+table+"/"+id+"/"+attr,
                                 cookies=self.cookies).json()["content"]
        try:
            if not data["AUTHORIZATION"]:
                return None
        except:
            return data

    def find_attr(self, value, attr=None):
        if attr != None:
            url = self.url+"core/data/find/attr/"+attr+"/"+value
        else:
            url = self.url+"core/data/find/attr/"+value

        data = self.session.post(url,
                                 cookies=self.cookies).json()["content"]
        try:
            if not data["AUTHORIZATION"]:
                return None
        except:
            return data

    def find_schema(self, value):
        data = self.session.post(self.url+"core/data/find/schema/"+value,
                                 cookies=self.cookies).json()["content"]
        try:
            if not data["AUTHORIZATION"]:
                return None
        except:
            return data

    def find_path(self, value):
        data = self.session.post(self.url+"core/data/find/path/"+value,
                                 cookies=self.cookies).json()["content"]
        try:
            if not data["AUTHORIZATION"]:
                return None
        except:
            return data

    def find_children(self, value):
        data = self.session.post(self.url+"core/data/find/children/"+value,
                                 cookies=self.cookies).json()["content"]
        try:
            if not data["AUTHORIZATION"]:
                return None
        except:
            return data

    def find_parent(self, value):
        data = self.session.post(self.url+"core/data/find/parent/"+value,
                                 cookies=self.cookies).json()["content"]
        try:
            if not data["AUTHORIZATION"]:
                return None
        except:
            return data["Parent"]

    def create(self, parent_id=None, newid=None):

        if parent_id != None:
            if newid != None:
                url = self.url+"core/data/create/"+parent_id+"/"+newid
            else:
                url = self.url+"core/data/create/"+parent_id
        else:
            url = self.url+"core/data/create/"

        data = self.session.post(url,
                                 cookies=self.cookies).json()["content"]
        try:
            if not data["AUTHORIZATION"]:
                return None
        except:
            return data["ID"]

    def delete(self, parent_id=None, newid=None):

        if parent_id != None and newid != None:
            url = self.url+"core/data/delete/"+parent_id+"/"+newid
        elif newid != None:
            url = self.url+"core/data/delete/"+newid
        else:
            return

        self.session.post(url,
                          cookies=self.cookies)

    def move(self, id, newparent):
        self.session.post(self.url+"core/data/move/"+id+"/"+newparent,
                          cookies=self.cookies)

    def set_attr(self, table, id, attr, store):

        self.session.post(self.url+"core/data/set/"+table+"/"+id+"/"+attr, json=json.dumps(store),
                          cookies=self.cookies)

    def set_table(self, table, store):
        self.session.post(self.url+"core/data/set/"+table, json=json.dumps(store),
                          cookies=self.cookies)

    def cleanup(self):
        self.session.post(self.url+"core/data/cleanup/",
                          cookies=self.cookies)
