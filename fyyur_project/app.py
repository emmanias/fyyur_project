#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

# from models import Venue, Artist, Shows, VenueGenre, ArtistGenre
from model import *
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import load_only
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

db = SQLAlchemy(app)
migrate = Migrate(app, db)
# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


# db.create_all()

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
# db.create_all()
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@ app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@ app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    data = []
    try:
        period = datetime.datetime.now()
        venLoc = db.session.query(Venue.city.distinct(), Venue.state).all()
        for loc in venLoc:
            city = loc[0]
            state = loc[1]
            loc_dt = {"city": city, "state": state, "venues": []}
            venues = Venue.query.filter_by(city=city, state=state).all()
            for venue in venues:
                venueName = venue.name
                venueId = venue.id
                upcoming_shows = (Shows.query.filter_by(
                    venue_id=venueId).filter(Shows.start_time > period).all())

                venue_dt = {
                    "id": venueId,
                    "name": venueName,
                    "num_upcoming_shows": len(upcoming_shows),
                }

                loc_dt["venues"].append(venue_dt)

            data.append(loc_dt)

    except:
        db.session.rollback()
        return render_template("pages/home.html")

    return render_template('pages/venues.html', areas=data)


@ app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.

    the_query = request.form.get("search_term", "")
    response = {"count": 0,
                "data": []
                }

    items = ['id', 'name']
    results = db.session.query(Venue).filter(Venue.name.ilike(
        f"%{the_query}%")).options(load_only(*items)).all()

    response["count"] = len(results)

    for result in results:
        item = {
            "id": result.id,
            "name": result.name,
        }

        response["data"].append(item)

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@ app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id

    data = {}

    try:
        thevenue = Venue.query.get(venue_id)

        if thevenue is None:
            return not_found_error(404)

        genres = []
        for item in thevenue.genres:
            genres.append(item.genre)

        shows = Shows.query.filter_by(venue_id=venue_id)

        period = datetime.datetime.now()

        thePastshows = shows.filter(Shows.start_time < period).all()
        past_shows = []
        for show in thePastshows:
            artist = Artist.query.get(show.artist_id)
            show_data = {
                "artist_id": artist.id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": str(show.start_time),
            }
            past_shows.append(show_data)

        theUpcomingshows = shows.filter(Shows.start_time >= period).all()
        upcoming_shows = []
        for show in theUpcomingshows:
            artist = Artist.query.get(show.artist_id)
            show_data = {
                "artist_id": artist.id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": str(show.start_time),
            }
            upcoming_shows.append(show_data)

        data = {
            "id": thevenue.id,
            "name": thevenue.name,
            "genres": genres,
            "address": thevenue.address,
            "city": thevenue.city,
            "state": thevenue.state,
            "phone": thevenue.phone,
            "website": thevenue.website,
            "facebook_link": thevenue.facebook_link,
            "seeking_talent": thevenue.seeking_talent,
            "image_link": thevenue.image_link,
            "past_shows": past_shows,
            "upcoming_shows": upcoming_shows,
            "past_shows_count": len(past_shows),
            "upcoming_shows_count": len(upcoming_shows),
        }
    except:
        print("Something went wrong. Please try again.")

    finally:
        db.session.close()
    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@ app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@ app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    try:
        name = request.form.get("name")
        city = request.form.get("city")
        state = request.form.get("state")
        address = request.form.get("address")
        phone = request.form.get("phone")
        genres = request.form.getlist("genres")
        facebook_link = request.form.get("facebook_link")

        venueAdd = Venue(
            name=name,
            city=city,
            state=state,
            address=address,
            phone=phone,
            facebook_link=facebook_link,
        )

        venueAllgenres = []
        for genre in genres:
            genre_dt = VenueGenre(genre=genre)
            genre_dt.venue = venueAdd
            venueAllgenres.append(genre_dt)

        db.session.add(venueAdd)
        db.session.commit()

        db.session.refresh(venueAdd)
        flash("Venue " + venueAdd.name + " was successfully listed!")

    except:
        db.session.rollback()
        flash("An error occurred. Venue " + request.form.get("name") + " could not be listed."
              )

    finally:
        db.session.close()
        return render_template('pages/home.html')

    # on successful db insert, flash success

    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/


@ app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    nameOfVenue = Venue.query.get(venue_id).name
    try:
        nameOfVenueToDelete = db.session.query(
            Venue).filter(Venue.id == venue_id)
        nameOfVenueToDelete.delete()
        db.session.commit()
        flash("Venue: " + nameOfVenue + " was successfully deleted.")

    except:
        db.session.rollback()
        return jsonify(
            {
                "errorMessage": "Sorry! This venue was not successfully deleted. Try again."
            }
        )

    finally:
        db.session.close()
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
        return redirect(url_for("index"))

