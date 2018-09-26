#!/usr/bin/env python
__author__ = 'Samir KHERRAZ'
__copyright__ = '(c) Samir HERRAZ 2018-2018'
__version__ = '1.1.0'
__licence__ = 'GPLv3'

import os
TERMINAL = """sshpass -p [SSHPassword] ssh -p [SSHPort] -tt -o StrictHostKeyChecking=no [SSHUsername]@[ServerIP] [ID] """
CONFIG_PATH = os.getenv("HOME")+"/.pynetmap-client"
NAME = "PyNetMAP"
VERSION = " 1.0.4-beta"
