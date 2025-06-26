import vlc
import time
from mutagen import File 
from app_library import TrackLibrary


instance = vlc.Instance(r'D:\Project\plugins')
player = instance.media_player_new()

class MusicPlayerCore:
    def __init__(self):
        self.library = TrackLibrary()
        self.tracks = self.library.list_tracks()
        self.current_index = None
        self.player = vlc.MediaPlayer()
        self.total_time = 0

    def load_track(self, index):
        self.stop()
        self.current_index = index
        file_path = self.tracks[index].file_path

        media = vlc.Media(file_path)
        self.player.set_media(media)

        audio = File(file_path)
        self.total_time = int(audio.info.length) if audio and audio.info else 0

        # BẮT BUỘC: Phát thử rồi tạm dừng để VLC cập nhật nội dung
        self.player.play()

        # Đợi vài trăm ms cho VLC load media xong
        time.sleep(0.1)  # Đủ cho .get_time() hoạt động

        self.player.set_time(0)  # Reset về đầu
        self.player.pause()      # Dừng lại ở đầu


    def play(self):
        self.player.play()

    def pause(self):
        self.player.pause()

    def stop(self):
        self.player.stop()
    
    def prev_track(self):
        if self.current_index is not None and len(self.tracks) > 0:
            self.current_index = (self.current_index - 1 + len(self.tracks)) % len(self.tracks)
            self.load_track(self.current_index)
            self.play()

    def next_track(self):
        if self.current_index is not None and len(self.tracks) > 0:
            self.current_index = (self.current_index + 1) % len(self.tracks)
            self.load_track(self.current_index)
            self.play()

    def get_position(self):
        pos = self.player.get_time()
        return max(pos / 1000.0, 0)


    def seek(self, seconds):
        self.player.set_time(int(seconds * 1000))

    def set_volume(self, volume):
        self.player.audio_set_volume(int(volume * 100))
    
    