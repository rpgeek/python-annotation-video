#! /usr/bin/python

from __future__ import print_function

from __future__ import absolute_import
import sys
import os.path
import vlc
from PyQt4 import QtGui, QtCore
from .VideoEvents import controller
from .VideoEvents import model as mdl
import random
from shutil import copyfile
import json


class VideoEvtWidget(QtGui.QWidget):
    def __init__(self, videoEventModel):
        QtGui.QWidget.__init__(self)
        self.label = QtGui.QLabel(videoEventModel.get_description())
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

    def remove_model(self):
        print('controller removing model from dict')


def showVideoAlert(layout, info="Video Error",
                   defaultResponse="There is no video resource to analyze"):
    QtGui.QMessageBox.about(layout, info, defaultResponse)


class VideoEventsMenu(QtGui.QWidget):
    def __init__(self, eventsController):
        QtGui.QWidget.__init__(self)
        self.controller = eventsController

        self.start = QtGui.QPushButton("Start")
        self.stop = QtGui.QPushButton("Stop")
        self.add = QtGui.QPushButton("Add")
        self.resource = QtGui.QPushButton("Resource")
        self.serialize = QtGui.QPushButton("Serialize")

        self.startLab = QtGui.QLabel("Start: ")

        self.startLab.setMaximumHeight(20)
        self.stopLab = QtGui.QLabel("Stop: ")
        self.posLab = QtGui.QLabel("Pos: ")
        self.posLab.setMaximumHeight(20)
        self.resLab = QtGui.QLabel("Res: ")

        self.eventLayout = QtGui.QGridLayout()
        self.eventLayout.setAlignment(QtCore.Qt.AlignTop)

        self.layout = QtGui.QVBoxLayout()
        self.layout.setAlignment(QtCore.Qt.AlignTop)

        self.eventLayout.addWidget(self.start, 0, 0)
        self.eventLayout.addWidget(self.stop, 0, 1)
        self.eventLayout.addWidget(self.resource, 0, 2)
        self.eventLayout.addWidget(self.add, 1, 0)
        self.eventLayout.addWidget(self.serialize, 1, 1)
        self.eventLayout.addWidget(self.startLab, 2, 0)
        self.eventLayout.addWidget(self.stopLab, 2, 1)
        self.eventLayout.addWidget(self.posLab, 2, 2)
        self.eventLayout.addWidget(self.resLab, 3, 0)

        self.layout.addLayout(self.eventLayout)
        self.setLayout(self.layout)

        self.connect(self.add,
                     QtCore.SIGNAL("clicked()"),
                     self.addVideoEvent)

        self.connect(self.start,
                     QtCore.SIGNAL("clicked()"),
                     self.setstart)

        self.connect(self.stop,
                     QtCore.SIGNAL("clicked()"),
                     self.setstop)

        self.connect(self.resource,
                     QtCore.SIGNAL("clicked()"),
                     self.setres)

        self.connect(self.serialize,
                     QtCore.SIGNAL("clicked()"),
                     self.serializeAction)

        self.models_list = list()
        self.resources = list()
        self.posx = None
        self.posy = None
        self.starttime = self.stoptime = self.resname = False
        self.player_vlc = None
        self.outname = ''
        self.outdir = '../output/'
        if not os.path.exists(self.outdir):
            os.makedirs(self.outdir)

    def serializeAction(self):
        if not self.player_vlc:
            showVideoAlert(self)
            return

        if len(self.models_list) == 0:
            return
        filename = QtGui.QFileDialog.\
            getSaveFileName(self, "Save File", os.path.expanduser(os.getcwd()))

        if len(filename) == 0:
            return

        print('outdir, fileout name ', self.outdir, self.outname)

        serialized_dict = dict()
        serialized_dict['file_name'] = str(self.video_name)
        serialized_dict['events'] = [ob.__dict__ for ob in self.models_list]

        with open(filename, 'w') as outfile:

            strx = json.dumps(serialized_dict, sort_keys=True, indent=4)
            outfile.write(strx)

        if os.path.exists(self.outdir + '/resources/') == 0:
            os.mkdir(self.outdir + 'resources/')

        print('resources ', self.resources)
        for it, (name, dir) in enumerate(self.resources):
            print('enumerate copy ', name, dir)
            print('saving to ', self.outdir + '/resources/' + name)
            copyfile(dir, self.outdir + '/resources/' + name)

    def pass_player_ref(self, playerRef, facadePlayer):
        print('menu player - passed ref')
        self.player_vlc = playerRef
        self.playerFacadeRef = facadePlayer

    def set_file_outputs_names(self, filename):
        self.video_name = filename
        self.openedFileDir = filename.split('.')[-2]
        print('opened file dir ', self.openedFileDir)

    def getPos(self):
        if not self.player_vlc:
            showVideoAlert(self)
            return
        if self.playerFacadeRef:
            self.posx, self.posy = self.playerFacadeRef.lastPos
            print('menu pos ', self.posx, self.posy)
            self.posLab.setText("Pos: " + str((self.posx, self.posy)))

    def setstop(self):
        print('set stop')
        if not self.player_vlc:
            showVideoAlert(self)
            return
        if self.player_vlc.get_time() == -1:
            self.stoptime = 0
        else:
            self.stoptime = self.player_vlc.get_time()
        self.stopLab.setText("Stop: " + str(self.stoptime))

    def setstart(self):
        print('set start')
        if not self.player_vlc:
            showVideoAlert(self)
            return
        if self.player_vlc.get_time() == -1:
            self.starttime = 0
        else:
            self.starttime = self.player_vlc.get_time()

        self.startLab.setText("Start: " + str(self.starttime))

    def setres(self):
        if not self.player_vlc:
            showVideoAlert(self)
            return
        print('set res')
        dir = os.getcwd()
        fnamedir = QtGui.QFileDialog.\
            getOpenFileName(self, 'Open file', dir)

        if len(fnamedir) == 0:
            return

        name = fnamedir.split('/')[-1]
        print('res ', name)
        self.resources.append((name, fnamedir))

        dirout = os.getcwd() + "/data/"

        if os.path.exists(dirout) == 0:
            os.mkdir(dirout)

        diroutresources = os.getcwd() + "/data/" + self.openedFileDir
        print('dirout resources ', diroutresources)

        if os.path.exists(diroutresources) == 0:
            os.mkdir(diroutresources)

        copyfile(fnamedir, diroutresources + "/" + name)
        self.resname = name
        self.resLab.setText("Res: " + str(self.resname))

    def addVideoEvent(self):
        if not self.resname or not self.starttime or not self.stoptime:
            print('set start stop and res')
            return
        if not self.posx and not self.posy:
            return

        id = random.randint(0, 2 ** 32 - 1)

        fileType = str(self.resname).split('.')[-1]
        if fileType == 'jpg' or fileType == 'gif' or fileType == 'jpeg' or fileType == 'png':
            type = 'image'
        elif fileType == 'mp3' or fileType == 'wav' or fileType == 'ogg':
            type = 'audio'
        else:
            type = 'text'

        model = mdl.VideoEventModel(id, self.starttime,
                                    self.stoptime, self.posx,
                                    self.posy, type, str(self.resname))
        self.controller.addModel(model)
        self.models_list.append(model)

        video_evt_widget = VideoEvtWidget(model)

        box = QtGui.QHBoxLayout()

        removeBtn = QtGui.QPushButton("X")
        box.addWidget(removeBtn)
        box.addWidget(video_evt_widget)

        widg = QtGui.QWidget()
        widg.setLayout(box)

        removeBtn.clicked.connect(lambda state, x=id: self.button_pushed(x, widg))

        self.layout.addWidget(widg)

        self.starttime = self.stoptime = self.resname = False
        self.cleanLabels()

    def button_pushed(self, num, boxref):
        print('Pushed button {}'.format(num))
        self.controller.removeModel(num)
        self.layout.removeWidget(boxref)
        boxref.deleteLater()

    def cleanLabels(self):
        self.startLab.setText("Start: ")
        self.stopLab.setText("Stop: ")
        self.posLab.setText("Pos: ")
        self.resLab.setText("Res: ")


