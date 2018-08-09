#!/usr/bin/python
import os
from const import TERMINAL


class Terminal:
    def __init__(self, elm, config):
        try:
            try:
                sport = str(elm["PORT"]).strip()
                if sport == "":
                    sport = 22
                else:
                    sport = int(float(sport))
            except:
                sport = 22
            cmd = TERMINAL
            cmd = cmd.replace("[ServerIP]", str(
                config.get("ServerIP")).strip())
            cmd = cmd.replace("[SSHUsername]", str(
                config.get("SSHUsername")).strip())
            cmd = cmd.replace("[SSHPassword]", str(
                config.get("SSHPassword")).strip())
            cmd = cmd.replace("[SSHPort]", str(config.get("SSHPort")).strip())
            cmd = cmd.replace("[TerminalCommand]", str(
                config.get("TerminalCommand")).strip())
            cmd = cmd.replace("[IP]", str(elm["IP"]).strip())
            cmd = cmd.replace("[PORT]", str(sport).strip())
            cmd = cmd.replace("[USER]", str(elm["User"]).strip())
            cmd = cmd.replace("[PASS]", str(
                elm["Password"]).replace("'", "\\'").strip())
            os.system(cmd)
        except:
            pass
