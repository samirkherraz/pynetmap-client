#!/usr/bin/env python
__author__ = 'Samir KHERRAZ'
__copyright__ = '(c) Samir HERRAZ 2018-2019'
__version__ = '1.3.0'
__licence__ = 'GPLv3'

from gi import require_version

require_version('Gtk', '3.0')
require_version('Vte', '2.91')

from Core.Window.GtkMainWindow import GtkMainWindow
from gi.repository import Gtk
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

if __name__ == '__main__':

    mainBoot = GtkMainWindow()
    Gtk.main()