class VideoFrame(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.click_positions = []
        self.scene = QtGui.QGraphicsScene()
        self.view = QtGui.QGraphicsView(self.scene)
        self.setAttribute(QtCore.Qt.WA_StaticContents)

        imageSize = QtCore.QSize(500, 500)
        self.image = QtGui.QImage(imageSize, QtGui.QImage.Format_RGB32)
        self.text = ""
        self.lastPos = (0, 0)
        self.player_vlc = None

    def pass_player_ref(self, playerRef):
        self.player_vlc = playerRef

    def pass_menu_ref(self, video_side):
        self.video_side_menu = video_side

    def mousePressEvent(self, QMouseEvent):
        print('mouse pressed')
        if not self.player_vlc:
            return
        print(self.player_vlc.video_get_cursor())
        print(self.player_vlc.get_time())
        self.lastPos = self.player_vlc.video_get_cursor()
        print('last pos ', self.lastPos)

        self.pixelSelect(self.player_vlc.video_get_cursor())
        self.video_side_menu.getPos()

    def pixelSelect(self, eventpos):
        print('pixel select')
        painter = QtGui.QPainter(self.image)
        painter.setPen(QtGui.QPen(QtCore.Qt.red, 55,
                                  QtCore.Qt.SolidLine,
                                  QtCore.Qt.RoundCap,
                                  QtCore.Qt.RoundJoin))

        painter.drawLine(QtCore.QPoint(22, 22), QtCore.QPoint(100, 100))

        self.update()


class Player(QtGui.QMainWindow):
    """A simple Media Player using VLC and Qt
    """

    def __init__(self, master=None):
        QtGui.QMainWindow.__init__(self, master)
        self.setWindowTitle("Media Player")

        self.instance = vlc.Instance("--no-xlib")
        self.mediaplayer = self.instance.media_player_new()

        self.createUI()
        self.isPaused = False

    def clicked(self, clicked):
        print('clicked ', str(clicked))

    def createUI(self):
        """Set up the user interface, signals & slots
        """
        self.widget = QtGui.QWidget(self)
        self.setCentralWidget(self.widget)

        # In this widget, the video will be drawn
        if sys.platform == "darwin":  # for MacOS
            self.videoframe = QtGui.QMacCocoaViewContainer(0)
        else:

            self.videoframe = VideoFrame()
        # self.connect(self.videoframe, QtCore.SIGNAL("clicked()"),
        #                  self.clicked)

        self.palette = self.videoframe.palette()
        self.palette.setColor(QtGui.QPalette.Window,
                              QtGui.QColor(0, 0, 0))
        self.videoframe.setPalette(self.palette)
        self.videoframe.setAutoFillBackground(True)

        self.positionslider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.positionslider.setToolTip("Position")
        self.positionslider.setMaximum(1000)
        self.connect(self.positionslider,
                     QtCore.SIGNAL("sliderMoved(int)"), self.setPosition)

        self.hbuttonbox = QtGui.QHBoxLayout()
        self.playbutton = QtGui.QPushButton("Play")
        self.hbuttonbox.addWidget(self.playbutton)
        self.connect(self.playbutton, QtCore.SIGNAL("clicked()"),
                     self.PlayPause)

        self.stopbutton = QtGui.QPushButton("Stop")
        self.hbuttonbox.addWidget(self.stopbutton)
        self.connect(self.stopbutton, QtCore.SIGNAL("clicked()"),
                     self.Stop)

        self.hbuttonbox.addStretch(1)
        self.volumeslider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.volumeslider.setMaximum(100)
        self.volumeslider.setValue(self.mediaplayer.audio_get_volume())
        self.volumeslider.setToolTip("Volume")
        self.hbuttonbox.addWidget(self.volumeslider)
        self.connect(self.volumeslider,
                     QtCore.SIGNAL("valueChanged(int)"),
                     self.setVolume)

        self.vboxlayout = QtGui.QVBoxLayout()
        self.vboxlayout.addWidget(self.videoframe)
        self.vboxlayout.addWidget(self.positionslider)
        self.vboxlayout.addLayout(self.hbuttonbox)

        self.controller = controller.VideoEventsController()

        self.sideeventmenu = VideoEventsMenu(self.controller)

        self.hboxlayout = QtGui.QHBoxLayout(self)
        self.hboxlayout.addLayout(self.vboxlayout)
        self.hboxlayout.addWidget(self.sideeventmenu)
        #
        self.widget.setLayout(self.hboxlayout)

        # self.widget.setLayout(self.vboxlayout)

        open = QtGui.QAction("&Open", self)
        self.connect(open, QtCore.SIGNAL("triggered()"), self.OpenFile)

        exit = QtGui.QAction("&Exit", self)
        self.connect(exit, QtCore.SIGNAL("triggered()"), sys.exit)
        menubar = self.menuBar()
        filemenu = menubar.addMenu("&File")
        filemenu.addAction(open)
        filemenu.addSeparator()
        filemenu.addAction(exit)

        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(200)
        self.connect(self.timer, QtCore.SIGNAL("timeout()"),
                     self.updateUI)

    def PlayPause(self):
        """Toggle play/pause status
        """
        if self.mediaplayer.is_playing():
            self.mediaplayer.pause()
            self.playbutton.setText("Play")
            self.isPaused = True
        else:
            if self.mediaplayer.play() == -1:
                self.OpenFile()
                return
            self.mediaplayer.play()
            self.playbutton.setText("Pause")
            self.timer.start()
            self.isPaused = False

    def Stop(self):
        """Stop player
        """
        self.mediaplayer.stop()
        self.playbutton.setText("Play")

    def SaveFile(self, filename=None):
        """Open a media file in a MediaPlayer
        """
        if filename is None:
            filename = QtGui.QFileDialog.getOpenFileName\
                (self, "Open File", os.path.expanduser('~'))
        if not filename:
            return

    def OpenFile(self, filename=None):
        """Open a media file in a MediaPlayer
        """
        if filename is None:
            dir = os.getcwd()
            filename = QtGui.QFileDialog.getOpenFileName\
                (self, "Open File", os.path.expanduser(dir))
        if not filename:
            return

        diroutresources = filename.split('/')[-1]

        # create the media
        if sys.version < '3':
            filename = unicode(filename)
        self.media = self.instance.media_new(filename)
        # put the media in the media player
        self.mediaplayer.set_media(self.media)

        # parse the metadata of the file
        self.media.parse()
        # set the title of the track as window title
        self.setWindowTitle(self.media.get_meta(0))

        # the media player has to be 'connected' to the QFrame
        # (otherwise a video would be displayed in it's own window)
        # this is platform specific!
        # you have to give the id of the QFrame (or similar object) to
        # vlc, different platforms have different functions for this
        if sys.platform.startswith('linux'):  # for Linux using the X Server
            self.mediaplayer.set_xwindow(self.videoframe.winId())
        elif sys.platform == "win32":  # for Windows
            self.mediaplayer.set_hwnd(self.videoframe.winId())
        elif sys.platform == "darwin":  # for MacOS
            self.mediaplayer.set_nsobject(self.videoframe.winId())
        self.PlayPause()

        self.videoframe.pass_player_ref(self.mediaplayer)
        self.sideeventmenu.pass_player_ref(self.mediaplayer, self.videoframe)
        self.sideeventmenu.set_file_outputs_names(diroutresources)

        self.videoframe.pass_menu_ref(self.sideeventmenu)

    def setVolume(self, Volume):
        """Set the volume
        """
        self.mediaplayer.audio_set_volume(Volume)

    def setPosition(self, position):
        """Set the position
        """
        # setting the position to where the slider was dragged
        self.mediaplayer.set_position(position / 1000.0)
        # the vlc MediaPlayer needs a float value between 0 and 1, Qt
        # uses integer variables, so you need a factor the higher the
        # factor, the more precise are the results
        # (1000 should be enough)

    def updateUI(self):
        """updates the user interface"""
        # setting the slider to the desired position
        self.positionslider.setValue(self.mediaplayer.get_position() * 1000)

        if not self.mediaplayer.is_playing():
            # no need to call this function if nothing is played
            self.timer.stop()
            if not self.isPaused:
                # after the video finished, the play button stills shows
                # "Pause", not the desired behavior of a media player
                # this will fix it
                self.Stop()


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    player = Player()
    player.show()
    player.resize(640, 480)
sys.exit(app.exec_())
