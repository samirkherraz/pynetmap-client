import requests
from database import Database
import json
from threading import Thread, Lock, Event
from dialog import Ask, Error, Notify
import hashlib
import gtk
import gobject


class APIDaemon(Thread):
    def __init__(self, ui):
        Thread.__init__(self)
        self.ui = ui
        self._stop = Event()
        self.setDaemon(True)
        self.last_update = -1
        self.cookies = None
        self.session = requests.Session()
        self.session.verify = False
        self.reset()

    def reset(self):
        self.url = "https://" + \
            self.ui.config.get("ServerIP")+":" + \
            self.ui.config.get("ServerPort")+"/"

    def reload(self):
        self.session.post(
            self.url+"reload", cookies=self.cookies).json()
        self.state_check()

    def state_check(self):
        t = self.session.post(
            self.url+"state_check", json=json.dumps({"TIMESTAMP": self.last_update}), cookies=self.cookies).json()
        self.last_update = t["TIMESTAMP"]
        print t["ACTIONS"]
        return t["ACTIONS"]

    def auth_user(self, username, password):
        self.d = dict()
        self.d["username"] = username
        self.d["password"] = hashlib.sha256(password).hexdigest()
        return self.auth()

    def is_server_online(self):
        try:
            self.session.post(self.url)
            return True
        except:
            return False

    def auth(self):
        t = self.session.post(self.url+"auth", json=json.dumps(self.d)).json()
        if t["TOKEN"] != None:
            self.cookies = {"TOKEN": t["TOKEN"]}
            Notify("Connection succeded",
                   "You have been connected to the server")
            return True
        Notify("Connection Failed",
               "please try to connect later")
        return False

    def auth_check(self):

        t = self.session.post(self.url+"auth_check",
                              cookies=self.cookies).json()
        try:
            return t["AUTHORIZATION"]
        except:
            return False

    def pull_data(self):
        data = self.session.post(self.url+"pull_data",
                                 cookies=self.cookies).json()
        try:
            if not data["AUTHORIZATION"]:
                return None
        except:
            return data

    def pull_schema(self):
        data = self.session.post(self.url+"pull_schema",
                                 cookies=self.cookies).json()
        try:
            if not data["AUTHORIZATION"]:
                return None
        except:
            return data

    def push_data(self, store):
        data = self.session.post(self.url+"push_data", json=json.dumps(store.head()),
                                 cookies=self.cookies).json()
        try:
            if not data["AUTHORIZATION"]:
                return None
        except:
            return data

    def push_schema(self, store):
        data = self.session.post(self.url+"push_schema", json=json.dumps(store.head()),
                                 cookies=self.cookies).json()
        try:
            if not data["AUTHORIZATION"]:
                return None
        except:
            return data

    def run(self):
        while not self._stop.isSet():
            try:
                actions = self.state_check()
                if "AUTH" in actions:
                    Notify("Invalid Access Token",
                           "You have been disconnected from the server \n Reconnecting ...")
                    self.auth()
                    raise Exception("AUTH")
                if "DATA" in actions:
                    data = self.pull_data()
                    if data != None:
                        self.ui.store.replace_data(data)
                        gobject.idle_add(self.ui.refresh,
                                         priority=gobject.PRIORITY_HIGH)
                if "SCHEMA" in actions:
                    data = self.pull_schema()
                    if data != None:
                        self.ui.store.replace_schema(data)
                        gobject.idle_add(self.ui.refresh,
                                         priority=gobject.PRIORITY_HIGH)
            except:
                pass
            self._stop.wait(15)

    def stop(self):
        self._stop.set()
        self.join()
