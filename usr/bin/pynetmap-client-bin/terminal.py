#!/usr/bin/env python
__author__ = 'Samir KHERRAZ'
__copyright__ = '(c) Samir HERRAZ 2018-2018'
__version__ = '1.1.0'
__licence__ = 'GPLv3'

import os
from const import TERMINAL
import vte
import gtk
from subprocess import Popen
import threading
import socket
import select


class Terminal:
    def __init__(self, ui):
        self.terminals = dict()
        self.terminals_prc = dict()
        self.terminals_hope = dict()
        self.ui = ui

        if self.ui.api.get_access("users.privilege.terminal"):
            self.sshuser = self.ui.api.get("server", "server.ssh.user")
            self.sshpassword = self.ui.api.get("server", "server.ssh.password")
        else:
            self.sshuser = None
            self.sshpassword = None

    def build(self, key):
        cmd = self.build_cmd(key)
        if cmd != None:
            background = None
            blink = 1
            font = "monospace 10"
            scrollback = 100
            terminal = vte.Terminal()
            terminal.get_pty()
            if (background):
                terminal.set_background_image(background)
            terminal.set_cursor_blinks(blink)
            terminal.set_font_from_string(font)
            terminal.set_scrollback_lines(scrollback)
            master, slave = os.openpty()
            self.terminals_prc[key] = Popen(["/bin/bash", "-c", cmd], stdin=slave,
                                            stdout=slave, stderr=slave)
            self.terminals_hope[key] = 5
            os.close(slave)
            terminal.set_pty(master)
            terminal.show()
            scrollbar = gtk.VScrollbar()
            scrollbar.set_adjustment(terminal.get_adjustment())
            box = gtk.HBox()
            box.pack_start(terminal)
            box.pack_start(scrollbar)
            return box
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
            elm = self.ui.store.get("base", key)
            cmd = TERMINAL
            cmd = cmd.replace("[ServerIP]", str(
                self.ui.config.get("ServerIP")).strip())
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
        for key in self.terminals_hope.keys():
            if key == id:
                if force == True:
                    del self.terminals_hope[key]
                    del self.terminals[key]
                    self.terminals_prc[key].kill()
                    del self.terminals_prc[key]
                else:
                    self.terminals_hope[key] = 5
            elif self.terminals_hope[key] > 0:
                self.terminals_hope[key] -= 1
            else:
                del self.terminals_hope[key]
                del self.terminals[key]
                self.terminals_prc[key].kill()
                del self.terminals_prc[key]

        if id not in self.terminals.keys() or self.terminals[id] == None:
            self.terminals[id] = self.build(id)
        return self.terminals[id]

    def external(self, key):
        cmd = self.build_cmd(key)
        if cmd != None:
            os.system(str(self.ui.config.get("TerminalCommand")
                          ).strip()+' -e "'+cmd+'" &')
