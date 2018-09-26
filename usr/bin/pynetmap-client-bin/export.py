#!/usr/bin/env python
__author__ = 'Samir KHERRAZ'
__copyright__ = '(c) Samir HERRAZ 2018-2018'
__version__ = '1.1.0'
__licence__ = 'GPLv3'

import os


class Export:
    def __init__(self, base):
        self.store = base

        self.filesystem = open("/tmp/export-"+str(os.getuid())+".md", "w")
        st = ""
        elm = self.store.head()
        for k in elm:
            st += self.write(elm[k], 0)
        self.filesystem.write(st)
        self.filesystem.close()
        os.system("xdg-open /tmp/export-"+str(os.getuid())+".md &")

    def writeNode(self, el, spc):
        s = "___ \n"
        s += spc+" "+el["base.core.schema"]+" - "+el["base.name"]+"\n"
        hidden = ["base.ssh.password", "base.core.schema", "base.ssh.user", "base.ssh.port",
                  "base.tunnel.user", "base.tunnel.password", "base.tunnel.port"]
        for key in el:
            if key in hidden:
                pass
            else:
                s += "  - "+key + " : "
                if "\n" in str(el[key]):
                    s += "\n"+"\t"
                s += str(el[key]).replace("\n", "\n"+"\t")+"\n"
        return s

    def write(self, node, lvl):
        spc = ""
        i = 0
        while i < lvl:
            spc += "#"
            i += 1
        if spc == "":
            spc = "#"
        st = self.writeNode(node, spc)
        for k in node["base.core.children"]:
            st += self.write(node["base.core.children"][k], lvl+2)
        return st
