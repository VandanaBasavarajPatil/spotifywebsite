from flask import Flask, render_template, request, redirect, jsonify

from utils.db import db
from sqlalchemy import desc

from models.song import *
from models.StreamedDate import *
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Song.db'


# @app.route('/')
# def index():
#     song = Song.query.all()
#     return render_template('index.html', content=song)

@app.route('/', methods=['GET', 'POST'])
def view_stats():
    # Get the current month and year
    current_month = datetime.datetime.now().month
    current_year = datetime.datetime.now().year

    # Get the search query (if any)
    search_query = request.form.get('search', '')

    # Default to the current month and year
    month = request.form.get('month', current_month)
    year = request.form.get('year', current_year)

    # Query data based on the selected month, year, and search query
    if search_query:
        streamed_data = db.session.query(Song.song_name, Song.artist, StreamedDate.streamed_hours) \
            .join(StreamedDate) \
            .filter((Song.song_name.ilike(f"%{search_query}%")) | (Song.artist.ilike(f"%{search_query}%"))) \
            .filter(StreamedDate.month == int(month), StreamedDate.year == int(year)) \
            .order_by(desc(StreamedDate.streamed_hours)) \
            .all()

    else:
        streamed_data = db.session.query(Song.song_name, Song.artist, StreamedDate.streamed_hours) \
            .join(StreamedDate) \
            .filter(StreamedDate.month == int(month), StreamedDate.year == int(year)) \
            .order_by(desc(StreamedDate.streamed_hours)) \
            .all()

    return render_template('index.html', streamed_data=streamed_data, current_month=current_month,
                           current_year=current_year)


@app.route('/search')
def search():
    return render_template('search.html')


@app.route('/topsongs')
def topsongs():
    return render_template('topsongs.html')


@app.route('/admin')
def get_all_songs():
    song = Song.query.all()
    return render_template('admin.html', content=song)


db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/submit', methods=['POST'])
def submit():
    form_data = request.form.to_dict()
    print(f"form_data: {form_data}")

    song_id = form_data.get('song_id')
    song_name = form_data.get('song_name')
    artist = form_data.get('artist')
    # streamed_hours = form_data.get('streamed_hours')

    song = Song.query.filter_by(song_id=song_id).first()
    if not song:
        song = Song(song_id=song_id, song_name=song_name, artist=artist)
        db.session.add(song)
        db.session.commit()
    print("sumitted successfully")
    return redirect('/admin')


@app.route('/api/add_song_stats', methods=['POST'])
def add_song_stats():
    data = request.get_json()

    song_id = data['song_id']
    year = data['year']
    month = data['month']
    streamed_hours = data['streamed_hours']

    # Save the data to the database
    song_stat = StreamedDate(song_id=song_id, year=year, month=month, streamed_hours=streamed_hours)
    db.session.add(song_stat)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Statistics added successfully'})


@app.route('/api/get_song_stats/<int:song_id>', methods=['GET'])
def get_song_stats(song_id):
    # Query the database for all stats of the song (multiple records)
    stats = db.session.query(StreamedDate.year, StreamedDate.month, StreamedDate.streamed_hours) \
        .filter(StreamedDate.song_id == song_id) \
        .all()

    if stats:
        # Return the list of stats as JSON
        stats_list = [{'year': stat.year, 'month': stat.month, 'streamed_hours': stat.streamed_hours} for stat in stats]
        return jsonify({'success': True, 'stats': stats_list})
    else:
        return jsonify({'success': False, 'message': 'No stats found for this song'})


@app.route('/delete/<int:song_id>', methods=['GET', 'DELETE'])
def delete_song(song_id):
    song = Song.query.get(song_id)
    print("task: {}".format(song))

    if not song:
        return jsonify({'message': 'song not found'}), 404
    try:
        db.session.delete(song)
        db.session.commit()
        return jsonify({'message': 'song deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'An error occurred while deleting the data {}'.format(e)}), 500


@app.route('/update/<int:song_id>', methods=['GET', 'POST'])
def update_song(song_id):
    song = Song.query.get(song_id)

    if not song:
        return jsonify({'message': 'Song not found'}), 404

    if request.method == 'POST':
        form_data = request.form.to_dict()
        song.song_name = form_data.get('song_name')
        song.artist = form_data.get('artist')
        song.streamed_hours = form_data.get('streamed_hours')

        db.session.commit()
        return redirect('/')

    return render_template('update.html', song=song)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5003, debug=True)
