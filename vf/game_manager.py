import tkinter as tk
from tkinter import filedialog
import random

from yolo_processor import get_detectable_objects
from game_window import GameWindow
from video_window import VideoWindow
from object_selector import show_selected_objects

class GameManager:
    def __init__(self, app):
        self.app = app

    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Sélectionner une vidéo",
            filetypes=[
                ("Vidéos", "*.mp4 *.avi *.mov *.mkv"),
                ("Tous les fichiers", "*.*")
            ]
        )
        if not file_path:
            return

        self.app.hide_main_window()
        self.open_video_window(file_path)

    def select_random_objects(self):
        # Liste d'objets courants dans une maison
        home_objects = [
            "person", "chair", "sofa", "bed", "dining table", "toilet", "tv",
            "laptop", "mouse", "remote", "keyboard", "cell phone", "microwave",
            "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase",
            "scissors", "teddy bear", "hair drier", "toothbrush", "cup", "fork",
            "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange",
            "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "bottle"
        ]

        # Filtrer selon les objets détectables par YOLO
        detectable_objects = get_detectable_objects()
        available_home_objects = [obj for obj in home_objects if obj in detectable_objects]

        # Sélection aléatoire de 5 objets maximum
        num_objects = min(5, len(available_home_objects))
        selected_objects = random.sample(available_home_objects, num_objects)

        # Afficher les objets sélectionnés à l'utilisateur
        show_selected_objects(self.app, selected_objects)

    def start_game_with_objects(self, objects_to_detect, player1_name, player2_name):
        # Préparation du jeu
        self.app.hide_main_window()

        # Configuration des joueurs
        self.app.player1_name = player1_name
        self.app.player2_name = player2_name
        self.app.player1_score = 0
        self.app.player2_score = 0
        self.app.current_player = 1

        # Réinitialisation des états
        self.app.player1_completed = False
        self.app.player2_completed = False
        self.app.player1_time = 0
        self.app.player2_time = 0
        self.app.remaining_time = self.app.max_time

        # Lancement de la fenêtre de jeu
        self.open_game_window(0, objects_to_detect)  # 0 = webcam

    def open_game_window(self, video_source, objects_to_detect):
        # Création de la fenêtre de jeu
        GameWindow(self.app, video_source, objects_to_detect)

    def open_video_window(self, video_source, objects_to_detect=None):
        # Création de la fenêtre d'analyse vidéo
        VideoWindow(self.app, video_source, objects_to_detect)
