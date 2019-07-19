#!/usr/bin/env python
__author__ = 'Samir KHERRAZ'
__copyright__ = '(c) Samir HERRAZ 2018-2019'
__version__ = '1.2.0'
__licence__ = 'GPLv3'

import configparser
import os
from shutil import copyfile
from gi.repository import Gtk, Gdk, GLib

from Constants import *

class Config():

    __INSTANCE__ =None


    def __init__(self):
        if not os.path.isfile(CONFIG_PATH):
            copyfile("/etc/pynetmap-client/global.conf", CONFIG_PATH)
        self.configuration = configparser.ConfigParser()
        self.file = CONFIG_PATH

    def read(self):
        with open(self.file, "r") as fp:
            self.configuration.readfp(fp)

    def write(self):
        with open(self.file, "w") as fp:
            self.configuration.write(fp)

    def get(self, key):
        return self.configuration.get("GLOBAL", key)

    def set(self, key, value):
        self.configuration.set("GLOBAL", key, value)

    def items(self):
        return self.configuration.items("GLOBAL")

    @staticmethod
    def getInstance():
        if Config.__INSTANCE__ is None:
            Config.__INSTANCE__ = Config()
            Config.__INSTANCE__.read()
        return Config.__INSTANCE__