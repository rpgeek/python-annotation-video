#! /usr/bin/python

from __future__ import print_function
import sys

from PyQt4 import QtGui # pylint: disable=import-error
from app.player import Player

if __name__ == "__main__":
    APP = QtGui.QApplication(sys.argv)
    PLAYER = Player()
    PLAYER.show()
    PLAYER.resize(640, 480)
    sys.exit(APP.exec_())
