#!/usr/bin/env python
__author__ = 'Samir KHERRAZ'
__copyright__ = '(c) Samir HERRAZ 2018-2019'
__version__ = '1.2.0'
__licence__ = 'GPLv3'

import os
from Constants import *
from Core.Libs.Api import Api
from Core.Libs.Lang import Lang

class MDExport:
    def __init__(self):
       
        self.filesystem = open("/tmp/export-"+str(os.getuid())+".md", "w")
        st = self.write(Api.getInstance().get("structure"), 0)
        self.filesystem.write(st)
        self.filesystem.close()
        os.system("xdg-open /tmp/export-"+str(os.getuid())+".md &")

    def write_node(self, key, spc):
        el = Api.getInstance().get(DB_BASE , key)
        s = "\n"
        s += spc+" "+el[KEY_TYPE]+" - "+el[KEY_NAME]+"\n"
        hidden = [KEY_SSH_PASSWORD, KEY_TYPE, KEY_NAME, KEY_SSH_USER, KEY_SSH_PORT,
                  KEY_TUNNEL_IP, KEY_TUNNEL_PASSWORD, KEY_TUNNEL_PORT, KEY_TUNNEL_USER]
        for key in el:
            if key in hidden:
                pass
            else:
                s += "  - "+Lang.getInstance().get(key) + " : "
                if "\n" in str(el[key]):
                    s += "\n"+'```\n'
                    s += str(el[key])
                    s += "\n"+'```'
                else:
                    s += str(el[key])
                s += "\n"
        return s

    def write(self, node, lvl):
        spc = ""
        i = 0
        while i < lvl:
            spc += "#"
            i += 1
        if spc == "":
            spc = "#"
        st = ""
        for k in node:
            st += self.write_node(k, spc)
            st += self.write(node[k], lvl+2)
        return st
