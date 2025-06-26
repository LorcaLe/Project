import time
import os
import pygame
import tkinter as tk
from tkinter import ttk, messagebox
from app_core import MusicPlayerCore

# Color theme
BG = "#121212"
SIDEBAR_BG = "#1e1e1e"
CARD_BG = "#282828"
GREEN = "#1DB954"
WHITE = "#ffffff"
GRAY = "#b3b3b3"

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
    
        self.configure(width=self.width_chars)
       
        if len(text) > self.width_chars:
            self.start_scroll()

    def start_scroll(self):
        self.after_id = self.after(200, self._scroll_text)

    def _scroll_text(self):
        
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

        self.title_scroll_after_id = None  # ← thêm dòng này

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
                self.main_content, text="🎵 Your Library",
                bg=BG, fg=WHITE, font=("Helvetica", 20, "bold")
            )
            title_label.pack(anchor="w", pady=10, padx=10)

            
            self.canvas = tk.Canvas(self.main_content, bg=BG, highlightthickness=0)
            self.scrollbar = ttk.Scrollbar(self.main_content, orient="vertical", command=self.canvas.yview)
            self.canvas.configure(yscrollcommand=self.scrollbar.set)

            self.canvas.pack(side="left", fill="both", expand=True)
            self.scrollbar.pack(side="right", fill="y")
           
            self.grid_frame = tk.Frame(self.canvas, bg=BG)
            self.canvas_frame_id = self.canvas.create_window((0, 0), window=self.grid_frame, anchor="nw")

            self.grid_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
            self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_frame_id, width=e.width))

            
            self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

            self.build_grid()

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

   
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

        
        canvas = tk.Canvas(self.main_content, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.main_content, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg=BG)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.grid_frame = self.scrollable_frame  
        self.build_grid()
            
        canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1*(event.delta/120)), "units"))


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
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
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
        # Hủy scroll cũ
        if self.title_scroll_after_id:
            self.root.after_cancel(self.title_scroll_after_id)
            self.title_scroll_after_id = None

        self.core.load_track(index)
        self.total_time = self.core.total_time        
        self.timeline_var.set(0)
        self.timeline_scale.configure(to=self.total_time)


        title = f"{self.core.tracks[index].name} — {self.core.tracks[index].artist}"
        self.scroll_text = title + "     "
        self.scroll_index = 0  # 💥 Phải reset nếu không chuỗi sẽ nhảy nhanh

        self.animate_title()

        self.status_label.configure(text="Status: Playing")
        self.play_btn.configure(text="⏸")

        self.core.play()
        self.is_playing = True
        self.root.after(500, self.update_progress)

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
        max_chars = 30
        if len(self.scroll_text) <= max_chars:
            self.track_label.config(text=self.scroll_text)
            return

        display = self.scroll_text[self.scroll_index:self.scroll_index + max_chars]
        if len(display) < max_chars:
            display += self.scroll_text[:max_chars - len(display)]

        self.track_label.config(text=display)
        self.scroll_index = (self.scroll_index + 1) % len(self.scroll_text)

        # Trước khi đặt after mới, xóa cái cũ (nếu có)
        if self.title_scroll_after_id:
            self.root.after_cancel(self.title_scroll_after_id)

        # Tạo after mới
        self.title_scroll_after_id = self.root.after(200, self.animate_title)




    def format_time(self, seconds):
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins}:{secs:02d}"