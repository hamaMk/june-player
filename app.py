from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtWidgets import QFileDialog
import os
import sys
import vlc
from urllib.parse import urlparse, unquote
from models import PlaylistModel
import time
import datetime

# playback options
default = vlc.PlaybackMode.default
loop = vlc.PlaybackMode.loop
repeat = vlc.PlaybackMode.repeat
options = [
    repeat
]



class Home(QtWidgets.QMainWindow):

    def __init__(self):
        super(Home, self).__init__()
        uic.loadUi('views/home.ui', self)

         # Create a basic vlc instance
        self.instance = vlc.Instance('--novideo')


        self.model = PlaylistModel()


        self.media_list = self.instance.media_list_new()
        

        self.list_player = self.instance.media_list_player_new()
        self.list_player.set_media_list(self.media_list)
        

        self.player = self.list_player.get_media_player()
        

        self.is_paused = False
        self.player.audio_set_volume(30)
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_ui)


        # self.media = self.instance.media_new('fly.mp3')
        #  # Put the media in the media player
        # self.player.set_media(self.media)
        # # Parse the metadata of the file
        # self.media.parse()
        # print(self.media.get_meta(0))
        # d = self.media.get_duration()
        
        # print(self.duration(d))
        

        # event manager
        self.player.event_manager().event_attach(vlc.EventType.MediaPlayerEndReached, self.track_finished)
        self.player.event_manager().event_attach(vlc.EventType.MediaPlayerPlaying, self.track_playing)
        # self.player.event_manager().event_attach(vlc.EventType.MediaListItemDeleted, self.track_finished)

        self.menuBar = self.findChild(QtWidgets.QMenuBar, 'menuBar')
        self.menuFile = self.findChild(QtWidgets.QMenu, 'menuFile')
        self.actionOpen = self.findChild(QtWidgets.QAction, 'actionOpen')
        self.actionOpen.triggered.connect(self.action_open)

        self.list_view = self.findChild(QtWidgets.QListView, 'listView')
        self.list_view.doubleClicked.connect(self.list_double_clicked)
        self.list_view.setModel(self.model)
        

        self.btn_play_pause = self.findChild(QtWidgets.QPushButton, 'btnPlayPause')
        self.btnPlayPause.clicked.connect(self.play_pause)
        self.btn_play_pause.setText("Play")

        self.btn_prev = self.findChild(QtWidgets.QPushButton, 'btnPrev')
        self.btn_prev.clicked.connect(self.prev)

        self.btn_next = self.findChild(QtWidgets.QPushButton, 'btnNext')
        self.btn_next.clicked.connect(self.skip)

        self.volumeSlider = self.findChild(QtWidgets.QSlider, 'volumeSlider')
        self.volumeSlider.setValue(self.player.audio_get_volume())
        self.volumeSlider.sliderMoved.connect(self.volumeAdjust)

        self.positionslider = self.findChild(QtWidgets.QSlider, 'positionSlider')
        self.positionslider.setMaximum(1000)
        self.positionslider.sliderMoved.connect(self.set_position)
        self.positionslider.sliderPressed.connect(self.set_position)

        self.show()

    def list_double_clicked(self, index):
        print('selected # ' + index)

    def duration(self, ms):
        seconds = ms/1000
        duration = time.strftime('%H:%M:%S', time.gmtime(seconds))
        return duration

    def play_track(self):
        pass

    def track_finished(self, event):
        print('done playback')
        self.positionslider.setValue(0)

    def track_playing(self, event):
        self.btn_play_pause.setText('Pause')
       


    def dragEnterEvent(self, e):
        if e.mimeData().hasFormat('text/uri-list'):
            e.accept()
        else:
            e.ignore()
    
    def dropEvent(self, e):
        # self.setText(e.mimeData().text())
        track = e.mimeData().text()
        track = unquote(urlparse(track).path)
        print(track)
        self.add_to_list(track)
            

    def action_open(self):
        self.openFileNamesDialog()

    def play_pause(self):
        """Toggle play/pause status
        """
        if self.list_player.is_playing():
            self.list_player.pause()
            self.btn_play_pause.setText("Play")
            self.is_paused = True
            self.timer.stop()
        else:
            if self.list_player.play() == -1:
                self.openFileNamesDialog()
                return
            self.list_player.play()
            self.btn_play_pause.setText("Pause")
            self.timer.start()
            self.is_paused = False


    def prev(self):
        self.list_player.previous()

    def skip(self):
        self.list_player.next()
            

    def volumeAdjust(self):
        slider = self.volumeSlider
        self.player.audio_set_volume(slider.value())


    def set_position(self):
        # The vlc MediaPlayer needs a float value between 0 and 1, Qt uses
        # integer variables, so you need a factor; the higher the factor, the
        # more precise are the results (1000 should suffice).

        # Set the media position to where the slider was dragged
        self.timer.stop()
        pos = self.positionslider.value()
        self.player.set_position(pos / 1000.0)
        self.timer.start()

    def stop(self):
        self.player.stop()

    def update_ui(self):
        """Updates the user interface"""

        # Set the slider's position to its corresponding media position
        # Note that the setValue function only takes values of type int,
        # so we must first convert the corresponding media position.
        media_pos = int(self.player.get_position() * 1000)
        self.positionslider.setValue(media_pos)
 
        # No need to call this function if nothing is played
        if not self.player.is_playing():
            self.timer.stop()
 
             # After the video finished, the play button stills shows "Pause",
             # which is not the desired behavior of a media player.
            # This fixes that "bug".
            # if  not self.is_paused:
            #     self.stop()
            self.positionslider.setValue(0)
            self.btn_play_pause.setText('Play')

    def toggle_mute(self):
        is_mute = self.player.audio_get_mute()
        if is_mute:
            self.player.audio_set_mute(False)
        else:
            self.player.audio_set_mute(True)
        # player.audio_toggle_mute()

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;Python Files (*.py)", options=options)
        if fileName:
            print(fileName)
    
    def openFileNamesDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(self,"QFileDialog.getOpenFileNames()", "","All Files (*);;Mp3 Files (*.mp3);; Flac Files (*.flac)", options=options)
        if files:
            for f in files:
                self.add_to_list(f)
    
    def saveFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()","","All Files (*);;Text Files (*.txt)", options=options)
        if fileName:
            print(fileName)


    # add track to playlist and to display model
    def add_to_list(self, path):
        media = self.instance.media_new(path)
        self.media_list.add_media(media)
        media.parse()
        name = media.get_meta(0)
        self.model.tracks.append(name)
        self.model.layoutChanged.emit()
    

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Home()

    # Start the event loop.
    sys.exit(app.exec_())