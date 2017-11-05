import os.path
from PyQt4 import QtGui, QtCore  # pylint: disable=import-error
from controller import VideoEventsController  # pylint: disable=import-error
from events import VideoEventsMenu
import vlc  # pylint: disable=import-error
import sys


class VideoFrame(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.click_positions = []
        self.scene = QtGui.QGraphicsScene()
        self.view = QtGui.QGraphicsView(self.scene)
        self.setAttribute(QtCore.Qt.WA_StaticContents)

        img_size = QtCore.QSize(500, 500)
        self.image = QtGui.QImage(img_size, QtGui.QImage.Format_RGB32)
        self.text = ""
        self.last_poz = (0, 0)
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
        self.last_poz = self.player_vlc.video_get_cursor()
        print('last pos ', self.last_poz)

        self.pxl_select(self.player_vlc.video_get_cursor())
        self.video_side_menu.update_pos()

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

        self.__create_ui()
        self.isPaused = False

    def clicked(self, clicked):
        print('clicked ', str(clicked))

    def __create_ui(self):
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
                     self.play_pause)

        self.stopbutton = QtGui.QPushButton("Stop")
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
                     self.set_volume)

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

    def play_pause(self):
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
            filename = QtGui.QFileDialog. \
                getOpenFileName(self, "Open File", os.path.expanduser('~'))
        if not filename:
            return

    def open_file(self, filename=None):
        """Open a media file in a MediaPlayer
        """
        if filename is None:
            dir = os.getcwd()
            filename = QtGui.QFileDialog.getOpenFileName \
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
        self.play_pause()

        self.video_frame.pass_player_ref(self.mediaplayer)
        self.sideeventmenu.pass_player_ref(self.mediaplayer, self.video_frame)
        self.sideeventmenu.set_file_outputs_names(diroutresources)

        self.video_frame.pass_menu_ref(self.sideeventmenu)

    def set_volume(self, Volume):
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
