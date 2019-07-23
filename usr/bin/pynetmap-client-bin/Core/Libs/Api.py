#!/usr/bin/env python
__author__ = 'Samir KHERRAZ'
__copyright__ = '(c) Samir HERRAZ 2018-2019'
__version__ = '1.2.0'
__licence__ = 'GPLv3'


import hashlib
import json
from threading import Thread
import requests
from Core.Libs.Config import Config
class Api:

    __INSTANCE__ =None

    def __init__(self):
        self.last_update = -1
        self.cookies = None
        self.session = requests.Session()
        self.session.verify = True
        self.reset()

    def __post(self, ressource, data={}, timeout=None):
            ret = self.session.post(self.url+ressource, cookies=self.cookies,  json=json.dumps(data), timeout=timeout).json()
            status=ret["status"]
            content=""
            data=""
            if status == "OK":
                try:
                    content=ret["content"]
                    return content
                except:
                    return None
            else:
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
            self.__post(self.url+"ping", None, 1)
            return True
        except:
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

    def get(self, *args):
        data = self.__post("data/get/"+"/".join(args))
        try:
            if not data["AUTHORIZATION"]:
                return None
        except:
            return data


    def find(self,table, value, attr=None):
        if attr != None:
            url ="data/find/attr/"+table+"/"+attr+"/"+value
        else:
            url = "data/find/attr/"+table+"/"+value

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

    def delete(self, newid):    
        url = "data/delete/"+newid
        self.__post(url)

    def move(self, id, newparent):
        self.__post("data/move/"+id+"/"+newparent)


    def set(self, *args, data):
        self.__post("data/set/"+"/".join(args),data)
    
    def rm(self, *args):
        self.__post("data/rm/"+"/".join(args))


    def cleanup(self):
        self.__post("data/cleanup/")

    
    @staticmethod
    def getInstance():
        if Api.__INSTANCE__ is None:
            Api.__INSTANCE__ = Api()
        return Api.__INSTANCE__