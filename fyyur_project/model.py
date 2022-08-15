from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=True)
    image_link = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True, default="")
    website = db.Column(db.String(120), nullable=True)
    seeking_talent = db.Column(db.Boolean, nullable=True, default=False)
    seeking_description = db.Column(db.String(120), nullable=True)
    genres = db.relationship("VenueGenre", backref="venue", lazy=True)
    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=True)
    image_link = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    website = db.Column(db.String(120), nullable=True, default="")
    seeking_venues = db.Column(db.Boolean, nullable=True, default=False)
    seeking_description = db.Column(db.String(120), nullable=True, default="")
    genres = db.relationship("ArtistGenre", backref="venue", lazy=True)


class Shows(db.Model):
    __tablename__ = 'shows'
    # id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey(
        "Venue.id"), primary_key=True)
    artists_id = db.Column(db.Integer, db.ForeignKey(
        "Artist.id"), primary_key=True)
    start_time = db.Column(db.DateTime)

    def __repr__(self):
        return f'<Shows  {self.id} {self.venue_id} {self.artists_id} {self.start_time}>'


class VenueGenre(db.Model):
    __tablename__ = "venuegenres"
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"))
    genre = db.Column(db.String(), nullable=True)

    def __repr__(self):
        return f"<VenueGenre venue_id:{self.venue_id} genre: {self.genre}>"

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class ArtistGenre(db.Model):
    __tablename__ = "artistgenres"
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"),)
    genre = db.Column(db.String(), nullable=True)

    def __repr__(self):
        return f"<ArtistGenre artist_id:{self.artist_id} genre: {self.genre}>"
