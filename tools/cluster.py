# import make_spectrogram
from database import JDB
from imagecluster import calc, io as icio, postproc


def make_cluster():
    images,fingerprints,timestamps = icio.get_image_data('/home/hama/Documents/projects/playr/data/spectrograms/')
    clusters = calc.cluster(fingerprints, sim=0.5)
    return clusters
    
    # keys = clusters.keys()
    # for key in keys:
    #     cluster_name = key
    #     tracks = clusters.get(key)
    #     db.saveClusters(cluster_name, tracks)