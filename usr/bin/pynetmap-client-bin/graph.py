#!/usr/bin/python
import os
import gtk


class Graph:
    def __init__(self, database):
        try:
            os.mkdir("/tmp/pynetmap/")
        except:
            pass
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
        file = open("/tmp/pynetmap/graph.dot", "w")
        file.write(filecontent)
        file.close()
        os.system("dot -T"+self.format +
                  " /tmp/pynetmap/graph.dot -o  /tmp/pynetmap/graph."+self.format + "; exit")
        r = gtk.gdk.pixbuf_new_from_file("/tmp/pynetmap/graph."+self.format)
        #os.system("rm /tmp/pynetmap/*")
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
            schema = self.store.schema()[vm["__SCHEMA__"]]["Fields"]
            keylist = vm.keys()
            keylist.sort()
            table = []
            table.append([])  # 0
            table.append([])  # 1
            table.append([])  # 2
            for k in keylist:
                if (not k.startswith("__")) and (vm[k] != ""):
                    if "Password" in str(k):
                        rst = "*" * len(str(vm[k]))
                        table[1].append(k)
                    elif type(vm[k]) is list:
                        table[0].append(k)
                    elif "\n" in str(vm[k]) or ("|" in str(vm[k])) or (k in schema and schema[k] == "LONG"):
                        table[2].append(k)
                    else:
                        table[1].append(k)
            tbl0b = False
            tbl1b = False
            tbl2b = False
            tbl0 = "<TABLE border='0' cellborder='0' cellspacing='5'>"
            for k in table[0]:
                name = (vm["__ID__"]+k+".png").replace(" ", "").lower()
                self.subgraph(vm[k], name, k)

                tbl0 += "<TR><TD VALIGN='TOP' ALIGN='LEFT'><IMG SRC='/tmp/pynetmap/" + \
                    name+"' /></TD></TR>"
                tbl0b = True
            tbl0 += "</TABLE>"

            tbl1 = "<TABLE border='0' cellborder='0' cellspacing='5'>"
            for k in table[1]:
                if "Password" in k:
                    rst = "*" * len(str(vm[k]))
                else:
                    rst = str(vm[k])
                    rst = rst.replace('"', '\"')
                tbl1 += "<TR><TD VALIGN='TOP' ALIGN='LEFT'><B>"+k + \
                    "</B></TD><TD VALIGN='TOP' ALIGN='LEFT'>"+rst + "</TD></TR>"
                tbl1b = True
            tbl1 += "</TABLE>"

            tbl2 = "<TABLE border='0' cellborder='0' cellspacing='5'>"
            for k in table[2]:
                rst = str(vm[k])
                rst = rst.replace('"', '\"')

                tbl2 += "<TR><TD VALIGN='TOP' ALIGN='LEFT'>"

                tbl2 += "<TABLE border='0' cellborder='0' cellspacing='5'><TR><TD ALIGN='LEFT'><B><U>" + \
                    k+"</U></B></TD></TR>"

                for l in rst.split("\n"):
                    tbl2 += "<TR>"
                    for d in l.split("|"):
                        tbl2 += "<TD VALIGN='TOP' ALIGN='LEFT'>"+d.strip()+"</TD>"
                    tbl2 += "</TR>"
                tbl2 += "</TABLE>"
                tbl2 += "</TD></TR>"
                tbl2b = True
            tbl2 += "</TABLE>"

            if tbl0b and tbl1b:
                s += "<TR><TD VALIGN='TOP' ALIGN='LEFT'>"+tbl0 + \
                    "</TD><TD VALIGN='TOP' ALIGN='LEFT'>"+tbl1+"</TD></TR>"
            elif tbl0b:
                s += "<TR><TD VALIGN='TOP' ALIGN='LEFT' colspan='2'>"+tbl0 + "</TD></TR>"
            elif tbl1b:
                s += "<TR><TD VALIGN='TOP' ALIGN='LEFT' colspan='2'>"+tbl1 + "</TD></TR>"
            if tbl2b:
                s += "<TR><TD VALIGN='TOP' ALIGN='LEFT' colspan='2'>"+tbl2 + "</TD></TR>"

        s += "</TABLE>>]\n"
        return s

    def subgraph(self, list, name, title):
        i = 0
        file = open("/tmp/pynetmap/"+name+".list", "w")
        for e in list:
            ee = str(e).replace("[^0-9.]+", "").replace("%", "")
            if ee != "":
                ee = float(ee)
                if ee < 25:
                    color = 0
                elif ee < 75:
                    color = 1
                else:
                    color = 2

                file.write(str(i) + "    "+str(ee) +
                           "    " + str(color) + "\n")
                i = i+1
        file.close()

        cmd = """gnuplot -e "set terminal png size 500,250 font arial 12 enhanced;
        set title "";
        set yrange [0:100];
        set style line 1 linewidth 5 pointtype 7 pointsize 1.5 ;
        set colorbox;
        set palette model RGB maxcolors 3;
        set palette model RGB defined (0 '#999900', 1 '#009900', 2 '#cc0000');
        set cbrange [0:2];
        plot '/tmp/pynetmap/""" + name+""".list' title '"""+title+"""' with lines linestyle 1 palette ;" > /tmp/pynetmap/""" + name+""" && rm '/tmp/pynetmap/"""+name+""".list'"""
        os.system(cmd)

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
