
import os
TERMINAL = """sshpass -p [SSHPassword] ssh -p [SSHPort] -tt -o StrictHostKeyChecking=no [SSHUsername]@[ServerIP] [ID] """
CONFIG_PATH = os.getenv("HOME")+"/.pynetmap-client"
NAME = "PyNetMAP"
VERSION = " 1.0.4-beta"
