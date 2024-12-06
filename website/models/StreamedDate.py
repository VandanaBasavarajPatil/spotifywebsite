from utils.db import db
from sqlalchemy.orm import relationship

class StreamedDate(db.Model):
    __tablename__ = 'streamed_data'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Auto-incrementing unique ID
    song_id = db.Column(db.Integer, db.ForeignKey('song.song_id'), nullable=False)  # Foreign key referencing Song
    streamed_hours = db.Column(db.Float, nullable=False)  # Hours streamed
    month = db.Column(db.Integer, nullable=False)  # Month (1-12)
    year = db.Column(db.Integer, nullable=False)  # Year (e.g., 2024)

    # Relationship to access the song data
    song = relationship("Song", backref="streamed_data")

    def __repr__(self):
        return f"<StreamedDate(id={self.id}, song_id={self.song_id}, streamed_hours={self.streamed_hours}, month={self.month}, year={self.year})>"
