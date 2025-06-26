import os
from mutagen import File  
from mutagen.easyid3 import EasyID3  
import time
import os
import pygame
import tkinter as tk
from tkinter import ttk, messagebox
import vlc
from mutagen.mp3 import MP3

BG = "#121212"
SIDEBAR_BG = "#1e1e1e"
CARD_BG = "#282828"
GREEN = "#1DB954"
WHITE = "#ffffff"
GRAY = "#b3b3b3"



class LibraryItem:
    def __init__(self, name, artist, rating=0, file_path=None, duration=0):
        self.name = name
        self.artist = artist
        self.rating = rating
        self.file_path = file_path
        self.play_count = 0
        self.duration = duration
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

                # Sử dụng mutagen để đọc thông tin file
                audio = File(file_path)  
                duration = int(audio.info.length) if audio and audio.info else 0

                # Thử lấy thông tin ID3 của file
                artist = "Unknown Artist"
                title = os.path.splitext(file_name)[0]

                try:
                    tags = EasyID3(file_path)
                    if "artist" in tags:
                        artist = tags["artist"][0]
                    if "title" in tags:
                        title = tags["title"][0]
                except Exception as e:
                    # Nếu không đọc được ID3 thì vẫn dùng tên file
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
    

class MusicPlayerCore:
    def __init__(self):
        self.library = TrackLibrary()
        self.tracks = self.library.list_tracks()
        self.current_index = None
        self.player = vlc.MediaPlayer()
        self.total_time = 0

    def load_track(self, index):
        self.current_index = index
        file_path = self.tracks[index].file_path
        self.player.set_media(vlc.Media(file_path))
        self.total_time = int(MP3(file_path).info.length)

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
        return self.player.get_time() / 1000.0

    def seek(self, seconds):
        self.player.set_time(int(seconds * 1000))

    def set_volume(self, volume):
        self.player.audio_set_volume(int(volume * 100))
    
    
class WelcomeScreen:
    def __init__(self, root, on_enter):
        self.root = root
        self.on_enter = on_enter
        self.frame = tk.Frame(root, bg="#121212")
        self.frame.pack(fill="both", expand=True)

        self.center_container = tk.Frame(self.frame, bg="#121212")
        self.center_container.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            self.center_container, text="Welcome to MusicApp",
            fg="white", bg="#121212", font=("Helvetica", 24, "bold")
        ).pack(pady=10)

        tk.Label(
            self.center_container, text="Click anywhere to start",
            fg="#aaaaaa", bg="#121212", font=("Helvetica", 12, "italic")
        ).pack()

        self.frame.bind("<Button-1>", lambda e: self.fade_out())

        self.root.attributes("-alpha", 1.0)

    def fade_out(self):
        alpha = self.root.attributes("-alpha")
        if alpha > 0:
            self.root.attributes("-alpha", alpha - 0.05)
            self.root.after(30, self.fade_out)
        else:
            self.frame.destroy()
            self.on_enter()
            self.root.attributes("-alpha", 0.0)
            self.fade_in()

    def fade_in(self):
        alpha = self.root.attributes("-alpha")
        if alpha < 1.0:
            self.root.attributes("-alpha", alpha + 0.05)
            self.root.after(30, self.fade_in)

class MarqueeLabel(tk.Label):
    def __init__(self, master, text, width, **kwargs):
        super().__init__(master, text=text, anchor="center", **kwargs)
        self.full_text = text
        self.display_text = text + "   "
        self.width_chars = width
        self.after_id = None
        self.scroll_position = 0

        # Đặt độ rộng cố định để không giãn ra
        self.configure(width=self.width_chars)

        # Nếu text dài hơn, kích hoạt marquee
        if len(text) > self.width_chars:
            self.start_scroll()

    def start_scroll(self):
        self.after_id = self.after(200, self._scroll_text)

    def _scroll_text(self):
        # Cắt text để hiển thị theo từng khung nhỏ
        view = self.display_text[self.scroll_position:self.scroll_position + self.width_chars]
        self.configure(text=view)
        self.scroll_position = (self.scroll_position + 1) % len(self.display_text)
        self.after_id = self.after(200, self._scroll_text)

    def stop_scroll(self):
        if self.after_id:
            self.after_cancel(self.after_id)



