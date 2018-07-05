#!/usr/bin/python
import os
import gtk


class Graph:
    def __init__(self, database):
        self.store = database
        self.header = "Digraph{ \nnode [style=\"filled, rounded\",fillcolor=\"#eeeeee\",fontname=\"Sans\", fixedsize=false,shape=plaintext];\ngraph [splines=\"true\", dpi = 128, pad=\"1\", ranksep=\"1\",nodesep=\"0.5\"]\n"
        self.footer = "}"
        self.format = "png"

    def edge(self, a, b, lvl=0):
        i = 0
        s = "\t"
        while i < lvl:
            s += "\t"
            i += 1
        s += "\""+str(a)+"\" -> \""+str(b)+"\" \n"
        return s

    def calldot(self, filecontent):
        file = open("/tmp/graph.dot", "w")
        file.write(filecontent)
        file.close()
        os.system("dot -T"+self.format +
                  " /tmp/graph.dot -o  /tmp/graph."+self.format + "; exit")
        r = gtk.gdk.pixbuf_new_from_file("/tmp/graph."+self.format)
        # os.remove("/tmp/graph.dot")
        os.remove("/tmp/graph."+self.format)
        return r

    def node(self, key, vm, detailed, lvl=0):
        icon = self.store.schema()[vm["__SCHEMA__"]]["Icon"]+".png"
        try:
            if vm["Status"] == "running":
                icon = self.store.schema(
                )[vm["__SCHEMA__"]]["Icon"]+"_running.png"
            elif vm["Status"] == "stopped":
                icon = self.store.schema(
                )[vm["__SCHEMA__"]]["Icon"]+"_stopped.png"
            elif vm["Status"] == "unknown":
                icon = self.store.schema(
                )[vm["__SCHEMA__"]]["Icon"]+"_unknown.png"
        except:
            pass
        s = "\t"
        i = 0
        while i < lvl:
            s += "\t"
            i += 1
        s += "\""+str(key)+"\" "
        s += " [label=<<TABLE border='0' cellborder='0' cellspacing='5'>"
        s += "<TR><TD port='IMG' colspan='2'><IMG SRC='"+icon+"' /></TD></TR>"
        s += "<TR><TD colspan='2' ><b>" + \
            str(vm["__ID__"])+"</b></TD></TR>"
        if detailed:
            i = 0
            keylist = vm.keys()
            keylist.sort()
            for k in keylist:
                i += 1
                if (not k.startswith("__")) and (vm[k] != ""):
                    if "Password" in k:
                        rst = "*" * len(str(vm[k]))
                    else:
                        rst = str(vm[k])
                    rst = rst.replace('"', '\"')
                    rst = rst.replace('\n', "<BR ALIGN='LEFT'/>")
                    s += "<TR><TD VALIGN='TOP' ALIGN='LEFT'><B>"+k + \
                        "</B></TD><TD VALIGN='TOP' ALIGN='LEFT'>" + rst+"</TD></TR>"
        s += "</TABLE>>]\n"
        return s

    def generate_node_recur(self, key, node, detailed, lvl):
        st = self.node(key, node, detailed, lvl)
        for k in node["__CHILDREN__"]:
            st += self.generate_node_recur(k,
                                           node["__CHILDREN__"][k], detailed, lvl+1)
            st += self.edge(key, k, lvl+1)
        return st

    def generate(self, elm):
        st = self.header
        k = self.store.head()
        lo = None
        i = 0
        for o in reversed(elm):
            el = k[o]
            i += 1
            if i < len(elm):
                st += self.node(o, el, False)

            else:
                st += self.node(o, el, True)
            if lo != None:
                st += self.edge(lo, o)
            lo = o
            k = el["__CHILDREN__"]

        for o in k:
            st += self.generate_node_recur(o, k[o], False, 1)
            st += self.edge(lo, o, 1)

        st += self.footer
        return self.calldot(st)

    def generate_all_map(self):
        st = self.header
        elm = self.store.head()
        for k in elm:
            st += self.generate_node_recur(k, elm[k], False, 0)

        st += self.footer
        return self.calldot(st)
