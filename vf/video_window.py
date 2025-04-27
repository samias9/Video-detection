import tkinter as tk
from tkinter import Toplevel, Canvas, ttk
import os

from ui_components import GameButton, COLORS
from yolo_processor import process_video, stop_video, toggle_pause
from confetti_effect import create_confetti_effect

class VideoWindow:
    def __init__(self, app, video_source, objects_to_detect=None):
        self.app = app
        self.video_source = video_source
        self.objects_to_detect = objects_to_detect

        self.create_window()
        self.start_analysis()

    def create_window(self):
        # Création de la fenêtre principale
        self.window = Toplevel()
        self.window.title("Analyse vidéo YOLO")
        self.window.geometry("1000x700")
        self.window.configure(bg=COLORS["background"])

        self.app.center_window(self.window, 1000, 700)

        # En-tête
        title_frame = tk.Frame(self.window, bg=COLORS["dark_bg"], pady=10)
        title_frame.pack(fill=tk.X)

        window_title = tk.Label(
            title_frame,
            text="Détection d'objets en cours",
            font=("Helvetica", 14, "bold"),
            bg=COLORS["dark_bg"],
            fg=COLORS["light_text"]
        )
        window_title.pack()

        # Affichage de la source
        if isinstance(self.video_source, int):
            source_text = "Source: Webcam"
        else:
            source_text = f"Source: {os.path.basename(self.video_source)}"

        source_label = tk.Label(
            self.window,
            text=source_text,
            font=("Helvetica", 10),
            bg=COLORS["background"],
            fg=COLORS["text"]
        )
        source_label.pack(pady=(5, 0))

        # Liste des objets à détecter
        if self.objects_to_detect:
            objects_text = ", ".join(self.objects_to_detect[:5])
            if len(self.objects_to_detect) > 5:
                objects_text += f" et {len(self.objects_to_detect) - 5} autres"

            objects_label = tk.Label(
                self.window,
                text=f"Objets à détecter: {objects_text}",
                font=("Helvetica", 10),
                bg=COLORS["background"],
                fg=COLORS["text"]
            )
            objects_label.pack(pady=(5, 0))

        # Zone d'affichage vidéo
        video_frame = tk.Frame(
            self.window,
            bg=COLORS["dark_bg"],
            padx=3,
            pady=3,
            highlightbackground=COLORS["primary"],
            highlightthickness=2
        )
        video_frame.pack(pady=15)

        self.canvas = Canvas(
            video_frame,
            width=800,
            height=500,
            bg=COLORS["dark_bg"],
            highlightthickness=0
        )
        self.canvas.pack()

        # Barre de progression
        progress_frame = tk.Frame(self.window, bg=COLORS["background"])
        progress_frame.pack(fill=tk.X, padx=50, pady=(5, 15))

        self.progress = ttk.Progressbar(
            progress_frame,
            orient="horizontal",
            length=900,
            mode="indeterminate"
        )
        self.progress.pack(fill=tk.X)
        self.progress.start(10)

        win_frame = tk.Frame(self.window, bg=COLORS["background"])
        win_frame.pack(fill=tk.X, pady=5)

        self.win_label = tk.Label(
            win_frame,
            text="🎉 VICTOIRE ! Tous les objets détectés ! 🎉",
            font=("Helvetica", 14, "bold"),
            bg=COLORS["background"],
            fg=COLORS["text"]
        )
        self.win_label.pack()
        self.win_label.pack_forget()

        # Contrôles vidéo
        control_frame = tk.Frame(self.window, bg=COLORS["background"], pady=10)
        control_frame.pack()

        self.is_paused = {'value': False}

        def toggle_video():
            self.is_paused['value'] = toggle_pause()
            self.btn_toggle.config(text="▶ Play" if self.is_paused['value'] else "⏸ Pause")

        self.btn_toggle = GameButton(
            control_frame,
            text="⏸ Pause",
            command=toggle_video,
            width=15,
            height=1,
            color=COLORS["primary"]
        )
        self.btn_toggle.pack(side=tk.LEFT, padx=10)

        btn_return = GameButton(
            control_frame,
            text="↩ Retour au menu",
            command=lambda: (stop_video(), self.app.show_main_window()),
            width=15,
            height=1,
            color=COLORS["accent"]
        )
        btn_return.pack(side=tk.LEFT, padx=10)

        # Indicateurs
        stats_frame = tk.Frame(self.window, bg=COLORS["background"], pady=10)
        stats_frame.pack()

        if self.objects_to_detect:
            self.detection_label = tk.Label(
                stats_frame,
                text=f"Objets détectés: 0/{len(self.objects_to_detect)}",
                font=("Helvetica", 11),
                bg=COLORS["background"],
                fg=COLORS["text"]
            )
        else:
            self.detection_label = tk.Label(
                stats_frame,
                text="Objets détectés: 0",
                font=("Helvetica", 11),
                bg=COLORS["background"],
                fg=COLORS["text"]
            )
        self.detection_label.pack(side=tk.LEFT, padx=20)

        self.fps_label = tk.Label(
            stats_frame,
            text="FPS: 0",
            font=("Helvetica", 11),
            bg=COLORS["background"],
            fg=COLORS["text"]
        )
        self.fps_label.pack(side=tk.LEFT, padx=20)

    def start_analysis(self):
        # Variables d'état
        self.last_detected_count = [0]
        self.win_shown = [False]

        original_update_label = self.detection_label.config

        def update_detection_label(**kwargs):
            if 'text' in kwargs and self.objects_to_detect:
                try:
                    parts = kwargs['text'].split(': ')[1]
                    current = int(parts.split('/')[0])
                    total = int(parts.split('/')[1])

                    if current == total and current > 0 and not self.win_shown[0]:
                        self.win_shown[0] = True
                        self.win_label.pack()
                        create_confetti_effect(self.app, self.canvas)

                    self.last_detected_count[0] = current
                except Exception as e:
                    print(f"Erreur lors de l'analyse des détections: {e}")

            original_update_label(**kwargs)

        self.detection_label.config = update_detection_label

        # Lancement du traitement vidéo
        try:
            if self.objects_to_detect:
                process_video(
                    self.video_source,
                    self.canvas,
                    self.window,
                    self.detection_label,
                    self.fps_label,
                    self.progress,
                    self.objects_to_detect
                )
            else:
                process_video(
                    self.video_source,
                    self.canvas,
                    self.window,
                    self.detection_label,
                    self.fps_label,
                    self.progress
                )
        except Exception as e:
            print(f"Erreur lors du démarrage du traitement vidéo: {e}")
