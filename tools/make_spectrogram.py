import os
import uuid
import argparse
import subprocess 
from pathlib import Path

SAVE_PATH = 'data/spectrograms'
PATH = None
AUDIO_FORMATS = [
    'mp3',
    'wav',
    'acc',
]

# # args
# parser = argparse.ArgumentParser()
# parser.add_argument("input", help="The directory containing audio files")
# parser.add_argument("--duration", help="set audio recording length in seconds", type=int)
# args = parser.parse_args()

# PATH = args.input


def faster_spectrograms(file_paths):
    pass


def audio_to_spectrogram(id, file_path):
    path, filename = os.path.split(file_path)
    filename, ext = os.path.splitext(filename) 
    # out_name = filename + '.png'
    out_name = str(id) + '.png'
    out_path = os.path.join(SAVE_PATH, out_name)
    # uses ffmpeg to make a spectrogram
    s = subprocess.call(["ffmpeg", "-i", file_path, "-lavfi", "showspectrumpic=s=224x224:mode=separate:legend=disabled", "-n", out_path])
    
    
    # delete all spectrogram images stored
def clear_spect_data():
    pass
    

if __name__ == '__main__':  
    for path in Path(PATH).rglob('*.mp3'):
        audio_to_spectrogram(str(path.absolute()))
        pass
    # audio_to_spectrogram('/home/hama/Music/Nicki minaj/nicki swalla.mp3')