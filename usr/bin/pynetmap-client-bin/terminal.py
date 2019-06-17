#!/usr/bin/env python
__author__ = 'Samir KHERRAZ'
__copyright__ = '(c) Samir HERRAZ 2018-2018'
__version__ = '1.1.0'
__licence__ = 'GPLv3'

import os
import select
import socket
import threading
from subprocess import Popen
from urllib.request import urlparse

from gi.repository import Gtk, Gdk, GLib,Vte

from const import TERMINAL


class Terminal:
    def __init__(self, ui):
        self.terminals = dict()
        self.ui = ui

    def reload_access(self):
        if self.ui.api.get_access("users.privilege.terminal"):
            self.sshuser = self.ui.api.get("server", "server.ssh.user")
            self.sshpassword = self.ui.api.get("server", "server.ssh.password")
        else:
            self.sshuser = None
            self.sshpassword = None

    def build(self, key):
        cmd = self.build_cmd(key)
        if cmd != None:
            terminal = Vte.Terminal()
            
            self.terminals[key] = terminal
            terminal.spawn_sync(
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
            swin.add_with_viewport(terminal)
            
            return swin
        else:
            return None

    def handler(self, chan, host, port):
        sock = socket.socket()
        try:
            sock.connect((host, port))
        except Exception as e:
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
            cmd = TERMINAL
            cmd = cmd.replace("[Server]", str(
                urlparse(self.ui.config.get("server")).hostname))
            cmd = cmd.replace("[SSHUsername]", self.sshuser)
            cmd = cmd.replace("[SSHPassword]",
                              self.sshpassword.replace("!", "\\!").strip())
            cmd = cmd.replace(
                "[SSHPort]", self.ui.config.get("SSHPort").strip())
            cmd = cmd.replace("[TerminalCommand]", str(
                self.ui.config.get("TerminalCommand")).strip())
            cmd = cmd.replace("[ID]", key)
            return cmd
        except:
            return None

    def internal(self, id, force=False):
        for key in self.terminals.keys():
            if key == id:
                if force == True:
                    del self.terminals[key]
        self.reload_access()
        if id not in self.terminals.keys() or self.terminals[id] == None:
            self.terminals[id] = self.build(id)
        return self.terminals[id]

    def external(self, key):
        self.reload_access()
        cmd = self.build_cmd(key)
        if cmd != None:
            os.system(str(self.ui.config.get("TerminalCommand")
                          ).strip()+' -e "'+cmd+'" &')
