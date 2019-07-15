#!/usr/bin/env python
__author__ = 'Samir KHERRAZ'
__copyright__ = '(c) Samir HERRAZ 2018-2019'
__version__ = '1.2.0'
__licence__ = 'GPLv3'

import configparser
import os
from shutil import copyfile

from gi.repository import Gtk, Gdk, GLib

from const import CONFIG_PATH
from dialog import Config


class ConfigStore():
    def __init__(self, ui):
        self.ui = ui
        if not os.path.isfile(CONFIG_PATH):
            copyfile("/etc/pynetmap-client/global.conf", CONFIG_PATH)
        self.configuration = configparser.ConfigParser()
        self.file = CONFIG_PATH

    def check(self):
        cfg = Config(self.ui)
        for (k, _) in self.configuration.items("GLOBAL"):
            cfg.set_field(k, self.get(k))
        result = cfg.run()
        if result == Gtk.ResponseType.OK:
            for (k, _) in self.configuration.items("GLOBAL"):
                self.set(k, cfg.get_field(k))
            self.write()
        cfg.destroy()

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