#  Artists
#  ----------------------------------------------------------------


@ app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    items = ["id", "name"]
    data = db.session.query(Artist).options(load_only(*items)).all()
    return render_template('pages/artists.html', artists=data)


@ app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    query = request.form.get("search_term", "")

    response = {"count": 0, "data": []}

    items = ["id", "name"]
    artist_results = (
        db.session.query(Artist).filter(Artist.name.ilike(
            f"%{query}%")).options(load_only(*items)).all()
    )

    num_upcoming_shows = 0

    response["count"] = len(artist_results)

    for result in artist_results:
        item = {
            "id": result.id,
            "name": result.name,
            "num_upcoming_shows": num_upcoming_shows,
        }
        response["data"].append(item)
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@ app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id

    data = {}
    try:
        artist = Artist.query.get(artist_id)

        if artist is None:
            return not_found_error(404)

        genres = []
        for item in artist.genres:
            genres.append(item.genre)

        shows = Shows.query.filter_by(artist_id=artist_id)

        period = datetime.datetime.now()

        forpastShows = shows.filter(Shows.start_time < period).all()
        thePastShowsList = []
        for show in forpastShows:
            venue = Venue.query.get(show.venue_id)
            show_data = {
                "venue_id": venue.id,
                "venue_name": venue.name,
                "venue_image_link": venue.image_link,
                "start_time": str(show.start_time),
            }
            thePastShowsList.append(show_data)

        forUpcomingShows = shows.filter(Shows.start_time >= period).all()
        theUpcomingShowsList = []
        for show in forUpcomingShows:
            venue = Venue.query.get(show.venue_id)
            show_data = {
                "venue_id": venue.id,
                "venue_name": venue.name,
                "venue_image_link": venue.image_link,
                "start_time": str(show.start_time),
            }
            theUpcomingShowsList.append(show_data)

        data = {
            "id": artist.id,
            "name": artist.name,
            "genres": genres,
            "city": artist.city,
            "state": artist.state,
            "phone": artist.phone,
            "seeking_venue": False,
            "facebook_link": artist.facebook_link,
            "image_link": artist.image_link,
            "past_shows": thePastShowsList,
            "upcoming_shows": theUpcomingShowsList,
            "past_shows_count": len(thePastShowsList),
            "upcoming_shows_count": len(theUpcomingShowsList),
        }

    except:
        flash("Sorry! Something went wrong. Please try again.")

    finally:
        db.session.close()
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@ app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()

    artist = {}
    try:
        artist = Artist.query.get(artist_id)
        print(artists)
        if artists is None:
            return not_found_error(404)

        genres = []
        if len(artist.genres) > 0:
            for item in artist.genres:
                genres.append(item.genre)

        artist = {
            "id": artist.id,
            "name": artist.name,
            "city": artist.city,
            "state": artist.state,
            "phone": artist.phone,
            "genres": genres,
            "facebook_link": artist.facebook_link,
            "seeking_venue": artist.seeking_venue,
            "seeking_description": artist.seeking_description,
            "image_link": artist.image_link,
        }

    except:
        flash("Sorry! Something went wrong. Please try again.")
        return redirect(url_for("index"))

    finally:
        db.session.close()
    # TODO: populate form with fields from artist with ID <artist_id>
        return render_template('forms/edit_artist.html', form=form, artist=artist)


