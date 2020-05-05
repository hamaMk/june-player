from PyQt5 import QtCore

class PlaylistModel(QtCore.QAbstractListModel):
    def __init__(self, *args, tracks=None, **kwargs):
        super(PlaylistModel, self).__init__(*args, **kwargs)
        self.tracks = tracks or []

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            text = self.tracks[index.row()]
            return text

    def rowCount(self, index):
        return len(self.tracks)

