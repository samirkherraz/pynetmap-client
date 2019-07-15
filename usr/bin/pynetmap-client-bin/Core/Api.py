#!/usr/bin/env python
__author__ = 'Samir KHERRAZ'
__copyright__ = '(c) Samir HERRAZ 2018-2019'
__version__ = '1.2.0'
__licence__ = 'GPLv3'


import hashlib
import json
from threading import Thread
import requests
from Core.Config import Config
class API:

    __INSTANCE__ =None

    def __init__(self):
        self.last_update = -1
        self.cookies = None
        self.session = requests.Session()
        self.session.verify = True
        self.reset()

    def __post(self, ressource, data={}):
            ret = self.session.post(self.url+ressource, cookies=self.cookies,  json=json.dumps(data)).json()
            print(ressource)
            status=ret["status"]
            content=""
            data=""
            if status == "OK":
                try:
                    content=ret["content"]
                    return content
                except:
                    print(ret)
                    return None
            else:
                print(data)
                print(content)
                return None
    def reset(self):
        self.url= Config.getInstance().get("server")+"/"


    def auth_user(self, username, password):
        self.d=dict()
        self.d["username"]=username
        self.d["password"]=hashlib.sha256(password.encode()).hexdigest()
        return self.auth()

    def is_server_online(self):
        try:
            self.__post(self.url+"ping")
            return True
        except Exception as e:
            print(e)
            return False

    def get_access(self, prop):
        t=self.__post("auth/access/"+prop)
        return t["AUTHORIZATION"]

    def auth(self):
        t=self.__post("auth/login", self.d)
        if t["TOKEN"] is not None:
            self.cookies={"TOKEN": t["TOKEN"],
                            "USERNAME": self.d["username"]}
            return True
        return False

    def auth_check(self):
        try:
            t = self.__post("auth/check")
            try:
                return t["AUTHORIZATION"]
            except:
                return False
        except:
            return False

    def get_table(self, table):
        data = self.__post("data/get/"+table)
        try:
            if not data["AUTHORIZATION"]:
                return None
        except:
            return data

    def get(self, table, id, attr=None):
        ressource = "data/get/"+table+"/"+id
        if attr is not None:
            ressource += "/"+attr
        data = self.__post(ressource)
        try:
            if not data["AUTHORIZATION"]:
                return None
        except:
            return data

    def set(self, table, id, store):
        self.__post("data/set/"+table+"/"+id,store)


    def find_attr(self, value, attr=None):
        if attr != None:
            url ="data/find/attr/"+attr+"/"+value
        else:
            url = "data/find/attr/"+value

        data = self.__post(url)
        try:
            if not data["AUTHORIZATION"]:
                return None
        except:
            return data


    def find_path(self, value):
        data = self.__post("data/find/path/"+value)
        try:
            if not data["AUTHORIZATION"]:
                return None
        except:
            return data

    def find_children(self, value):
        data = self.__post("data/find/children/"+value)
        try:
            if not data["AUTHORIZATION"]:
                return None
        except:
            return data

    def find_parent(self, value):
        data = self.__post("data/find/parent/"+value)
        try:
            if not data["AUTHORIZATION"]:
                return None
        except:
            return data["Parent"]

    def create(self, parent_id=None, newid=None):

        if parent_id != None:
            if newid != None:
                url = "data/create/"+parent_id+"/"+newid
            else:
                url = "data/create/"+parent_id
        else:
            url = "data/create/"

        data = self.__post(url)
    
        try:
            if not data["AUTHORIZATION"]:
                return None
        except:
            return data["ID"]

    def delete(self, parent_id=None, newid=None):

        if parent_id != None and newid != None:
            url = "data/delete/"+parent_id+"/"+newid
        elif newid != None:
            url = "data/delete/"+newid
        else:
            return

        self.__post(url)

    def move(self, id, newparent):
        self.__post("data/move/"+id+"/"+newparent)

    def set_attr(self, table, id, attr, store):

        self.__post("data/set/"+table+"/"+id+"/"+attr, store)

    def set_table(self, table, store):
        self.__post("data/set/"+table, store)

    def cleanup(self):
        self.__post("data/cleanup/")

    
    @staticmethod
    def getInstance():
        if API.__INSTANCE__ is None:
            API.__INSTANCE__ = API()
        return API.__INSTANCE__