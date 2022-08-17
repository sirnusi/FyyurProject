#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from datetime import datetime
from flask import (Flask, 
                   render_template, 
                   request, 
                   Response, 
                   flash, 
                   redirect, 
                   url_for)
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import create_database, Venue, Show, Artist
from sqlalchemy import func

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
db = create_database(app)
  
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  areas = Venue.query.distinct(Venue.state, Venue.city).all() 

  data =[]
  for area in areas:
    venues = Venue.query.filter_by(state=area.state).filter_by(city=area.city).all()
    venues_data = []
    for venue in venues:
      upcoming_shows = Show.query.filter_by(venue_id=venue.id).filter(Show.start_time > datetime.today()).all()
      venues_data.append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": len(upcoming_shows),
      })
    data.append({
      "city": area.city,
      "state": area.state,
      "venues": venues_data
    })

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  new = request.form.get('search_term')
  response = Venue.query.filter(Venue.name.ilike(f'%{new}%')).all()
  no_of_response = len(response)
  return render_template('pages/search_venues.html', no_of_response=no_of_response, results=response, search_term=new)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  # venue = Venue.query.filter_by(id=venue_id).first()
  # # data.genres = json.loads(data.genres)
    
  venues = Venue.query.get(venue_id)
  
  data_for_upcoming_shows = db.session.query(Show).join(Venue).filter(
    Show.venue_id==venue_id).filter(Show.start_time>datetime.now()).all()

  upcoming_shows = []
  for shows in data_for_upcoming_shows:
    upcoming_shows.append({
      'artist_id':shows.artist_id,
      'artist_name': shows.artist.name,
      'artist_image_link': shows.artist.image_link,
      'start_time': str(shows.start_time)
    })
  
  data_for_past_shows = db.session.query(Show).join(Venue).filter(Show.venue_id==venue_id).filter(Show.start_time<datetime.now()).all()
  
  past_shows = []
  for shows in data_for_past_shows:
    past_shows.append({
      "artist_id": shows.artist_id,
      "artist_name": shows.artist.name,
      "artist_image_link":shows.artist.image_link,
      "start_time": str(shows.start_time)
    })
  
  venues.upcoming_shows = upcoming_shows
  venues.past_shows = past_shows 
  data={
    'id': venues.id,
    'name': venues.name,
    'genres': venues.genres,
    'address': venues.address,
    'city': venues.city,
    'state': venues.state,
    'phone': venues.phone,
    'website': venues.website,
    'facebook_link': venues.facebook_link,
    'seeking_talent': venues.seeking_talent,
    'seeking_description': venues.seeking_description,
    'image_link': venues.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  } 
  
    
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  # on successful db insert, flash success
  form = VenueForm(request.form)
  try:
    venue = Venue(name=form.name.data, city=form.city.data, 
                  state=form.state.data, address=form.address.data, 
                  phone=form.phone.data, 
                  genres=form.genres.data, 
                  facebook_link=form.facebook_link.data,
                  website=form.website.data, image_link=form.image_link.data,
                  seeking_talent=form.seeking_talent.data,
                  seeking_description=form.seeking_description.data
                )
    db.session.add(venue)
    db.session.commit()

        # flash success if no errors/exceptions
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return redirect(url_for('index'))
  except:
    flash('An error occured. Venue ' + request.form['name'] + ' could not be listed.')
  
  finally:
    db.session.close()
    #TODO: on unsuccessful db insert, flash an error instead.
  # e.g., 
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artist = Artist.query.order_by(Artist.id.desc()).limit(10).all()
 
  
  return render_template('pages/artists.html', artists=artist)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # search for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  
  # search for "band" should return "The Wild Sax Band".
 
  new = request.form.get('search_term')
  response = Artist.query.filter(Artist.name.ilike(f'%{new}%')).all()
  no_of_response = len(response)
  
  return render_template('pages/search_artists.html', results=response, search_term=new, no_of_response=no_of_response)

  
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get(artist_id)
  #artist_genres = [s.strip() for s in artist.genres[1:-1].split(',')]
  
  data_for_upcoming_shows = db.session.query(Show).join(Artist).filter(
    Show.artist_id==artist_id).filter(Show.start_time>datetime.now()).all()
  
  upcoming_shows = []
  for shows in data_for_upcoming_shows:
    upcoming_shows.append({
      'venue_id':shows.venue_id,
      'venue_name':shows.venue.name,
      'venue_image_link':shows.artist.image_link,
      'start_time': str(shows.start_time)
    })
    
  data_for_past_shows = db.session.query(Show).join(Artist).filter(
      Show.artist_id==artist_id).filter(
      Show.start_time<datetime.now()).all()
    
  past_shows = []
  for shows in data_for_past_shows:
    past_shows.append({
      'venue_id':shows.venue_id,
      'venue_name':shows.artist.name,
      'venue_image_link':shows.artist.image_link,
      'start_time': str(shows.start_time)
    })
  artist.upcoming_shows = upcoming_shows
  artist.past_shows = past_shows
    
  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }
 
    
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])

def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = ArtistForm(request.form)
  try:
    artist = Artist(name=form.name.data, city=form.city.data, 
                    state=form.state.data, 
                    phone=form.phone.data,
                    genres=form.genres.data, facebook_link=form.facebook_link.data,
                    website=form.website.data, image_link=form.image_link.data,
                    seeking_venue=form.seeking_venue.data,
                    seeking_description=form.seeking_description.data
                  )
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')       
    return redirect(url_for('index'))
  except:
    flash('An error occured. Venue ' + request.form['name'] + ' could not be listed.')
  
  finally:
    db.session.close()
 # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  
  shows = Show.query.all()
  data = []
  for show in shows:
    data.append({
        "venue_id": show.venue_id,
        "venue_name": show.venue.name,
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": str(show.start_time)
    })
  return render_template('pages/shows.html', shows=data)
    

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():

  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  # on successful db insert, flash success
  form = ShowForm(request.form)
  try:
    show = Show(artist_id=form.artist_id.data,
                venue_id=form.venue_id.data,
                start_time=form.start_time.data
                )
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
   
  finally:
    db.session.close()
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., 
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
