import os


import ConfigParser

CONFIG_FILE = "/etc/pynetmap-client/global.conf"
configuration = ConfigParser.ConfigParser()
with open(CONFIG_FILE) as fp:
    configuration.readfp(fp)

IP = configuration.get("Server", "IP")
PORT = configuration.get("Server", "Port")

SSH_USER = configuration.get("Server SSH", "Username")
SSH_PASSWORD = configuration.get("Server SSH", "Password")
SSH_PORT = configuration.get("Server SSH", "Port")

TERMINAL_COMMAND = configuration.get("Terminal", "Command")
TERMINAL = """[TERMINAL] -e "sshpass -p"""+SSH_PASSWORD+""" ssh -p """+SSH_PORT+""" -tt -o StrictHostKeyChecking=no """ + \
    SSH_USER+"""@"""+IP + \
    """ 'sshpass -p[PASS] ssh -o StrictHostKeyChecking=no [USER]@[IP]' " &"""
