#!/usr/bin/env python
__author__ = 'Samir KHERRAZ'
__copyright__ = '(c) Samir HERRAZ 2018-2019'
__version__ = '1.2.0'
__licence__ = 'GPLv3'

import configparser

from Constants import *


class Lang():

    __INSTANCE__ =None

    def __init__(self, lang):
        self.configuration = configparser.ConfigParser()
        self.file = "/etc/pynetmap-client/langs.conf"
        self.lang = lang

    def read(self):
        with open(self.file, "r") as fp:
            self.configuration.readfp(fp)

    def get(self, key):
        try:
            return self.configuration.get(self.lang, key)
        except:
            try:
                return self.configuration.get("DEFAULT", key)
            except:
                return key
    

    @staticmethod
    def getInstance(lang="DEFAULT"):
        if Lang.__INSTANCE__ is None:
            Lang.__INSTANCE__ = Lang(lang)
            Lang.__INSTANCE__.read()
        return Lang.__INSTANCE__