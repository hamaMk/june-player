import faster_than_walk as ftw
import threading
import logging
# from database import JDB

# sqlite database instance
# db = JDB()
PATH = '/home/hama/Music/'

extensions = [
    '.mp3',
    # '.mp4',
    '.flac',
    '.wav',
    # '.mkv',
    # '.avi',
]

dirs = []

# logging.basicConfig(level=logging.INFO)

# def save_discovered(files):
#     for path in files:
#         db.addTrack(path)
#         pass

# returns list of discovered files
def search():
    return ftw.walk(PATH, extensions)
    

if __name__ == '__main__':
    # id = db.getTrackId('/home/hama/Music/hiphop/Meek Mill, Rick Ross & Wale - Maybach Team (2015) 320 kbps [GloDLS]/06 The Deep End (feat. Pusha T).mp3')
    print('id')
