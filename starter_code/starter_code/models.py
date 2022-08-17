from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

#----------------------------------------------------#
#CONFIGURATION
#----------------------------------------------------#

db = SQLAlchemy()

def create_database(app):
    app.config.from_object('config')
    db.app = app
    db.init_app(app)
    migrate = Migrate(app, db)
    return db

class Venue(db.Model):
  __tablename__ = 'venues'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False)
  city = db.Column(db.String(120), nullable=False)
  state = db.Column(db.String(120), nullable=False)
  address = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  genres = db.Column(db.ARRAY(db.String), nullable=False)
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  website = db.Column(db.String(500))
  seeking_talent = db.Column(db.Boolean)
  seeking_description = db.Column(db.String(120))
  artists = db.relationship('Artist', secondary='show', lazy='joined', cascade='all, delete')

  def __repr__(self):
    return f"Venue with the {self.id} is called {self.name}"


class Artist(db.Model):
  __tablename__ = 'artist'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(120), nullable=False)
  city = db.Column(db.String(120), nullable=False)
  state = db.Column(db.String(120), nullable=False)
  phone = db.Column(db.String(120))
  genres = db.Column(db.ARRAY(db.String), nullable=False)

  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  website = db.Column(db.String(500))
  seeking_venue = db.Column(db.Boolean)
  seeking_description = db.Column(db.String(120))
  venue = db.relationship('Venue', secondary='show', lazy='joined', cascade='all, delete')
    
  def __repr__(self):
    return f"Artist name is {self.name}"



class Show(db.Model):
  __tablename__ = 'show'
  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
  start_time = db.Column(db.DateTime, default=datetime.utcnow)
  

  venue = db.relationship(Venue, backref=db.backref("shows", lazy=True))
  artist = db.relationship(Artist, backref=db.backref("shows", lazy=True))
    
  def __repr__(self):
    return f"Artist {self.artists.name} will be performing at {self.venue.name} time is {self.start_time}"