@ app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    defaultImage = "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
    try:
        artistToUpdate = Artist.query.get(artist_id)

        if artistToUpdate is None:
            return not_found_error(404)

        from_form_name = request.form.get("name")
        from_form_city = request.form.get("city")
        from_form_state = request.form.get("state")
        from_form_phone = request.form.get("phone")
        from_form_genres = request.form.getlist("genres")
        from_form_facebook_link = request.form.get("facebook_link")

        artistToUpdate.name = from_form_name
        artistToUpdate.city = from_form_city
        artistToUpdate.state = from_form_state
        artistToUpdate.phone = from_form_phone
        artistToUpdate.facebook_link = from_form_facebook_link
        artistToUpdate.image_link = defaultImage

        genres_for_this_artist = []
        for genre in from_form_genres:
            the_genre = ArtistGenre(genre=genre)
            the_genre.artist = artistToUpdate
            genres_for_this_artist.append(the_genre)

        db.session.add(artistToUpdate)
        db.session.commit()

        db.session.refresh(artistToUpdate)
        flash("Great! The venue was successfully updated!")

    except:
        db.session.rollback()

        flash(
            "An error occurred. Venue "
            + request.form.get("name")
            + " could not be updated."
        )

    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@ app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()

    venue = {}

    try:
        the_venue = Venue.query.get(venue_id)

        if the_venue is None:
            return not_found_error(404)
            # Figure out a better way to do this

        genres = []
        if len(the_venue.genres) > 0:
            for item in the_venue.genres:
                genres.append(item.genre)

        venue = {
            "id": the_venue.id,
            "name": the_venue.name,
            "city": the_venue.city,
            "state": the_venue.state,
            "address": the_venue.address,
            "phone": the_venue.phone,
            "genres": genres,
            "facebook_link": the_venue.facebook_link,
            "seeking_talent": the_venue.seeking_talent,
            "seeking_description": the_venue.seeking_description,
            "image_link": the_venue.image_link,
        }

    except:
        flash("Something went wrong. Please try again.")
        return redirect(url_for("index"))

    finally:
        db.session.close()
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@ app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    try:

        from_form_name = request.form.get("name")
        from_form_city = request.form.get("city")
        from_form_state = request.form.get("state")
        from_form_address = request.form.get("address")
        from_form_phone = request.form.get("phone")
        from_form_genres = request.form.getlist("genres")
        from_form_facebook_link = request.form.get("facebook_link")

        venueToUpdate = Venue.query.get(venue_id)

        venueToUpdate.name = from_form_name
        venueToUpdate.city = from_form_city
        venueToUpdate.state = from_form_state
        venueToUpdate.address = from_form_address
        venueToUpdate.phone = from_form_phone
        venueToUpdate.facebook_link = from_form_facebook_link

        genres_for_venue = []
        for genre in from_form_genres:
            current_genre = VenueGenre(genre=genre)
            current_genre.venue = venueToUpdate
            genres_for_venue.append(current_genre)

            db.session.add(venueToUpdate)
            db.session.commit()

            flash("The venue was updated successfully")

    except:
        db.session.rollback()
        flash("An error occurred. The venue " +
              request.form.get("name") + " could not be updated.")

    finally:
        db.session.close()

    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@ app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@ app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    ###
    try:
        from_form_name = request.form.get("name")
        from_form_city = request.form.get("city")
        from_form_state = request.form.get("state")
        from_form_phone = request.form.get("phone")
        from_form_genres = request.form.getlist("genres")
        from_form_facebook_link = request.form.get("facebook_link")

        new_artist = Artist(
            name=from_form_name,
            city=from_form_city,
            state=from_form_state,
            phone=from_form_phone,
            facebook_link=from_form_facebook_link
        )

        genres_for_this_artist = []
        for genre in from_form_genres:
            the_genre = ArtistGenre(genre=genre)
            the_genre.artist = new_artist
            genres_for_this_artist.append(the_genre)

        db.session.add(new_artist)
        db.session.commit()

        db.session.refresh(new_artist)
        # on successful db insert, flash success
        flash("Artist " + new_artist.name + " was successfully listed!")

    except:
        db.session.rollback()
        flash("An error occurred. The venue artist " +
              request.form.get("name") + " could not be created.")

    finally:
        db.session.close()
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
        return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@ app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.

    data = []
    try:
        shows = Shows.query.all()
        print(shows)
        for show in shows:

            venue_id = show.venue_id
            artist_id = show.artist_id
            artist = Artist.query.get(artist_id)

            show_data = {
                "venue_id": venue_id,
                "venue_name": Venue.query.get(venue_id).name,
                "artist_id": artist_id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": str(show.start_time),
            }

            show_data.append(show_data)

    except:
        db.session.rollback()
        flash("Sorry! Something went wrong, please try again.")
    return render_template('pages/shows.html', shows=data)


@ app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@ app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead

    errors = {"Unknown_artist_id": False, "Unknown_venue_id": False}
    try:
        from_form_artist_id = request.form.get("artist_id")
        from_form_venue_id = request.form.get("venue_id")
        from_form_start_time = request.form.get("start_time")

        the_artist = Artist.query.get(from_form_artist_id)
        if the_artist is None:
            errors["Unknown_artist_id"] = True

        the_venue = Venue.query.get(from_form_venue_id)
        if the_venue is None:
            errors["Unknown_venue_id"] = True

        if the_venue is not None and the_artist is not None:
            new_show = Shows(
                artist_id=the_artist.id,
                venue_id=the_venue.id,
                start_time=from_form_start_time,
            )
            db.session.add(new_show)
            db.session.commit()
            flash(
                "The show by "
                + the_artist.name
                + " has been successfully scheduled at the following venue: "
                + the_venue.name
            )

    except:
        db.session.rollback()
        flash("Something went wrong and the show was not created. Please try again.")

    finally:
        db.session.close()

    if errors["invalid_artist_id"] is True:
        flash(
            "There is no artist with id "
            + request.form.get("artist_id")
            + " in our records"
        )
    elif errors["invalid_venue_id"] is True:
        flash(
            "There is no venue with id "
            + request.form.get("venue_id")
            + " in our records"
        )
    # on successful db insert, flash success
    # flash('The show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@ app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@ app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
