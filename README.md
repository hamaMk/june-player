# june-player
AI powered music player built with python and Qt5

The june-player uses a deep learning model to group your songs into several groups according to similarities between the songs. After discovering all the songs in your system, images(Spectrogram) representing each of the songs are created in a temporary directory, these are then supplied to the deep learning model and the results are sets of similar songs whose references are then stored in a SQlite database.

### Why
During playback, if you stumble upon a song you like simply activate the ai playlist on the song and the following songs will be in the same group as the one you like and may sound somewhat similar.


## Platform Support
This program was built and tested on linux.


## Requirements
tensorflow
keras
scikit-learn
python-vlc
PyQt5
Pillow 
faster-than-walk
