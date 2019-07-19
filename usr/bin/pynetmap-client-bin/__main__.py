#!/usr/bin/env python
__author__ = 'Samir KHERRAZ'
__copyright__ = '(c) Samir HERRAZ 2018-2019'
__version__ = '1.2.0'
__licence__ = 'GPLv3'

import signal

from gi import require_version
require_version('Gtk', '3.0')
require_version('Vte', '2.91')

from gi.repository import Gtk

from Core.Window.GtkMainWindow import GtkMainWindow


signal.signal(signal.SIGINT, signal.SIG_DFL)

if __name__ == '__main__':

    mainBoot = GtkMainWindow()
    Gtk.main()
