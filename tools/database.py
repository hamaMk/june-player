from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
import logging
import os

# conf
Base = declarative_base()

class Track(Base):
    __tablename__ = 'tracks'

    id = Column(Integer, primary_key=True)
    path = Column(String, unique=True)

    def __repr__(self):
        return self.path


class Cluster(Base):
    __tablename__ = 'clusters'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    def __repr__(self):
        return self.name

class ClusterTrack(Base):
    __tablename__ = 'cluster_tracks'

    id = Column(Integer, primary_key=True)
    cluster_name = Column(String)
    track_id = Column(Integer, ForeignKey('tracks.id'))

    def __repr__(self):
        return '{} : {}'.format(cluster_name, track_id)


class Favourite(Base):
    __tablename__ = 'favourites'

    id = Column(Integer, primary_key=True)
    track_id = Column(Integer, ForeignKey('tracks.id'))
    track = relationship(Track)

    def __repr__(self):
        return self.track_id



class JDB:
    def __init__(self):
        self.engine = create_engine('sqlite:///data/june_db.sqlite')
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

        # create tables
        Base.metadata.create_all(self.engine)

    def addTrack(self, path):
        track = Track(path=path)
        self.session.add(track)
        self.session.commit()

    def addTracks(self, paths):
        try:
            for path in paths:
                track = Track(path=path)
                self.session.add(track)
            self.session.commit()
            print('done discovery')
        except:
            self.session.rollback()
            print('something went wrong')

    def getTracks(self):
        tracks = self.session.query(Track).all()
        return tracks

    def addCluster(self, name):
        cluster = Cluster(name=name)
        self.session.add(cluster)
        self.session.commit() #make transaction
        return cluster.id

    def getTrackId(self, path):
            track = self.session.query(Track).filter(Track.path == path).first()
            if track != None:
                return track.id

    def getClusterId(self, name):
            cluster = self.session.query(Cluster).filter(Cluster.name == name).first()
            if cluster != None:
                return cluster.id

    def addToCluster(self, cluster_id, tracks):
        for track in tracks:
            ct = ClusterTrack(cluster_id, track)
            self.session.add(ct)
        self.session.commit()

    def saveClusters(self, name, tracks):
        try:
            for track in tracks:
                path, filename = os.path.split(track)
                track_id, ext = os.path.splitext(filename) 
                logging.debug(track_id)
                ct = ClusterTrack(cluster_name=name, track_id=int(track_id))
                self.session.add(ct)
            self.session.commit()
        except:
            self.session.rollback()
            logging.exception('Something went wrong cl')
        


    def addToFavorites(self):
        pass