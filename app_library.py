import os
from mutagen import File  # thư viện mutagen tự nhận dạng file
from mutagen.easyid3 import EasyID3  # lấy tag MP3 (title, artist,...)

class LibraryItem:
    
    def __init__(self, name, artist, rating=0, file_path=None, duration=0):
        self.name = name
        self.artist = artist
        self.rating = rating
        self.file_path = file_path
        self.play_count = 0
        self.duration = duration  # giây

    def stars(self):
        return "★" * self.rating

class TrackLibrary:
    
    def __init__(self):
        self.library = {}
        self.load_tracks_from_folder()

    def load_tracks_from_folder(self):

        folder_path = r"D:\Project\music"
        for file_name in os.listdir(folder_path):
            if file_name.lower().endswith((".mp3", ".wav", ".ogg")):
                file_path = os.path.join(folder_path, file_name)

                audio = File(file_path)  
                duration = int(audio.info.length) if audio and audio.info else 0

                artist = "Unknown Artist"
                title = os.path.splitext(file_name)[0]

                try:
                    tags = EasyID3(file_path)
                    if "artist" in tags:
                        artist = tags["artist"][0]
                    if "title" in tags:
                        title = tags["title"][0]
                except Exception as e:
                 
                    pass

                new_id = str(len(self.library) + 1).zfill(2)
                self.library[new_id] = LibraryItem(
                    name=title,
                    artist=artist,
                    file_path=file_path,
                    duration=duration
                )

    def list_tracks(self):
        return list(self.library.values())

    def search(self, keyword):
        return [
            item for item in self.library.values()
            if keyword.lower() in item.name.lower() or keyword.lower() in item.artist.lower()
        ]