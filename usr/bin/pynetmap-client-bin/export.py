#!/usr/bin/env python
__author__ = 'Samir KHERRAZ'
__copyright__ = '(c) Samir HERRAZ 2018-2018'
__version__ = '1.1.0'
__licence__ = 'GPLv3'

import os


class Export:
    def __init__(self, parent):
        self.store = parent.store
        self.lang = parent.lang

        self.filesystem = open("/tmp/export-"+str(os.getuid())+".md", "w")
        st = self.write(self.store.get_table("structure"), 0)
        self.filesystem.write(st)
        self.filesystem.close()
        os.system("xdg-open /tmp/export-"+str(os.getuid())+".md &")

    def writeNode(self, key, spc):
        el = self.store.get("base", key)
        s = "\n"
        s += spc+" "+el["base.core.schema"]+" - "+el["base.name"]+"\n"
        hidden = ["base.ssh.password", "base.core.schema", "base.name", "base.ssh.user", "base.ssh.port",
                  "base.tunnel.user", "base.tunnel.password", "base.tunnel.port"]
        for key in el:
            if key in hidden:
                pass
            else:
                s += "  - "+self.lang.get(key) + " : "
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
            st += self.writeNode(k, spc)
            st += self.write(node[k], lvl+2)
        return st
