#!/usr/bin/env python
__author__ = 'Samir KHERRAZ'
__copyright__ = '(c) Samir HERRAZ 2018-2019'
__version__ = '1.2.0'
__licence__ = 'GPLv3'

import os
import select
import socket
import threading
from subprocess import Popen
from urllib.request import urlparse
from threading import Lock
from gi.repository import Gtk, Gdk, GLib, Vte
from Core.Libs.Config import Config
from Core.Libs.Api import Api
from Constants import *
class Terminal:
    def __init__(self):
        self.terminals = dict()
        self.spawns = dict()
        self._lock = Lock()

    def reload_access(self):
        if Api.getInstance().get_access("terminal"):
            self.sshuser = Api.getInstance().get("server", "ssh", "user")
            self.sshpassword = Api.getInstance().get("server", "ssh", "password")
        else:
            self.sshuser = None
            self.sshpassword = None

    def build(self, key):
        cmd = self.build_cmd(key)
        if cmd != None:
            self.spawns[key] = Vte.Terminal()

            self.spawns[key].spawn_sync(
                Vte.PtyFlags.DEFAULT,
                os.environ['HOME'],
                ["/bin/bash", "-c", cmd],
                [],
                GLib.SpawnFlags.DO_NOT_REAP_CHILD,
                None,
                None,
            )
            swin = Gtk.ScrolledWindow()
            swin.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            swin.add_with_viewport(self.spawns[key])

            return swin
        else:
            return None

    def handler(self, chan, host, port):
        sock = socket.socket()
        try:
            sock.connect((host, port))
        except:
            return

        while True:
            r, w, x = select.select([sock, chan], [], [])
            if sock in r:
                data = sock.recv(1024)
                if len(data) == 0:
                    break
                chan.send(data)
            if chan in r:
                data = chan.recv(1024)
                if len(data) == 0:
                    break
                sock.send(data)
        chan.close()
        sock.close()

    def reverse_forward_tunnel(self, server_port, remote_host, remote_port, transport):
        transport.request_port_forward("", server_port)
        while True:
            chan = transport.accept(1000)
            if chan is None:
                continue
            thr = threading.Thread(
                target=self.handler, args=(chan, remote_host, remote_port)
            )
            thr.setDaemon(True)
            thr.start()

    def build_cmd(self, key):
        try:
            cmd = "sshpass -p [SSHPassword] ssh -p [SSHPort] -tt -o StrictHostKeyChecking=no [SSHUsername]@[Server] [ID] "
            cmd = cmd.replace("[Server]", str(
                urlparse(Config.getInstance().get("server")).hostname))
            cmd = cmd.replace("[SSHUsername]", self.sshuser)
            cmd = cmd.replace("[SSHPassword]",
                              self.sshpassword.replace("!", "\\!").strip())
            cmd = cmd.replace(
                "[SSHPort]", Config.getInstance().get("SSHPort").strip())
            cmd = cmd.replace("[TerminalCommand]", str(
                Config.getInstance().get("TerminalCommand")).strip())
            cmd = cmd.replace("[ID]", key)
            return cmd
        except:
            return None


    def build_cmd_tunnel(self, key):
        try:
            cmd = "sudo sshpass -p '[TunnelPassword]' sshuttle -e 'ssh -q -o CheckHostIP=no -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null' -r [TunnelUsername]@[TunnelServer]:[TunnelPort] [TunnelNetwork]"
            cmd = cmd.replace("[TunnelPassword]", str(Api.getInstance().get(DB_BASE, key, KEY_TUNNEL_PASSWORD)).replace("'","\\'"))
            cmd = cmd.replace("[TunnelUsername]", str(Api.getInstance().get(DB_BASE, key, KEY_TUNNEL_USER)))
            cmd = cmd.replace("[TunnelServer]", str(Api.getInstance().get(DB_BASE, key, KEY_TUNNEL_IP)))
            cmd = cmd.replace("[TunnelPort]", str(Api.getInstance().get(DB_BASE, key, KEY_TUNNEL_PORT)))
            cmd = cmd.replace("[TunnelNetwork]", str(Api.getInstance().get(DB_BASE, key, KEY_TUNNEL_NETWORK)))
            return cmd
        except:
            return None

    def internal(self, id, force=False):
        if force == True:
            self.terminals[id] = self.build(id)
        self.reload_access()
        if id not in self.terminals.keys() or self.terminals[id] == None:
            self.terminals[id] = self.build(id)
        return self.terminals[id]

    def external(self, key):
        self.reload_access()
        cmd = self.build_cmd(key)
        if cmd != None:
            os.system(str(Config.getInstance().get("TerminalCommand")
                          ).strip()+' -e "'+cmd+'" &')

    def external_tunnel(self, key):
        self.reload_access()
        cmd = self.build_cmd_tunnel(key)
        if cmd != None:
            os.system(str(Config.getInstance().get("TerminalCommand")
                          ).strip()+' -e "'+cmd+'" &')
    def purge(self):
        ll = list(self.spawns.keys())
        for t in ll:
            del self.spawns[t]