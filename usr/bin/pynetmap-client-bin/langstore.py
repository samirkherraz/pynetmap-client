#!/usr/bin/env python
__author__ = 'Samir KHERRAZ'
__copyright__ = '(c) Samir HERRAZ 2018-2019'
__version__ = '1.2.0'
__licence__ = 'GPLv3'

import configparser

from const import CONFIG_PATH


class LangStore():
    def __init__(self, config):
        self.configuration = configparser.ConfigParser()
        self.file = "/etc/pynetmap-client/langs.conf"
        self.config = config

    def read(self):
        with open(self.file, "r") as fp:
            self.configuration.readfp(fp)

    def get(self, key):
        try:
            return self.configuration.get(self.config.get("Language"), key)
        except:
            try:
                return self.configuration.get("DEFAULT", key)
            except:
                return key
