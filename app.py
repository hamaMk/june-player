from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtWidgets import QFileDialog
import os
import sys
import vlc
from urllib.parse import urlparse, unquote
from models import PlaylistModel
import time
import datetime
import pwd
from tools.database import JDB
from tools import discover, make_spectrogram, constants
import logging
from tools.imagecluster import calc, io as icio, postproc
import uuid
import faster_than_walk as ftw


# logging conf
logging.basicConfig(level=logging.DEBUG)    

# sqlite database instance
db = JDB()

def get_username():
    return pwd.getpwuid( os.getuid() )[ 0 ]

# playback options
default = vlc.PlaybackMode.default
loop = vlc.PlaybackMode.loop
repeat = vlc.PlaybackMode.repeat
options = [
    repeat
]


class SmartPList():
    def __init__(self):
        pass
        # discover 
        # make spectrograms 
        # make clusters and save

    



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

        self.playlist_showing = False

        # event manager
        self.player.event_manager().event_attach(vlc.EventType.MediaPlayerEndReached, self.track_finished)
        self.player.event_manager().event_attach(vlc.EventType.MediaPlayerPlaying, self.track_playing)

        # self.player.event_manager().event_attach(vlc.EventType.MediaListItemDeleted, self.track_finished)

        self.menuBar = self.findChild(QtWidgets.QMenuBar, 'menuBar')
        self.menuFile = self.findChild(QtWidgets.QMenu, 'menuFile')
        self.actionOpen = self.findChild(QtWidgets.QAction, 'actionOpen')
        self.actionOpen.triggered.connect(self.action_open)
        self.actionSmartPList = self.findChild(QtWidgets.QAction, 'actionSmartPList')
        self.actionSmartPList.triggered.connect(self.start_smart_playlist)

        self.list_view = self.findChild(QtWidgets.QListView, 'listView')
        self.list_view.doubleClicked.connect(self.list_double_clicked)
        self.list_view.setModel(self.model)
        self.list_view.hide()

        self.btn_show_plist = self.findChild(QtWidgets.QPushButton, 'btnShowPList')
        self.btn_show_plist.clicked.connect(self.show_playlist)

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

        self.lbl_duration = self.findChild(QtWidgets.QLabel, 'lblDuration')

        self.positionslider = self.findChild(QtWidgets.QSlider, 'positionSlider')
        self.positionslider.setMaximum(1000)
        self.positionslider.sliderMoved.connect(self.set_position)
        self.positionslider.sliderPressed.connect(self.set_position)

        self.show()

    def show_playlist(self):
        view = self.list_view
        if self.playlist_showing:
            view.hide()
            self.playlist_showing = False
        else:
            view.show()
            self.playlist_showing = True

    def start_smart_playlist(self):
        tracks = discover.search()
        logging.debug('Found: ' + str(len(tracks)) + ' tracks in library')
        db.addTracks(tracks)
        logging.debug('Done disovery')

        # logging.debug('Making spectrograms ...')
        # files = db.getTracks()
        # logging.debug('Found: {}'.format(str(len(files))))
        # logging.debug(type(files[0].path))
        # for t in range(0, len(files)):
        #     make_spectrogram.audio_to_spectrogram(files[t].id, files[t].path)
        #     logging.debug('Done '.format(str(t)))
        # logging.debug('Done spectrograms')

        self.make_cluster()



    def make_cluster(self):
        logging.debug('Clustering files ...')
        images,fingerprints,timestamps = icio.get_image_data('/home/hama/Documents/projects/playr/data/spectrograms')
        # logging.debug('Sub-clusters found: {} {}'.format(images, fingerprints))
        if images == None or fingerprints == None:
            logging.error('No spectrograms found')
            return
        clusters = calc.cluster(fingerprints, sim=0.5)

        for csize, group in clusters.items():
            logging.debug('Sub-clusters found: '.format(csize))
            for iclus, cluster in enumerate(group):
                cluster_name = str(uuid.uuid4())
                # for track in cluster:
                db.saveClusters(cluster_name, cluster)

        logging.debug('Clustering completed')



    def save_discovered(self, files):
        saved_tracks = db.getTracks()
        # save only files that are not already saved
        tracks = list(set(files).difference(set(saved_tracks)))
        print('Found: ' + str(len(tracks)) + ' tracks in library')
        db.addTracks(tracks)

    def list_double_clicked(self, index):
        self.list_player.play_item_at_index(index.row())

    def duration(self, ms):
        seconds = ms/1000
        duration = time.strftime('%H:%M:%S', time.gmtime(seconds))
        return duration

    def play_track(self):
        pass

    def track_finished(self, event):
        print('done playback')
    

    def track_playing(self, event):
        self.btn_play_pause.setText('Pause')
        # highlight currently playing track in playlist view
        self.list_view


        # set duration
        duration = self.duration(self.list_player.get_media_player().get_media().get_duration())
        self.lbl_duration.setText(duration)

       


    def dragEnterEvent(self, e):
        # fix me !!! create custom mimedata to handle file paths properly
        if e.mimeData().hasFormat('text/uri-list'):
            e.accept()
        else:
            e.ignore()
    
    def dropEvent(self, e):
        tracks = e.mimeData().urls()
        for track in tracks:
            track = track.toDisplayString()
            self.add_to_list(track)
        if not self.list_player.is_playing():
            self.player.audio_set_volume(30)
            self.play()
            

    def action_open(self):
        self.openFileNamesDialog()

    def play(self):
        self.list_player.play()
        self.btn_play_pause.setText("Pause")
        self.timer.start()
        self.is_paused = False


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
            self.play()


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
        dialog = QFileDialog
        default_dir = '/home/{0}/Music'.format(get_username())
        files, _ = QFileDialog.getOpenFileNames(self,"QFileDialog.getOpenFileNames()", default_dir,"All Files (*);;Mp3 Files (*.mp3);; Flac Files (*.flac)", options=options)
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
        path = path.replace("file://", "")
        # check if the path if the path is a file or a directory
        if os.path.isdir(path):
            tracks = ftw.walk(path, constants.extensions)
            for track in tracks:
                self.add(track)
        else:
            self.add(path)

    def add(self, path):
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