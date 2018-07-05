#!/usr/bin/python
import os
from const import TERMINAL, TERMINAL_COMMAND


class Terminal:
    def __init__(self, elm):
        try:
            cmd = TERMINAL
            cmd = cmd.replace("[IP]", str(elm["IP"]).strip())
            cmd = cmd.replace("[USER]", str(elm["User"]).strip())
            cmd = cmd.replace("[PASS]", str(
                elm["Password"]).replace("'", "\\'").strip())
            cmd = cmd.replace("[TERMINAL]", TERMINAL_COMMAND.strip())
            os.system(cmd)
        except:
            pass
