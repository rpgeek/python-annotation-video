import json
import random
from PyQt4 import QtGui, QtCore  # pylint: disable=import-error
import os
from shutil import copyfile
from model import VideoEventModel


class VideoEvtWidget(QtGui.QWidget):
    def __init__(self, vid_evt_mdl):
        QtGui.QWidget.__init__(self)
        self.label = QtGui.QLabel(vid_evt_mdl.get_description)
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)


def show_video_alert(layout, info="Video Error",
                     default_resp="There is no video resource to analyze"):
    """
    Showing video alert function
    :param layout:
    :param info: String info
    :param default_resp: String response
    """
    QtGui.QMessageBox.about(layout, info, default_resp)


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
                     self.add_video_event)

        self.connect(self.start,
                     QtCore.SIGNAL("clicked()"),
                     self.set_start)

        self.connect(self.stop,
                     QtCore.SIGNAL("clicked()"),
                     self.set_stop)

        self.connect(self.resource,
                     QtCore.SIGNAL("clicked()"),
                     self.set_res)

        self.connect(self.serialize,
                     QtCore.SIGNAL("clicked()"),
                     self.serialize_action)

        self.models_list = list()
        self.resources = list()
        self.posx = None
        self.posy = None
        self.start_time = self.stoptime = self.resname = False
        self.player_vlc = None
        self.outname = ''
        self.outdir = '../output/'
        if not os.path.exists(self.outdir):
            os.makedirs(self.outdir)

    def serialize_action(self):
        """
        Serialization for events
        :return: None
        """
        if not self.player_vlc:
            show_video_alert(self)
            return

        if len(self.models_list) == 0:
            return
        filename = QtGui.QFileDialog. \
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
        """
        Passing player ref and facade player
        :param player_ref:
        :param facade_player:
        """
        print('menu player - passed ref')
        self.player_vlc = player_ref
        self.player_facade = facade_player

    def set_file_outputs_names(self, filename):
        self.video_name = filename
        self.opened_file_dir = filename.split('.')[-2]
        print('opened file dir ', self.opened_file_dir)

    def update_pos(self):
        """
        Update position from player_facade
        :return:
        """
        if not self.player_vlc:
            show_video_alert(self)
            return
        if self.player_facade:
            self.posx, self.posy = self.player_facade.lastPos
            print('menu pos ', self.posx, self.posy)
            self.pos_lab.setText("Pos: " + str((self.posx, self.posy)))

    def set_stop(self):
        """
        Setting stop time
        :return: None
        """
        print('set stop')
        if not self.player_vlc:
            show_video_alert(self)
            return
        if self.player_vlc.get_time() == -1:
            self.stoptime = 0
        else:
            self.stoptime = self.player_vlc.get_time()
        self.stop_lab.setText("stop_player: " + str(self.stoptime))

    def set_start(self):
        """
        Setting start time
        :return:
        """
        print('set start')
        if not self.player_vlc:
            show_video_alert(self)
            return
        if self.player_vlc.get_time() == -1:
            self.start_time = 0
        else:
            self.start_time = self.player_vlc.get_time()

        self.start_lab.setText("Start: " + str(self.start_time))

    def set_res(self):
        """
        Setting data resource file
        :return:
        """
        if not self.player_vlc:
            show_video_alert(self)
            return
        print('set res')
        dir = os.getcwd()
        fnamedir = QtGui.QFileDialog. \
            getOpenFileName(self, 'Open file', dir)

        if fnamedir == 0:
            return

        name = fnamedir.split('/')[-1]
        print('res ', name)
        self.resources.append((name, fnamedir))

        dirout = os.getcwd() + "/data/"

        if os.path.exists(dirout) == 0:
            os.mkdir(dirout)

        diroutresources = os.getcwd() + "/data/" + self.opened_file_dir
        print('dirout resources ', diroutresources)

        if os.path.exists(diroutresources) == 0:
            os.mkdir(diroutresources)

        copyfile(fnamedir, diroutresources + "/" + name)
        self.resname = name
        self.res_lab.setText("Res: " + str(self.resname))

    def add_video_event(self):
        """
        Adding new video evt
        :return: None
        """
        available_file_types = ['jpg', 'gif', 'jpeg', 'png']
        if not self.resname or not self.start_time or not self.stoptime:
            print('set start stop and res')
            return
        if not self.posx and not self.posy:
            return

        id = random.randint(0, 2 ** 32 - 1)

        fileType = str(self.resname).split('.')[-1]
        if fileType in available_file_types:
            type = 'image'
        elif fileType == 'mp3' or fileType == 'wav' or fileType == 'ogg':
            type = 'audio'
        else:
            type = 'text'

        model = VideoEventModel(id, self.start_time,
                                self.stoptime, self.posx,
                                self.posy, type, str(self.resname))

        self.controller.add_model(model)
        self.models_list.append(model)

        video_evt_widget = VideoEvtWidget(model)

        box = QtGui.QHBoxLayout()

        remove_btn = QtGui.QPushButton("X")
        box.addWidget(remove_btn)
        box.addWidget(video_evt_widget)

        widg = QtGui.QWidget()
        widg.setLayout(box)

        remove_btn.clicked.connect(lambda state, x=id:
                                   self.button_pushed(x, widg))

        self.layout.addWidget(widg)

        self.start_time = self.stoptime = self.resname = False
        self.clean_labels()

    def button_pushed(self, num, boxref):
        """
        Bushed button
        :param num:
        :param boxref:
        """
        print('Pushed button {}'.format(num))
        self.controller.remove_model(num)
        self.layout.removeWidget(boxref)
        boxref.deleteLater()

    def clean_labels(self):
        """
        Cleaning labels after new video start
        """
        self.start_lab.setText("Start: ")
        self.stop_lab.setText("stop_player: ")
        self.pos_lab.setText("Pos: ")
        self.res_lab.setText("Res: ")
