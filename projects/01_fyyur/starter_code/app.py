# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import logging
from datetime import datetime as date
from logging import Formatter, FileHandler

import babel
import dateutil.parser
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

from forms import *
from models import db, Venue, Artist, Show

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
db.init_app(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123456@localhost/Fyrr'


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues', methods=['GET'])
def venues():
    venues = Venue.query.all()
    data = []
    for venue in venues:
        data.append({
            'city': venue.city,
            'state': venue.state,
            'venues': []
        })

        for v in data:
            if venue.city == v['city'] and venue.state == v['state']:
                v['venues'].append({
                    'id': venue.id,
                    'name': venue.name,
                    'num_upcoming_shows': 0
                })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    data = []
    search_term = request.form.get('search_term', '')
    results = Venue.query.filter(Venue.name.ilike(f"%{search_term}%"))
    for venue in results:
        count = db.session.query(func.count(Show.id)).group_by(Show.venue_id).having(Show.venue_id == venue.id).scalar()
        data.append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": count
        })
        print(count)

    response = {
        "count": len(data),
        "data": data
    }
    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.get(venue_id)

    all_upcoming_shows = db.session.query(Show).join(Venue).filter(Show.venue_id == venue_id).filter(
        Show.start_time > datetime.now()).all()
    upcoming_shows = []
    all_past_shows = db.session.query(Show).join(Venue).filter(Show.venue_id == venue_id).filter(
        Show.start_time > datetime.now()).all()
    past_shows = []
    for show in all_past_shows:
        past_shows.append(
            {
                "artist_id": show.artist_id,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": date.isoformat(show.start_time)
            }
        )
    for show in all_upcoming_shows:
        upcoming_shows.append({
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": date.isoformat(show.start_time)
        })

    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website_link,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }
    data = list(filter(lambda d: d['id'] == venue_id, [data]))[0]
    return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm(request.form)
    try:
        venue = Venue(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            address=form.address.data,
            phone=form.phone.data,
            genres=",".join(request.form.getlist('genres')),
            facebook_link=form.facebook_link.data,
            image_link=form.image_link.data,
            website_link=form.website_link.data,
            seeking_talent=form.seeking_talent.data,
            seeking_description=form.seeking_description.data
        )
        db.session.add(venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
        db.session.rollback()
    finally:
        db.session.close()
        return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    return None


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    data = Artist.query.all()
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    data = []
    search_term = request.form.get('search_term', '')
    results = Artist.query.filter(Artist.name.ilike(f"%{search_term}%"))
    for artist in results:
        count = db.session.query(func.count(Show.id)).group_by(Show.artist_id).having(
            Show.artist_id == artist.id).scalar()
        data.append({
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": count
        })
    response = {
        "count": len(data),
        "data": data
    }
    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.get(artist_id)
    all_upcoming_shows = db.session.query(Show).join(Venue).filter(Show.artist_id == artist_id).filter(
        Show.start_time > datetime.now()).all()
    upcoming_shows = []
    all_past_shows = db.session.query(Show).join(Venue).filter(Show.artist_id == artist_id).filter(
        Show.start_time > datetime.now()).all()
    past_shows = []

    for show in all_past_shows:
        past_shows.append(
            {
                "venue_id": show.venue_id,
                "venue_name": show.venue.name,
                "venue_image_link": show.venue.image_link,
                "start_time": date.isoformat(show.start_time)
            }
        )
    for show in all_upcoming_shows:
        upcoming_shows.append({
            "venue_id": show.artist_id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": date.isoformat(show.start_time)
        })

    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website_link,
        "facebook_link": artist.facebook_link,
        "image_link": artist.image_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }
    data = list(filter(lambda d: d['id'] == artist_id, [data]))[0]
    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    an_artist = Artist.query.get(artist_id)
    form.name.data = an_artist.name
    form.phone.data = an_artist.phone
    form.genres.data = an_artist.genres.split(",")
    form.facebook_link.data = an_artist.facebook_link
    form.image_link.data = an_artist.image_link
    form.state.data = an_artist.state
    form.city.data = an_artist.city
    form.website_link.data = an_artist.website_link
    form.seeking_description.data = an_artist.seeking_description
    form.seeking_venue.data = an_artist.seeking_venue
    artist = {
        "id": an_artist.id,
        "name": an_artist.name,
        "genres": an_artist.genres,
        "city": an_artist.city,
        "state": an_artist.state,
        "phone": an_artist.phone,
        "website": an_artist.website_link,
        "facebook_link": an_artist.facebook_link,
        "seeking_venue": an_artist.seeking_venue,
        "seeking_description": an_artist.seeking_description,
        "image_link": an_artist.image_link
    }
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    an_artist = Artist.query.get(artist_id)
    form = ArtistForm()
    try:
        an_artist.name = form.name.data,
        an_artist.city = form.city.data,
        an_artist.state = form.state.data,
        an_artist.phone = form.phone.data,
        an_artist.image_link = form.image_link.data,
        an_artist.genres = " ".join(form.genres.data),
        an_artist.facebook_link = form.facebook_link.data,
        an_artist.website_link = form.website_link.data,
        an_artist.seeking_venue = form.seeking_venue.data,
        an_artist.seeking_description = form.seeking_description.data
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.phone.data = venue.phone
    form.address.data = venue.address
    form.genres.data = venue.genres.split(",")
    form.facebook_link.data = venue.facebook_link
    form.image_link.data = venue.image_link
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description

    venue = {
        "id": venue.id,
        "name": form.name.data,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website_link,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link
    }
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    a_venue = Venue.query.get(venue_id)
    form = request.form
    try:
        a_venue.name = form['name'],
        a_venue.city = form['city'],
        a_venue.state = form['state'],
        a_venue.address = form['address'],
        a_venue.phone = form['phone'],
        a_venue.genres = ",".join(request.form.getlist('genres')),
        a_venue.facebook_link = form['facebook_link'],
        a_venue.image_link = form['image_link'],
        a_venue.website_link = form['website_link'],
        a_venue.seeking_talent = form['seeking_talent'],
        a_venue.seeking_description = form['seeking_description']
        print(a_venue)
        db.session.commit()
    except:
        print(a_venue)
        db.session.rollback()
    finally:
        print(a_venue)
        db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    form = ArtistForm(request.form)
    try:
        artist = Artist(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            phone=form.phone.data,
            image_link=form.image_link.data,
            genres=" ".join(form.genres.data),
            facebook_link=form.facebook_link.data,
            website_link=form.website_link.data,
            seeking_venue=form.seeking_venue.data,
            seeking_description=form.seeking_description.data
        )
        db.session.add(artist)
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
        db.session.rollback()
    finally:
        db.session.close()
        return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    all_shows = Show.query.all()
    data = []
    for show in all_shows:
        venue = Venue.query.get(show.venue_id)
        artist = Artist.query.get(show.artist_id)
        data.append({
            "venue_id": show.venue_id,
            "venue_name": venue.name,
            "artist_id": show.artist_id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": date.isoformat(show.start_time)
        })

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    form = ShowForm(request.form)
    try:
        show = Show(
            artist_id=form.artist_id.data,
            venue_id=form.venue_id.data,
            start_time=form.start_time.data,
        )
        db.session.add(show)
        db.session.commit()
        flash('Show was successfully listed!')
    except:
        flash('An error occurred. Show could not be listed.')
        db.session.rollback()
    finally:
        db.session.close()
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

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
