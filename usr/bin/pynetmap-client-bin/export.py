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
        os.system("xdg-open /tmp/export-"+str(os.getuid())+".md")

    def writeNode(self, el, spc):
        s = "___ \n"
        s += spc+" "+el["__SCHEMA__"]+" - "+el["__ID__"]+"\n"
        hidden = ["__ID__", "Password", "__SCHEMA__", "__CHILDREN__", "User", "Password",
                  "Tunnel Password", "Tunnel User", "Tunnel SSH Port", "Uptime", "CPU Usage", "Status"]
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
        for k in node["__CHILDREN__"]:
            st += self.write(node["__CHILDREN__"][k], lvl+2)
        return st
