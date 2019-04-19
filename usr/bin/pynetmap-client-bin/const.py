#!/usr/bin/env python
__author__ = 'Samir KHERRAZ'
__copyright__ = '(c) Samir HERRAZ 2018-2018'
__version__ = '1.1.0'
__licence__ = 'GPLv3'

import os

TERMINAL = """sshpass -p [SSHPassword] ssh -p [SSHPort] -tt -o StrictHostKeyChecking=no [SSHUsername]@[Server] [ID] """
CONFIG_PATH = os.getenv("HOME")+"/.pynetmap-client"
NAME = "PyNetMAP"
VERSION = " 1.0.4-beta"



RUNNING_STATUS = "running"
STOPPED_STATUS = "stopped"
UNKNOWN_STATUS = "unknown"


KEY_MONITOR_ZABBIX_ID = "monitor.zabbix.id"
KEY_MONITOR_NB_CPU="nbcpu"
KEY_MONITOR_HISTORY="history"
KEY_MONITOR_LISTS="lists"
KEY_MONITOR_MEMORY="memory"
KEY_MONITOR_DISK="disk"
KEY_MONITOR_CPU_USAGE="cpuUsage"
KEY_MONITOR_MOUNTS="mounts"

KEY_DISCOVER_PROXMOX_ID="discover.proxmox.id"
KEY_DISCOVER_PROXMOX_STATUS="discover.proxmox.status"

KEY_SSH_USER="ssh.user"
KEY_SSH_PASSWORD="ssh.password"
KEY_SSH_PORT="ssh.port"

KEY_TYPE="type"
KEY_NET_IP="net.ip"
KEY_NET_ETH="net.eth"
KEY_NET_MAC="net.mac"

KEY_NAME="name"

KEY_LAST_UPDATE="lastUpdate"
KEY_MONITOR="monitor"
KEY_HYPERVISOR="hypervisor"
KEY_STATUS="status"