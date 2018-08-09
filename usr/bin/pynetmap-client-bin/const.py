
import os
TERMINAL = """[TerminalCommand] -e "sshpass -p [SSHPassword] ssh -p [SSHPort] -tt -o StrictHostKeyChecking=no [SSHUsername]@[ServerIP] 'sshpass -p[PASS] ssh -p [PORT] -o StrictHostKeyChecking=no [USER]@[IP]' " &"""
CONFIG_PATH = os.getenv("HOME")+"/.pynetmap-client"
