import uuid
class SongData:
    def __init__(self, song_title, origina_artist, music_file):
        self.id = uuid.uuid4()
        self.song_title = song_title
        self.original_artist = origina_artist
        self.performer_name = None
        self.vocal_file = None
        self.lyrics_txt = None
        self.lyrics_json = None
        self.original_music_file = music_file
        self.accompanyment_file = None
        self.vocal_file = None

    def set_vocal_file(self, vocal_file):
        self.vocal_file = vocal_file

    def set_lyrics_txt(self, lyrics_txt):
        self.lyrics_txt = lyrics_txt

    def set_lyrics_json(self, lyrics_json):
        self.lyrics_json = lyrics_json

    def set_original_music_file(self, original_music_file):
        self.original_music_file = original_music_file

    def set_accompanyment_file(self, accompaniment_file):
        self.accompanyment_file = accompaniment_file

    def set_vocal_file(self, vocal_file):
        self.vocal_file = vocal_file
    