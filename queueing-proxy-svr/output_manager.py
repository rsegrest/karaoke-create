from models import db, Song

class OutputManager:
    def add_song_data(self, title, artist, original_file_path):
        new_song = Song(
            title=title,
            artist=artist,
            original_file_path=original_file_path,
            status='queued'
        )
        db.session.add(new_song)
        db.session.commit()
        return new_song

    def get_song_data(self, song_id):
        return Song.query.get(song_id)

    def get_all_song_data(self):
        return Song.query.all()

    def remove_song_data(self, song_id):
        song = Song.query.get(song_id)
        if song:
            db.session.delete(song)
            db.session.commit()

    def find_song_by_title(self, song_title):
        return Song.query.filter_by(title=song_title).all()

    def find_songs_by_original_artist(self, original_artist):
        return Song.query.filter_by(artist=original_artist).all()
    
    def update_song_status(self, song_id, status, **kwargs):
        song = Song.query.get(song_id)
        if song:
            song.status = status
            for key, value in kwargs.items():
                if hasattr(song, key):
                    setattr(song, key, value)
            db.session.commit()
        return song
    
    def update_lyrics_text(self, song_id, lyrics_text):
        song = Song.query.get(song_id)
        if song:
            song.lyrics_text = lyrics_text
            db.session.commit()
        return song
    
    def update_lyrics_json(self, song_id, lyrics_json):
        song = Song.query.get(song_id)
        if song:
            song.lyrics_json = lyrics_json
            db.session.commit()
        return song 

    def update_vocal_file_path(self, song_id, vocal_file_path):
        song = Song.query.get(song_id)
        if song:
            song.vocals_file_path = vocal_file_path
            db.session.commit()
        return song
        
    def update_instrumental_file_path(self, song_id, instrumental_file_path):
        song = Song.query.get(song_id)
        if song:
            song.instrumental_file_path = instrumental_file_path
            db.session.commit()
        return song
    
    def update_original_file_path(self, song_id, original_file_path):
        song = Song.query.get(song_id)
        if song:
            song.original_file_path = original_file_path
            db.session.commit()
        return song
    
    def update_title(self, song_id, title):
        song = Song.query.get(song_id)
        if song:
            song.title = title
            db.session.commit()
        return song
    
    def update_artist(self, song_id, artist):
        song = Song.query.get(song_id)
        if song:
            song.artist = artist
            db.session.commit()
        return song