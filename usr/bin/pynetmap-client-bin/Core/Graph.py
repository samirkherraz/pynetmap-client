#!/usr/bin/env python
__author__ = 'Samir KHERRAZ'
__copyright__ = '(c) Samir HERRAZ 2018-2019'
__version__ = '1.2.0'
__licence__ = 'GPLv3'

import os
import time
import getpass
from datetime import datetime, timedelta
from Constants import *
from gi.repository import Gtk, Gdk, GLib,GdkPixbuf
from Core.Api import API
from Core.Lang import Lang
class Graph:
    def __init__(self):
        self.format = "jpeg"
        self.tmppath = "/tmp/.pynetmap-"+getpass.getuser()+"/"
        self.tmpfile = self.tmppath+"graph.dot"
        self.tmpfilefmt = self.tmppath+"graph."+self.format

        print(self.tmppath)
        try:
            os.mkdir(self.tmppath)
        except:
            pass
        self.header = "Digraph{ \nnode [style=\"filled, rounded\",fillcolor=\"#eeeeee\",fontname=\"Sans\", fixedsize=false,shape=plaintext];\ngraph [splines=\"line\", dpi = 196, pad=\"1\", ranksep=\"1\",nodesep=\"0.5\"]\n"
        self.footer = "}"

    def edge(self, a, b, lvl=0):
        i = 0
        s = "\t"
        while i < lvl:
            s += "\t"
            i += 1
        s += "\""+str(a)+"\" -> \""+str(b)+"\" \n"
        return s

    def calldot(self, filecontent):
        file = open(self.tmpfile, "w")
        file.write(filecontent)
        file.close()
        os.system("dot -T"+self.format +
                  " "+self.tmpfile+" -o  "+self.tmpfilefmt + "; exit")
        r = GdkPixbuf.Pixbuf.new_from_file(self.tmpfilefmt)
        os.system("rm "+ self.tmppath+"*")
        return r

    def node(self, key, detailed, lvl=0):
        base = API.getInstance().get(DB_BASE, key)
        if base is None:
            base = {}
        info = API.getInstance().get(DB_MODULE, key)
        if info is None:
            info = {}
        vmstate = info.get(KEY_STATUS)

        vmicon = self.tmpschema.get(base.get(KEY_TYPE)).get("Icon")

        vmname = base.get(KEY_NAME)

        icon = vmicon+".png"
        try:
            if vmstate == RUNNING_STATUS:
                icon = vmicon+"_running.png"
            elif vmstate == STOPPED_STATUS:
                icon = vmicon+"_stopped.png"
            elif vmstate == UNKNOWN_STATUS:
                icon = vmicon+"_unknown.png"
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
        s += "<TR><TD colspan='2' ><b>" + vmname+"</b></TD></TR>"
        if detailed:
            vmfields = self.tmpschema.get(base.get(KEY_TYPE)).get("Fields", [])
            
            table = dict()
            table["base"] = []
            table["baseinfo"] = []
            table["basemultiline"] = []
            for k in base:
                    if k in vmfields.keys() and vmfields[k] == "LONG":
                        table["basemultiline"].append(k)
                    else:
                        table["base"].append(k)

            try:
                for k in info.keys():
                    if (info[k] != "" and type(info[k]) == str):
                       table["baseinfo"].append(k)
                        
            except:
                pass
            tblhistoryb = False
            tblbaseb = False
            tbllistb = False

            for k in table:
                table[k].sort()

            # History
            tblhistory = "<TABLE border='0' cellborder='0' cellspacing='5'>"
            if KEY_MONITOR_HISTORY in info:
                for k in info.get(KEY_MONITOR_HISTORY, []):
                    
                    name = (vmname+k+".png").replace(" ", "").lower()
                    self.subgraph(info.get(KEY_MONITOR_HISTORY).get(k), name, Lang.getInstance().get(k), (k == KEY_STATUS) )
                    tblhistory += "<TR><TD VALIGN='TOP' ALIGN='LEFT'><IMG SRC='/tmp/pynetmap/" + \
                        name+"' /></TD></TR>"
                    tblhistoryb = True
            tblhistory += "</TABLE>"
            # Base
            tblbase = "<TABLE border='0' cellborder='0' cellspacing='5'>"
            for k in table["base"]:
                if ".password" in k:
                    rst = "*" * len(str(base.get(k)))
                else:
                    rst = str(base.get(k))
                    rst = rst.replace('"', '\"')
                tblbase += "<TR><TD VALIGN='TOP' ALIGN='LEFT'><B>"+Lang.getInstance().get(k) + \
                    "</B></TD><TD VALIGN='TOP' ALIGN='LEFT'>"+rst + "</TD></TR>"
                tblbaseb = True
            for k in table["baseinfo"]:
                if k == KEY_LAST_UPDATE:
                    rst = "-" + \
                        str(timedelta(seconds=int(time.time() - info.get(k))))
                else:
                    rst = str(info.get(k))
                    rst = rst.replace('"', '\"')
                tblbase += "<TR><TD VALIGN='TOP' ALIGN='LEFT'><B>"+Lang.getInstance().get(k) + \
                    "</B></TD><TD VALIGN='TOP' ALIGN='LEFT'>"+rst + "</TD></TR>"
                tblbaseb = True
            for k in table["basemultiline"]:
                rst = str(base.get(k))
                rst = rst.replace('\n', "<BR ALIGN='LEFT'/>")
                tblbase += "<TR><TD VALIGN='TOP' ALIGN='LEFT'><B>"+Lang.getInstance().get(k) + \
                    "</B></TD><TD VALIGN='TOP' ALIGN='LEFT'>"+rst + "</TD></TR>"
                tblbaseb = True

            tblbase += "</TABLE>"

            # List
            tbllist = "<TABLE border='0' cellborder='0' cellspacing='5'>"
            if KEY_MONITOR_LISTS in info:
                for k in info.get(KEY_MONITOR_LISTS):
                    rst = info.get(KEY_MONITOR_LISTS).get(k)
                    if len(rst) > 0:
                        tbllist += "<TR><TD VALIGN='TOP' ALIGN='LEFT'>"

                        tbllist += "<TABLE border='0' cellborder='0' cellspacing='5'><TR><TD ALIGN='LEFT'><B><U>" + \
                            Lang.getInstance().get(k)+"</U></B></TD></TR>"

                        for l in rst:
                            tbllist += "<TR>"
                            for d in l.keys():
                                tbllist += "<TD VALIGN='TOP' ALIGN='LEFT'>" + \
                                    l[d].strip()+"</TD>"
                            tbllist += "</TR>"
                        tbllist += "</TABLE>"
                        tbllist += "</TD></TR>"
                        tbllistb = True
            tbllist += "</TABLE>"

            if tblhistoryb and tblbaseb:
                s += "<TR><TD VALIGN='TOP' ALIGN='LEFT'>"+tblhistory + \
                    "</TD><TD VALIGN='TOP' ALIGN='LEFT'>"+tblbase + "</TD></TR>"
            else:
                s += "<TR><TD VALIGN='TOP' ALIGN='LEFT' colspan='2'>" + \
                    tblbase + "</TD></TR>"

            if tbllistb:
                s += "<TR><TD VALIGN='TOP' ALIGN='LEFT' colspan='2'>"+tbllist + "</TD></TR>"

        s += "</TABLE>>]\n"
        return s

    def subgraph(self, list, name, title, bln=False):
        file = open("/tmp/pynetmap/"+name+".list", "w")
        for e in list:
            if str(e["value"]) != "":
                ee = float(e["value"])
                dd = float(e["date"])
                if bln:
                    if ee == 100:
                        color = 1
                    else:
                        color = 2
                else:
                    if ee < 25:
                        color = 0
                    elif ee < 75:
                        color = 1
                    else:
                        color = 2
                t = datetime.fromtimestamp(dd)

                file.write(str(t.strftime("%Y%m%d%H%M")))
                file.write(",")
                file.write(str(e["value"]))
                file.write(",")
                file.write(str(color))
                file.write("\n")
        file.close()

        cmd = """gnuplot -e "set terminal png transparent size 800,400 font arial 18;
        set title '"""+title+"""';
        set datafile separator ',';
        set yrange [0:100];
        set xdata time;
        set timefmt '%Y%m%d%H%M';
        set format x '%H:%M';
        set xtics rotate by 45 offset -2,-2;
        set bmargin 3;
        set grid;
        set palette model RGB maxcolors 3;
        set palette model RGB defined (0 '#999900', 1 '#009900', 2 '#cc0000');
        set cbrange [0:2];
        set nocbtics;
        unset colorbox;
        plot '/tmp/pynetmap/""" + name+""".list' using 1:2:3 notitle with filledcurves above x1 fc palette;" > /tmp/pynetmap/""" + name+""" """
        os.system(cmd)

    def generate_node_recur(self, key,  detailed, lvl):
        st = self.node(key, detailed, lvl)
        for k in API.getInstance().find_children(key):
            st += self.generate_node_recur(k, detailed, lvl+1)
            st += self.edge(key, k, lvl+1)
        return st

    def generate(self, selection):
        self.tmpschema = API.getInstance().get(DB_SCHEMA)
        st = self.header
        st += self.node(selection[0], True)
        i = 1
        while i < len(selection):
            st += self.node(selection[i], False)
            st += self.edge(selection[i], selection[i-1], 0)
            i += 1

        for o in API.getInstance().find_children(selection[0]):
            st += self.generate_node_recur(o, False, 1)
            st += self.edge(selection[0], o, 1)
        st += self.footer
        return self.calldot(st)

    def generate_all_map(self):
        st = self.header
        elm = API.getInstance().get("structure")
        for k in elm:
            st += self.generate_node_recur(k, False, 0)

        st += self.footer
        return self.calldot(st)
