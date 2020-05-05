from PyQt5 import QtCore

class PlaylistModel(QtCore.QAbstractListModel):
    def __init__(self, *args, todos=None, **kwargs):
        super(PlaylistModel, self).__init__(*args, **kwargs)
        self.todos = todos or []

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            status, text = self.todos[index.row()]
            return text

    def rowCount(self, index):
        return len(self.todos)


class Track:
    def __init__(self, path):
        # self.title = title
        self.path = path

class Playlist:
    def __init__(self):
        self.current_track_id = 0
        self.tracks = []

    def add(self, track):
        self.tracks.append(track)

    def remove(self, track_id):
        self.tracks.pop(track_id)

    def get(self, track_id=0):
        # make sure value exists in playlist
        self.current_track_id = track_id
        return self.tracks[track_id]

    def get_playing(self):
        return self.current_track_id
    
    def next(self):
        if not self.has_next():
            print('no more media')
            return None
        return self.get(self.current_track_id + 1)
    
    def prev(self):
        if not self.has_next():
            print('no more media')
            return None
        return self.get(self.current_track_id - 1)

    def clear(self):
        self.tracks.clear()

    def has_next(self):
        if len(self.tracks) > self.current_track_id:
            return True
        return False