class MusicAppUI:
    def __init__(self, root):
        self.root = root
        self.core = MusicPlayerCore()
        self.is_playing = False
        self.total_time = 0
        self.scroll_text = ""
        self.scroll_index = 0


        self.build_ui()
        self.build_main_content()

    def build_ui(self):
        self.root.title("JukeBox — Apple Music Style")
        self.root.geometry("1600x900")
        self.root.configure(bg=BG)

        self.build_top_bar()
        self.build_sidebar()

    def build_top_bar(self):
        self.player_bar = tk.Frame(self.root, bg=SIDEBAR_BG, height=100)
        self.player_bar.pack(side="top", fill="x")

        left = tk.Frame(self.player_bar, bg=SIDEBAR_BG)
        left.pack(side="left", padx=20)

        tk.Label(
            left, text="🍏 MusicApp",
            bg=SIDEBAR_BG, fg=WHITE, font=("Helvetica", 18, "bold")
        ).pack(side="left", padx=10)

        self.prev_btn = ttk.Button(left, text="⏮", command=self.play_previous)
        self.prev_btn.pack(side="left", padx=5)
        self.play_btn = ttk.Button(left, text="▶", command=self.play_pause)
        self.play_btn.pack(side="left", padx=5)
        self.next_btn = ttk.Button(left, text="⏭", command=self.play_next)
        self.next_btn.pack(side="left", padx=5)

        mid = tk.Frame(self.player_bar, bg=SIDEBAR_BG)
        mid.pack(side="left", expand=True)

        self.track_label = tk.Label(
            mid, text="No Track Playing",
            bg=SIDEBAR_BG, fg=WHITE, font=("Helvetica", 14)
        )
        self.track_label.pack(pady=2)

        self.status_label = tk.Label(
            mid, text="Status: Stopped",
            bg=SIDEBAR_BG, fg=GRAY, font=("Helvetica", 10, "italic")
        )
        self.status_label.pack(pady=2)

        self.timeline_var = tk.DoubleVar(value=0)
        self.timeline_scale = ttk.Scale(
            mid, from_=0, to=100, orient="horizontal",
            variable=self.timeline_var, command=self.seek_to_time,
            length=400
        )
        self.timeline_scale.pack(pady=2)

        self.time_label = tk.Label(
            mid, text="0:00 / 0:00",
            bg=SIDEBAR_BG, fg=GRAY, font=("Helvetica", 9)
        )
        self.time_label.pack(pady=2)

        right = tk.Frame(self.player_bar, bg=SIDEBAR_BG)
        right.pack(side="right", padx=20)

        tk.Label(right, text="🔊", bg=SIDEBAR_BG, fg=WHITE, font=("Helvetica", 12)).pack(side="left")

        self.volume_var = tk.DoubleVar(value=0.5)
        self.volume_scale = ttk.Scale(
            right, from_=0, to=1.0, orient="horizontal",
            variable=self.volume_var, command=self.change_volume
        )
        self.volume_scale.pack(side="left")

    def build_main_content(self):
        self.content_frame = tk.Frame(self.root, bg=BG)
        self.content_frame.pack(side="right", fill="both", expand=True)

        self.main_content = tk.Frame(self.content_frame, bg=BG)
        self.main_content.pack(side="left", fill="both", expand=True)

        title_label = tk.Label(
            self.main_content, text="Smart playlists",
            bg=BG, fg=WHITE, font=("Helvetica", 20, "bold")
        )
        title_label.pack(anchor="w", pady=10, padx=10)

        self.grid_frame = tk.Frame(self.main_content, bg=BG)
        self.grid_frame.pack(fill="both", expand=True)

        self.build_grid()
    
    def home_screen(self):
        for widget in self.main_content.winfo_children():
            widget.destroy()

        container = tk.Frame(self.main_content, bg=BG)
        container.place(relx=0.5, rely=0.5, anchor="center")

        title_label = tk.Label(
            container, text="🎵 Welcome to MusicApp",
            bg=BG, fg=WHITE, font=("Helvetica", 24, "bold")
        )
        title_label.pack(pady=10)

    def search_screen(self):
        for widget in self.main_content.winfo_children():
            widget.destroy()

        tk.Label(
            self.main_content, text="🔍 Search Songs",
            bg=BG, fg=WHITE, font=("Helvetica", 20, "bold")
        ).pack(pady=10)

        search_entry = ttk.Entry(self.main_content, width=40)
        search_entry.pack(pady=10)

        search_entry.bind("<Return>", lambda event: self.perform_search(search_entry.get()))

        ttk.Button(
            self.main_content, text="Search", command=lambda: self.perform_search(search_entry.get())
        ).pack()

        self.search_results = tk.Frame(self.main_content, bg=BG)
        self.search_results.pack(pady=10, fill="both", expand=True)

    def perform_search(self, query):
        for widget in self.search_results.winfo_children():
            widget.destroy()

        matches = [
            (i, track)
            for i, track in enumerate(self.core.tracks)
            if query.lower() in track.name.lower() or query.lower() in track.artist.lower()
        ]

        if not matches:
            tk.Label(
                self.search_results, text="No matches found.", bg=BG, fg=GRAY,
                font=("Helvetica", 12, "italic")
            ).pack(pady=10)
            return

        for index, track in matches:
            result = tk.Label(
                self.search_results,
                text=f"{track.name} — {track.artist}",
                bg=BG, fg=WHITE, font=("Helvetica", 12),
                anchor="w", cursor="hand2"
            )
            result.pack(fill="x", padx=10, pady=2)
            result.bind("<Button-1>", lambda e, idx=index: self.select_track(idx))

    def library_screen(self):
        for widget in self.main_content.winfo_children():
            widget.destroy()

        tk.Label(
            self.main_content, text="🎵 Your Library",
            bg=BG, fg=WHITE, font=("Helvetica", 20, "bold")
        ).pack(pady=10)

        self.grid_frame = tk.Frame(self.main_content, bg=BG)
        self.grid_frame.pack(fill="both", expand=True)

        self.build_grid()

    def build_sidebar(self):
        self.sidebar = tk.Frame(self.root, width=200, bg=SIDEBAR_BG)
        self.sidebar.pack(side="left", fill="y")

        for name, icon, action in [
            ("Home", "🏠", self.home_screen),
            ("Search", "🔍", self.search_screen),
            ("Your Library", "🎵", self.library_screen)

        ]:
            btn = tk.Button(
                self.sidebar, text=f"{icon} {name}",
                bg=SIDEBAR_BG, fg=WHITE, relief="flat",
                anchor="w", font=("Helvetica", 12),
                activebackground=CARD_BG, activeforeground=WHITE,
                command=action
            )
            btn.pack(fill="x", padx=10, pady=5)

    def build_grid(self):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        cols = 5
        for c in range(cols):
            self.grid_frame.grid_columnconfigure(c, weight=1)

        for i, track in enumerate(self.core.tracks):
            row, col = divmod(i, cols)

            card = tk.Frame(self.grid_frame, bg=CARD_BG, height=200)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")  # ⬅ sticky để fit
            card.grid_propagate(False)

            cover = tk.Frame(card, bg=GREEN, width=120, height=90)
            cover.pack(pady=10)

            title = MarqueeLabel(
                card, text=track.name, width=22, bg=CARD_BG,
                fg=WHITE, font=("Helvetica", 12, "bold"),
                justify="center"
                )
            title.pack(fill='x')

            artist = MarqueeLabel(
                card, text=track.artist, width=22, bg=CARD_BG,
                fg=GRAY, font=("Helvetica", 10),
                justify="center"
                )
            artist.pack(fill='x')

        
            for widget in (card, cover, title, artist):
                widget.bind("<Button-1>", lambda e, idx=i: self.select_track(idx))

    def select_track(self, index):
        self.core.load_track(index)
        self.total_time = self.core.total_time
        self.timeline_scale.configure(to=self.total_time)
        title = f"{self.core.tracks[index].name} — {self.core.tracks[index].artist}"
        self.scroll_text = title + "     "  # khoảng trắng để tạo khoảng nghỉ khi quay vòng
        self.scroll_index = 0
        self.animate_title()


        self.status_label.configure(text="Status: Playing")
        self.play_btn.configure(text="⏸")

        self.core.play()
        self.is_playing = True
        self.update_progress()

    def play_pause(self):
        if self.core.current_index is None:
            messagebox.showinfo("Info", "No track is selected!")
        elif self.is_playing:
            self.core.pause()
            self.status_label.configure(text="Status: Paused")
            self.play_btn.configure(text="▶")
            self.is_playing = False
        else:
            self.core.pause()
            self.status_label.configure(text="Status: Playing")
            self.play_btn.configure(text="⏸")
            self.is_playing = True
            self.update_progress()

    def play_previous(self):
        self.core.prev_track()
        self.select_track(self.core.current_index)

    def play_next(self):
        self.core.next_track()
        self.select_track(self.core.current_index)

    def change_volume(self, event=None):
        self.core.set_volume(self.volume_var.get())

    def seek_to_time(self, event=None):
        if self.core.current_index is not None:
            target_time = self.timeline_var.get()
            self.core.seek(target_time)

    def update_progress(self):
        if self.is_playing and self.core.current_index is not None:
            self.current_time = self.core.get_position()
            self.timeline_var.set(self.current_time)
            self.time_label.configure(
                text=f"{self.format_time(self.current_time)} / {self.format_time(self.total_time)}"
            )
            self.root.after(500, self.update_progress)
    
    def animate_title(self):
        max_chars = 30  # số lượng ký tự hiển thị trong nhãn
        if len(self.scroll_text) <= max_chars:
            self.track_label.config(text=self.scroll_text)
            return

        display = self.scroll_text[self.scroll_index:self.scroll_index + max_chars]
        if len(display) < max_chars:
            display += self.scroll_text[:max_chars - len(display)]
        self.track_label.config(text=display)
        self.scroll_index = (self.scroll_index + 1) % len(self.scroll_text)
        self.root.after(200, self.animate_title)


    def format_time(self, seconds):
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins}:{secs:02d}"
    
def center_window(root, width=1600, height=900):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = int((screen_width - width) / 2)
    y = int((screen_height - height) / 2)
    root.geometry(f"{width}x{height}+{x}+{y}")

# Outside the class:
if __name__ == "__main__":
    root = tk.Tk()
    center_window(root, 1600, 900)  # 👈 Gọi hàm này trước khi hiển thị cửa sổ
    def start_app():
        MusicAppUI(root)
    WelcomeScreen(root, on_enter=start_app)
    root.mainloop()

