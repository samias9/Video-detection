import tkinter as tk
from tkinter import Canvas
import os
import threading
import random

from ui_components import GameButton, CircleIconButton, COLORS, load_icon
from game_manager import GameManager
from video_window import VideoWindow
from dialogs import show_ready_dialog

class VideoApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Analyseur Vidéo YOLO")
        self.root.geometry("800x600")
        self.root.configure(bg=COLORS["background"])
        self.root.resizable(True, True)

        self.player1_name = "Joueur 1"
        self.player2_name = "Joueur 2"
        self.player1_score = 0
        self.player2_score = 0
        self.current_player = 1
        self.remaining_time = 10
        self.timer_active = False
        self.timer_id = None

        self.player1_completed = False
        self.player2_completed = False
        self.player1_time = 0
        self.player2_time = 0
        self.max_time = 60

        self.game_manager = GameManager(self)

        self.thread_lock = threading.Lock()
        self.player_switch_in_progress = False

        self.center_window(self.root, 900, 700)

        if not os.path.exists("icons"):
            os.makedirs("icons")

        self.icons = {}
        self.confetti_particles = []
        self.confetti_active = False

        self.load_all_icons()
        self.create_main_window()

    def load_all_icons(self):
        icon_files = {
            "play": "play.png",
            "pause": "pause.png",
            "video": "video.png",
            "webcam": "webcam.png",
            "stop": "stop.png",
            "return": "return.png"
        }

        for name, filename in icon_files.items():
            self.icons[name] = load_icon(filename, size=(32, 32))

    def center_window(self, window, width, height):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        window.geometry(f"{width}x{height}+{x}+{y}")

    def create_main_window(self):
        top_bar = tk.Frame(self.root, bg="#2c3e50", height=40)
        top_bar.pack(fill=tk.X)

        btn_red = tk.Frame(top_bar, bg="#e74c3c", width=15, height=15, bd=0, relief=tk.RAISED)
        btn_red.place(x=15, y=12)
        btn_yellow = tk.Frame(top_bar, bg="#f1c40f", width=15, height=15, bd=0, relief=tk.RAISED)
        btn_yellow.place(x=45, y=12)
        btn_green = tk.Frame(top_bar, bg="#2ecc71", width=15, height=15, bd=0, relief=tk.RAISED)
        btn_green.place(x=75, y=12)

        title_label = tk.Label(
            top_bar,
            text="Analyseur Vidéo YOLO",
            font=("Arial", 14),
            bg="#2c3e50",
            fg="white"
        )
        title_label.pack(pady=8)

        main_canvas = Canvas(
            self.root,
            width=800,
            height=560,
            highlightthickness=0
        )
        main_canvas.pack(fill=tk.BOTH, expand=True)

        from forest_background import ForestBackground
        background = ForestBackground(main_canvas, 900, 660)

        from forest_badge import create_forest_badge
        badge = create_forest_badge(main_canvas, 280, 10, 150, 150, "Finder")

        button_container = tk.Frame(
            main_canvas,
            bg=COLORS["forest_green"],
            bd=4,
            relief=tk.RIDGE,
            highlightbackground=COLORS["button_border"],
            highlightthickness=4
        )
        button_container.place(relx=0.5, rely=0.6, anchor=tk.CENTER, width=400, height=200)

        button_frame = tk.Frame(button_container, bg=COLORS["forest_green"], bd=0)
        button_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        video_btn = GameButton(
            button_frame,
            text="Choisir une vidéo",
            command=self.game_manager.select_file,
            width=20,
            height=2,
            color="#FF9800"
        )
        video_btn.pack(pady=10)

        webcam_btn = GameButton(
            button_frame,
            text="Utiliser la webcam",
            command=lambda: show_ready_dialog(self),
            width=20,
            height=2,
            color="#FFC107"
        )
        webcam_btn.pack(pady=10)

    def hide_main_window(self):
        self.root.withdraw()

    def show_main_window(self):
        self.root.deiconify()

    def run(self):
        self.root.mainloop()
