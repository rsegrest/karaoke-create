class output_manager:
    def __init__(self):
        self.song_data_repo = {}

    def add_song_data(self, song_data):
        self.song_data_repo[song_data.id] = song_data

    def get_song_data(self, song_id):
        return self.song_data_repo.get(song_id)

    def get_all_song_data(self):
        return self.song_data_repo

    def remove_song_data(self, song_id):
        del self.song_data_repo[song_id]

    def find_song_by_title(self, song_title):
        songs_found = []
        for song_data in self.song_data_repo.values():
            if song_data.song_title == song_title:
                songs_found.append(song_data)
        return songs_found 

    def find_songs_by_original_artist(self, original_artist):
        songs_found = []
        for song_data in self.song_data_repo.values():
            if song_data.original_artist == original_artist:
                songs_found.append(song_data)
        return songs_found 
       