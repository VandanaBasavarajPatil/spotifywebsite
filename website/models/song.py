from utils.db import db
from models.StreamedDate import StreamedDate

class Song(db.Model):# Specify the table name

    # Defining the columns for the table
    song_id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Unique ID for each song
    song_name = db.Column(db.String(255), nullable=False)  # Name of the song
    artist = db.Column(db.String(255), nullable=False)  # Name of the artist
    #streamed_hours = db.Column(db.Integer, nullable=False)  # Total streamed hours