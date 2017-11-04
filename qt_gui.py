#! /usr/bin/python

from __future__ import print_function
import sys
import os.path
from PyQt4 import QtGui, QtCore
from VideoEvents.model import VideoEventModel
from VideoEvents.controller import VideoEventsController
import random
from shutil import copyfile
import json
import vlc


class VideoEvtWidget(QtGui.QWidget):
    def __init__(self, vid_evt_mdl):
        QtGui.QWidget.__init__(self)
        self.label = QtGui.QLabel(vid_evt_mdl.get_description())
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)


def show_video_alert(layout, info="Video Error",
                     defaultResponse="There is no video resource to analyze"):
    QtGui.QMessageBox.about(layout, info, defaultResponse)


class VideoEventsMenu(QtGui.QWidget):
    def __init__(self, eventsController):
        QtGui.QWidget.__init__(self)
        self.controller = eventsController

        self.start = QtGui.QPushButton("Start")
        self.stop = QtGui.QPushButton("stop_player")
        self.add = QtGui.QPushButton("Add")
        self.resource = QtGui.QPushButton("Resource")
        self.serialize = QtGui.QPushButton("Serialize")

        self.start_lab = QtGui.QLabel("Start: ")

        self.start_lab.setMaximumHeight(20)
        self.stop_lab = QtGui.QLabel("stop_player: ")
        self.pos_lab = QtGui.QLabel("Pos: ")
        self.pos_lab.setMaximumHeight(20)
        self.res_lab = QtGui.QLabel("Res: ")

        self.evt_layout = QtGui.QGridLayout()
        self.evt_layout.setAlignment(QtCore.Qt.AlignTop)

        self.layout = QtGui.QVBoxLayout()
        self.layout.setAlignment(QtCore.Qt.AlignTop)

        self.evt_layout.addWidget(self.start, 0, 0)
        self.evt_layout.addWidget(self.stop, 0, 1)
        self.evt_layout.addWidget(self.resource, 0, 2)
        self.evt_layout.addWidget(self.add, 1, 0)
        self.evt_layout.addWidget(self.serialize, 1, 1)
        self.evt_layout.addWidget(self.start_lab, 2, 0)
        self.evt_layout.addWidget(self.stop_lab, 2, 1)
        self.evt_layout.addWidget(self.pos_lab, 2, 2)
        self.evt_layout.addWidget(self.res_lab, 3, 0)

        self.layout.addLayout(self.evt_layout)
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
            show_video_alert(self)
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

    def pass_player_ref(self, player_ref, facade_player):
        print('menu player - passed ref')
        self.player_vlc = player_ref
        self.playerFacadeRef = facade_player

    def set_file_outputs_names(self, filename):
        self.video_name = filename
        self.openedFileDir = filename.split('.')[-2]
        print('opened file dir ', self.openedFileDir)

    def getPos(self):
        if not self.player_vlc:
            show_video_alert(self)
            return
        if self.playerFacadeRef:
            self.posx, self.posy = self.playerFacadeRef.lastPos
            print('menu pos ', self.posx, self.posy)
            self.pos_lab.setText("Pos: " + str((self.posx, self.posy)))

    def setstop(self):
        print('set stop')
        if not self.player_vlc:
            show_video_alert(self)
            return
        if self.player_vlc.get_time() == -1:
            self.stoptime = 0
        else:
            self.stoptime = self.player_vlc.get_time()
        self.stop_lab.setText("stop_player: " + str(self.stoptime))

    def setstart(self):
        print('set start')
        if not self.player_vlc:
            show_video_alert(self)
            return
        if self.player_vlc.get_time() == -1:
            self.starttime = 0
        else:
            self.starttime = self.player_vlc.get_time()

        self.start_lab.setText("Start: " + str(self.starttime))

    def setres(self):
        if not self.player_vlc:
            show_video_alert(self)
            return
        print('set res')
        dir = os.getcwd()
        fnamedir = QtGui.QFileDialog.\
            getOpenFileName(self, 'Open file', dir)

        if fnamedir == 0:
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
        self.res_lab.setText("Res: " + str(self.resname))

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
        self.controller.add_model(model)
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
        self.controller.remove_model(num)
        self.layout.removeWidget(boxref)
        boxref.deleteLater()

    def cleanLabels(self):
        self.start_lab.setText("Start: ")
        self.stop_lab.setText("stop_player: ")
        self.pos_lab.setText("Pos: ")
        self.res_lab.setText("Res: ")


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

        self.pxl_select(self.player_vlc.video_get_cursor())
        self.video_side_menu.getPos()

    def pxl_select(self, eventpos):
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

        self.create_ui()
        self.isPaused = False

    def clicked(self, clicked):
        print('clicked ', str(clicked))

    def create_ui(self):
        """Set up the user interface, signals & slots
        """
        self.widget = QtGui.QWidget(self)
        self.setCentralWidget(self.widget)

        # In this widget, the video will be drawn
        if sys.platform == "darwin":  # for MacOS
            self.video_frame = QtGui.QMacCocoaViewContainer(0)
        else:

            self.video_frame = VideoFrame()
        # self.connect(self.videoframe, QtCore.SIGNAL("clicked()"),
        #                  self.clicked)

        self.palette = self.video_frame.palette()
        self.palette.setColor(QtGui.QPalette.Window,
                              QtGui.QColor(0, 0, 0))
        self.video_frame.setPalette(self.palette)
        self.video_frame.setAutoFillBackground(True)

        self.positionslider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.positionslider.setToolTip("Position")
        self.positionslider.setMaximum(1000)
        self.connect(self.positionslider,
                     QtCore.SIGNAL("sliderMoved(int)"), self.set_position)

        self.hbuttonbox = QtGui.QHBoxLayout()
        self.playbutton = QtGui.QPushButton("Play")
        self.hbuttonbox.addWidget(self.playbutton)
        self.connect(self.playbutton, QtCore.SIGNAL("clicked()"),
                     self.PlayPause)

        self.stopbutton = QtGui.QPushButton("stop_player")
        self.hbuttonbox.addWidget(self.stopbutton)
        self.connect(self.stopbutton, QtCore.SIGNAL("clicked()"),
                     self.stop_player)

        self.hbuttonbox.addStretch(1)
        self.volumeslider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.volumeslider.setMaximum(100)
        self.volumeslider.setValue(self.mediaplayer.audio_get_volume())
        self.volumeslider.setToolTip("Volume")
        self.hbuttonbox.addWidget(self.volumeslider)
        self.connect(self.volumeslider,
                     QtCore.SIGNAL("valueChanged(int)"),
                     self.setVolume)

        self.vbox_layout = QtGui.QVBoxLayout()
        self.vbox_layout.addWidget(self.video_frame)
        self.vbox_layout.addWidget(self.positionslider)
        self.vbox_layout.addLayout(self.hbuttonbox)

        self.controller = VideoEventsController()

        self.sideeventmenu = VideoEventsMenu(self.controller)

        self.hbox_layout = QtGui.QHBoxLayout(self)
        self.hbox_layout.addLayout(self.vbox_layout)
        self.hbox_layout.addWidget(self.sideeventmenu)
        #
        self.widget.setLayout(self.hbox_layout)

        # self.widget.setLayout(self.vboxlayout)

        open = QtGui.QAction("&Open", self)
        self.connect(open, QtCore.SIGNAL("triggered()"), self.open_file)

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
                     self.update_ui)

    def PlayPause(self):
        """Toggle play/pause status
        """
        if self.mediaplayer.is_playing():
            self.mediaplayer.pause()
            self.playbutton.setText("Play")
            self.isPaused = True
        else:
            if self.mediaplayer.play() == -1:
                self.open_file()
                return
            self.mediaplayer.play()
            self.playbutton.setText("Pause")
            self.timer.start()
            self.isPaused = False

    def stop_player(self):
        """stop_player player
        """
        self.mediaplayer.stop()
        self.playbutton.setText("Play")

    def save_file(self, filename=None):
        """Open a media file in a MediaPlayer
        """
        if filename is None:
            filename = QtGui.QFileDialog.getOpenFileName\
                (self, "Open File", os.path.expanduser('~'))
        if not filename:
            return

    def open_file(self, filename=None):
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
            self.mediaplayer.set_xwindow(self.video_frame.winId())
        elif sys.platform == "win32":  # for Windows
            self.mediaplayer.set_hwnd(self.video_frame.winId())
        elif sys.platform == "darwin":  # for MacOS
            self.mediaplayer.set_nsobject(self.video_frame.winId())
        self.PlayPause()

        self.video_frame.pass_player_ref(self.mediaplayer)
        self.sideeventmenu.pass_player_ref(self.mediaplayer, self.video_frame)
        self.sideeventmenu.set_file_outputs_names(diroutresources)

        self.video_frame.pass_menu_ref(self.sideeventmenu)

    def setVolume(self, Volume):
        """Set the volume
        """
        self.mediaplayer.audio_set_volume(Volume)

    def set_position(self, position):
        """Set the position
        """
        # setting the position to where the slider was dragged
        self.mediaplayer.set_position(position / 1000.0)
        # the vlc MediaPlayer needs a float value between 0 and 1, Qt
        # uses integer variables, so you need a factor the higher the
        # factor, the more precise are the results
        # (1000 should be enough)

    def update_ui(self):
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
                self.stop_player()


if __name__ == "__main__":
    APP = QtGui.QApplication(sys.argv)
    PLAYER = Player()
    PLAYER.show()
    PLAYER.resize(640, 480)
    sys.exit(APP.exec_())
