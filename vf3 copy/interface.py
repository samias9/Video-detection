import tkinter as tk
from tkinter import filedialog, Toplevel, Canvas, ttk, scrolledtext
from yolo_processor import process_video, stop_video, toggle_pause, get_detectable_objects, get_detected_objects_list, reset_detected_objects
from ui_components import TextOnlyButton, ObjectCheckButton, COLORS, load_icon, create_placeholder_icon
from confetti import Confetti
from PIL import Image, ImageTk
import random
import os
import threading
import time

class VideoApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Analyseur Vidéo YOLO")
        self.root.geometry("700x550")
        self.root.configure(bg=COLORS["background"])
        self.root.resizable(True, True)


        # Variables pour le jeu à deux joueurs
        self.player1_name = "Joueur 1"
        self.player2_name = "Joueur 2"
        self.player1_score = 0
        self.player2_score = 0
        self.current_player = 1
        self.remaining_time = 10
        self.timer_active = False
        self.timer_id = None

        self.player1_completed = False  # Si le joueur 1 a trouvé tous les objets
        self.player2_completed = False  # Si le joueur 2 a trouvé tous les objets
        self.player1_time = 0  # Temps utilisé par le joueur 1 (si a tout trouvé)
        self.player2_time = 0  # Temps utilisé par le joueur 2 (si a tout trouvé)
        self.current_player = 1
        self.remaining_time = 60
        self.max_time = 60  # Temps maximum par joueur

        # Ajout d'un verrou pour synchroniser les threads
        self.thread_lock = threading.Lock()

        # Indicateur pour savoir si un changement de joueur est en cours
        self.player_switch_in_progress = False

        # Référence au thread de traitement vidéo
        self.video_thread = None

        # Centre la fenêtre sur l'écran
        self.center_window(self.root, 700, 550)

        # Création du dossier d'icônes s'il n'existe pas
        if not os.path.exists("icons"):
            os.makedirs("icons")
            print("Dossier 'icons' créé")

        # Variables pour stocker les références aux icônes (important!)
        self.icons = {}

        # Confettis actifs
        self.confetti_particles = []
        self.confetti_active = False

        # Tentative de chargement des icônes
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
        # Barre supérieure (titre de l'application)
        top_bar = tk.Frame(self.root, bg="#2c3e50", height=30)
        top_bar.pack(fill=tk.X)

        # Indicateurs colorés (comme dans la capture d'écran)
        tk.Frame(top_bar, bg="#e74c3c", width=20, height=20, bd=0).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Frame(top_bar, bg="#2ecc71", width=20, height=20, bd=0).pack(side=tk.LEFT, padx=5, pady=5)

        tk.Label(
            top_bar,
            text="Analyseur Vidéo YOLO",
            font=("Helvetica", 12),
            bg="#2c3e50",
            fg=COLORS["light_text"]
        ).pack(side=tk.RIGHT, padx=10)

        # Cadre de titre principal
        title_frame = tk.Frame(self.root, bg=COLORS["primary"], pady=20)
        title_frame.pack(fill=tk.X)

        app_title = tk.Label(
            title_frame,
            text="Finder",
            font=("Helvetica", 22, "bold"),
            bg=COLORS["primary"],
            fg=COLORS["light_text"]
        )
        app_title.pack()

        app_subtitle = tk.Label(
            title_frame,
            text="Apprenez les noms d'objets à vos enfants",
            font=("Helvetica", 14),
            bg=COLORS["primary"],
            fg=COLORS["light_text"]
        )
        app_subtitle.pack(pady=(5, 0))

        # Conteneur principal
        main_frame = tk.Frame(self.root, bg=COLORS["background"], padx=30, pady=30)
        main_frame.pack(expand=True, fill=tk.BOTH)

        # Zone d'information
        info_label = tk.Label(
            main_frame,
            text=(
                "Cette application vous permet d'analyser des vidéos ou le flux de votre webcam "
                "en temps réel en utilisant la technologie YOLO pour détecter des objets."
            ),
            font=("Helvetica", 11),
            bg=COLORS["background"],
            fg=COLORS["text"],  # Texte en bleu
            wraplength=500,
            justify=tk.CENTER
        )
        info_label.pack(pady=(0, 30))

        # Cadres pour les boutons
        buttons_frame = tk.Frame(main_frame, bg=COLORS["background"])
        buttons_frame.pack()

        # Bouton pour sélectionner une vidéo
        video_frame = tk.Frame(buttons_frame, bg=COLORS["background"], padx=15, pady=10)
        video_frame.pack(side=tk.LEFT)

        # Utilisation de TextOnlyButton au lieu de StyledButton avec image
        self.btn_video = TextOnlyButton(
            video_frame,
            text="Choisir une vidéo",
            command=self.select_file,
            color=COLORS["primary"],
            width=20,
            height=2
        )
        self.btn_video.pack()

        video_info = tk.Label(
            video_frame,
            text="Analyser un fichier vidéo",
            bg=COLORS["background"],
            fg=COLORS["text"]  # Texte en bleu
        )
        video_info.pack(pady=(5, 0))

        # Bouton pour la webcam
        webcam_frame = tk.Frame(buttons_frame, bg=COLORS["background"], padx=15, pady=10)
        webcam_frame.pack(side=tk.LEFT)

        # Utilisation de TextOnlyButton au lieu de StyledButton avec image
        self.btn_webcam = TextOnlyButton(
            webcam_frame,
            text="Utiliser la webcam",
            command=self.show_ready_dialog,  # <-- Nouvelle méthode à appeler
            color=COLORS["accent"],
            width=20,
            height=2
        )
        self.btn_webcam.pack()

        webcam_info = tk.Label(
            webcam_frame,
            text="Analyser en temps réel",
            bg=COLORS["background"],
            fg=COLORS["text"]  # Texte en bleu
        )
        webcam_info.pack(pady=(5, 0))

        # Pied de page
        footer_frame = tk.Frame(self.root, bg=COLORS["dark_bg"], pady=5)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)

        footer_text = tk.Label(
            footer_frame,
            text="© 2025 Analyseur Vidéo YOLO - Tous droits réservés",
            font=("Helvetica", 8),
            bg=COLORS["dark_bg"],
            fg=COLORS["light_text"]
        )
        footer_text.pack()

    def show_ready_dialog(self):
        # Boîte de dialogue "Êtes-vous prêts?"
        ready_window = Toplevel(self.root)
        ready_window.title("Nouveau jeu")
        ready_window.geometry("400x250")
        ready_window.configure(bg=COLORS["background"])

        # Centre la fenêtre
        self.center_window(ready_window, 400, 250)

        # Titre
        title_label = tk.Label(
            ready_window,
            text="Êtes-vous prêts à jouer?",
            font=("Helvetica", 14, "bold"),
            bg=COLORS["background"],
            fg=COLORS["text"]
        )
        title_label.pack(pady=20)

        # Explication
        explanation = tk.Label(
            ready_window,
            text="Deux joueurs vont s'affronter pour trouver les objets\ndans la maison le plus rapidement possible!",
            font=("Helvetica", 11),
            bg=COLORS["background"],
            fg=COLORS["text"],
            justify=tk.CENTER
        )
        explanation.pack(pady=10)

        # Boutons
        buttons_frame = tk.Frame(ready_window, bg=COLORS["background"])
        buttons_frame.pack(pady=20)

        btn_yes = TextOnlyButton(
            buttons_frame,
            text="Oui, commencer!",
            command=lambda: (ready_window.destroy(), self.select_random_objects()),
            width=15,
            color=COLORS["primary"]
        )
        btn_yes.pack(side=tk.LEFT, padx=10)

        btn_no = TextOnlyButton(
            buttons_frame,
            text="Non, retour",
            command=ready_window.destroy,
            width=15,
            color=COLORS["accent"]
        )
        btn_no.pack(side=tk.LEFT, padx=10)

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
        self.hide_main_window()
        self.open_video_window(file_path)

    def hide_main_window(self):
        self.root.withdraw()

    def show_main_window(self):
        self.root.deiconify()

    def select_random_objects(self):
        # Liste des objets qu'on trouve typiquement dans une maison
        home_objects = [
            "person", "chair", "sofa", "bed", "dining table", "toilet", "tv",
            "laptop", "mouse", "remote", "keyboard", "cell phone", "microwave",
            "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase",
            "scissors", "teddy bear", "hair drier", "toothbrush", "cup", "fork",
            "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange",
            "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "bottle"
        ]

        # Filtrer pour ne garder que les objets disponibles dans YOLO
        detectable_objects = get_detectable_objects()
        available_home_objects = [obj for obj in home_objects if obj in detectable_objects]

        # Sélectionner 5 objets aléatoires (ou moins si pas assez disponibles)
        num_objects = min(5, len(available_home_objects))
        selected_objects = random.sample(available_home_objects, num_objects)

        # Afficher les objets sélectionnés
        self.show_selected_objects(selected_objects)

    def show_selected_objects(self, selected_objects):
        # Affiche les objets sélectionnés avant de commencer
        objects_window = Toplevel(self.root)
        objects_window.title("Objets à trouver")
        objects_window.geometry("450x400")
        objects_window.configure(bg=COLORS["background"])

        # Centre la fenêtre
        self.center_window(objects_window, 450, 400)

        # Titre
        title_label = tk.Label(
            objects_window,
            text="Objets à trouver",
            font=("Helvetica", 16, "bold"),
            bg=COLORS["background"],
            fg=COLORS["text"]
        )
        title_label.pack(pady=15)

        # Instructions
        instructions = tk.Label(
            objects_window,
            text="Trouvez ces objets le plus rapidement possible!",
            font=("Helvetica", 12),
            bg=COLORS["background"],
            fg=COLORS["text"]
        )
        instructions.pack(pady=10)

        # Liste des objets
        objects_frame = tk.Frame(objects_window, bg=COLORS["dark_bg"], padx=20, pady=15)
        objects_frame.pack(pady=15)

        for i, obj in enumerate(selected_objects, 1):
            obj_label = tk.Label(
                objects_frame,
                text=f"{i}. {obj}",
                font=("Helvetica", 14),
                bg=COLORS["dark_bg"],
                fg=COLORS["light_text"],
                anchor="w"
            )
            obj_label.pack(pady=5, fill=tk.X)

        # Configuration des joueurs
        players_frame = tk.Frame(objects_window, bg=COLORS["background"])
        players_frame.pack(pady=15)

        player1_label = tk.Label(
            players_frame,
            text="Joueur 1:",
            font=("Helvetica", 12),
            bg=COLORS["background"],
            fg=COLORS["text"]
        )
        player1_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")

        player1_entry = tk.Entry(players_frame, font=("Helvetica", 12), width=15)
        player1_entry.grid(row=0, column=1, padx=5, pady=5)
        player1_entry.insert(0, "Joueur 1")

        player2_label = tk.Label(
            players_frame,
            text="Joueur 2:",
            font=("Helvetica", 12),
            bg=COLORS["background"],
            fg=COLORS["text"]
        )
        player2_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")

        player2_entry = tk.Entry(players_frame, font=("Helvetica", 12), width=15)
        player2_entry.grid(row=1, column=1, padx=5, pady=5)
        player2_entry.insert(0, "Joueur 2")

        # Bouton pour démarrer
        start_btn = TextOnlyButton(
            objects_window,
            text="Démarrer le jeu",
            command=lambda: (
                self.start_game_with_objects(
                    selected_objects,
                    player1_entry.get(),
                    player2_entry.get()
                ),
                objects_window.destroy()
            ),
            width=20,
            color=COLORS["primary"]
        )
        start_btn.pack(pady=10)

    def start_game_with_objects(self, objects_to_detect, player1_name, player2_name):
        # Cache la fenêtre principale
        self.hide_main_window()

        # Initialise le jeu avec les joueurs
        self.player1_name = player1_name
        self.player2_name = player2_name
        self.player1_score = 0
        self.player2_score = 0
        self.current_player = 1  # Commence avec le joueur 1

        # Ouvre la fenêtre vidéo avec les objets sélectionnés
        self.open_game_window(0, objects_to_detect)  # 0 représente la webcam

    def open_game_window(self, video_source, objects_to_detect):
        # Créer une fenêtre pour le jeu
        game_window = Toplevel()
        game_window.title("Jeu de détection d'objets")
        game_window.geometry("1000x750")
        game_window.configure(bg=COLORS["background"])

        # Conserver une référence à la fenêtre de jeu
        self.game_window = game_window

        # Centre la fenêtre
        self.center_window(game_window, 1000, 750)

        # Titre avec joueur actuel
        title_frame = tk.Frame(game_window, bg=COLORS["dark_bg"], pady=10)
        title_frame.pack(fill=tk.X)

        self.player_label = tk.Label(
            title_frame,
            text=f"Au tour de: {self.player1_name if self.current_player == 1 else self.player2_name}",
            font=("Helvetica", 14, "bold"),
            bg=COLORS["dark_bg"],
            fg=COLORS["light_text"]
        )
        self.player_label.pack()

        # Scores
        scores_frame = tk.Frame(game_window, bg=COLORS["background"], pady=5)
        scores_frame.pack(fill=tk.X)

        self.player1_score_label = tk.Label(
            scores_frame,
            text=f"{self.player1_name}: {self.player1_score} points",
            font=("Helvetica", 12),
            bg=COLORS["background"],
            fg=COLORS["primary"]
        )
        self.player1_score_label.pack(side=tk.LEFT, padx=20)

        self.player2_score_label = tk.Label(
            scores_frame,
            text=f"{self.player2_name}: {self.player2_score} points",
            font=("Helvetica", 12),
            bg=COLORS["background"],
            fg=COLORS["accent"]
        )
        self.player2_score_label.pack(side=tk.RIGHT, padx=20)

        # Timer
        timer_frame = tk.Frame(game_window, bg=COLORS["background"])
        timer_frame.pack()

        self.timer_label = tk.Label(
            timer_frame,
            text="Temps restant: 60s",
            font=("Helvetica", 14),
            bg=COLORS["background"],
            fg=COLORS["text"]
        )
        self.timer_label.pack(pady=10)

        # Liste des objets à trouver
        objects_frame = tk.Frame(game_window, bg=COLORS["background"], pady=10)
        objects_frame.pack()

        objects_title = tk.Label(
            objects_frame,
            text="Objets à trouver:",
            font=("Helvetica", 12, "bold"),
            bg=COLORS["background"],
            fg=COLORS["text"]
        )
        objects_title.pack(pady=(0, 5))

        # Créer des variables pour suivre l'état de chaque objet
        self.object_vars = {}
        objects_list_frame = tk.Frame(objects_frame, bg=COLORS["background"])
        objects_list_frame.pack()

        # Afficher les objets à trouver avec des cases à cocher
        for i, obj in enumerate(objects_to_detect):
            var = tk.BooleanVar(value=False)
            self.object_vars[obj] = var

            obj_check = tk.Checkbutton(
                objects_list_frame,
                text=obj,
                variable=var,
                state="disabled",
                font=("Helvetica", 11),
                bg=COLORS["background"],
                fg=COLORS["text"]
            )
            obj_check.grid(row=i//2, column=i%2, sticky="w", padx=10, pady=2)

        # Zone d'affichage vidéo
        video_frame = tk.Frame(
            game_window,
            bg=COLORS["dark_bg"],
            padx=3,
            pady=3,
            highlightbackground=COLORS["primary"],
            highlightthickness=2
        )
        video_frame.pack(pady=15)

        # Canvas pour afficher la vidéo
        canvas = Canvas(
            video_frame,
            width=800,
            height=400,
            bg=COLORS["dark_bg"],
            highlightthickness=0
        )
        canvas.pack()

        # Conserver une référence au canvas
        self.canvas_reference = canvas

        # Boutons de contrôle
        control_frame = tk.Frame(game_window, bg=COLORS["background"], pady=10)
        control_frame.pack()

        next_turn_btn = TextOnlyButton(
            control_frame,
            text="Passer au joueur suivant",
            command=lambda: self.schedule_next_player_turn(game_window, video_source, objects_to_detect),
            width=20,
            color=COLORS["primary"]
        )
        next_turn_btn.pack(side=tk.LEFT, padx=10)

        end_game_btn = TextOnlyButton(
            control_frame,
            text="Terminer le jeu",
            command=lambda: self.end_game(game_window),
            width=20,
            color=COLORS["accent"]
        )
        end_game_btn.pack(side=tk.LEFT, padx=10)

        # Démarrer le timer
        self.remaining_time = self.max_time
        self.update_timer(game_window)

        # Démarrer la détection vidéo avec les objets spécifiques
        self.start_player_turn(canvas, game_window, video_source, objects_to_detect)

    def create_confetti_effect(self, canvas, duration=3000):
        """Crée une animation de confettis pour célébrer une victoire"""
        self.confetti_active = True
        self.confetti_particles = []

        # Couleurs vives pour les confettis
        confetti_colors = ["#FF5252", "#FFEB3B", "#4CAF50", "#2196F3", "#9C27B0", "#FF9800"]

        # Créer les particules initiales
        width = canvas.winfo_width()
        height = canvas.winfo_height()

        for _ in range(100):  # Nombre de confettis
            x = random.randint(0, width)
            y = random.randint(-50, 0)  # Au-dessus du canvas pour un effet de chute
            self.confetti_particles.append(Confetti(canvas, x, y, confetti_colors))

        # Fonction d'animation
        def animate_confetti():
            if not self.confetti_active:
                # Supprimer tous les confettis restants
                for confetti in self.confetti_particles:
                    canvas.delete(confetti.id)
                self.confetti_particles = []
                return

            # Mettre à jour chaque confetti et supprimer ceux qui sont hors de l'écran
            active_particles = []
            for confetti in self.confetti_particles:
                if confetti.update():
                    active_particles.append(confetti)
                else:
                    canvas.delete(confetti.id)

            self.confetti_particles = active_particles

            # Continuer l'animation si des particules sont encore actives
            if self.confetti_particles:
                canvas.after(33, animate_confetti)  # ~30 FPS
            else:
                self.confetti_active = False

        # Démarrer l'animation
        animate_confetti()

        # Arrêter l'animation après la durée spécifiée
        canvas.after(duration, lambda: setattr(self, 'confetti_active', False))

    def update_timer(self, window):
        """Met à jour le timer et vérifie s'il est écoulé"""
        if not hasattr(self, 'timer_label') or not self.timer_label.winfo_exists():
            return

        if hasattr(self, 'timer_active') and not self.timer_active:
            return

        if self.remaining_time > 0:
            self.remaining_time -= 1
            self.timer_label.config(text=f"Temps restant: {self.remaining_time}s")

            # Programmer la prochaine mise à jour du timer
            if hasattr(self, 'game_window') and self.game_window.winfo_exists():
                self.timer_id = window.after(1000, lambda: self.update_timer(window))
        else:
            # Temps écoulé pour le joueur actuel
            self.timer_active = False
            message = f"Temps écoulé pour {self.player1_name if self.current_player == 1 else self.player2_name}!"

            # Sauvegarder le score actuel avant de passer à la suite
            detected_objects = get_detected_objects_list()
            if self.current_player == 1:
                self.player1_score = len(detected_objects)
                # Passer au joueur 2
                self.show_timeout_message(window, message, lambda: self.schedule_next_player_turn(window, 0, list(self.object_vars.keys())))
            else:
                self.player2_score = len(detected_objects)
                # Afficher les résultats finaux avec notre nouvelle fonction
                self.show_timeout_message(window, message, lambda: self.create_results_window(window))

    def show_timeout_message(self, window, message, callback=None):
        """Affiche un message quand le temps est écoulé"""
        timeout_window = Toplevel(window)
        timeout_window.title("Temps écoulé")
        timeout_window.geometry("300x150")
        timeout_window.configure(bg=COLORS["background"])

        # Centre la fenêtre
        self.center_window(timeout_window, 300, 150)

        # Message
        msg_label = tk.Label(
            timeout_window,
            text=message,
            font=("Helvetica", 12, "bold"),
            bg=COLORS["background"],
            fg=COLORS["text"]
        )
        msg_label.pack(pady=20)

        # Bouton pour continuer
        continue_btn = TextOnlyButton(
            timeout_window,
            text="Continuer",
            command=lambda: (timeout_window.destroy(), callback() if callback else None),
            width=15,
            color=COLORS["primary"]
        )
        continue_btn.pack(pady=10)

    def schedule_stop_detection(self, callback=None):
        """Arrêt programmé de la détection vidéo"""
        print("Arrêt programmé de la détection...")

        # Désactiver le timer
        self.timer_active = False

        # Arrêter l'ancien timer s'il existe
        if hasattr(self, 'timer_id') and self.timer_id:
            self.game_window.after_cancel(self.timer_id)
            self.timer_id = None

        # Arrêter le traitement vidéo actuel
        with self.thread_lock:
            stop_video()

            # Petit délai pour s'assurer que le traitement vidéo est bien arrêté
            self.game_window.after(100, callback if callback else lambda: None)

    def schedule_next_player_turn(self, window, video_source, objects_to_detect):
        """Programme le passage au joueur suivant de façon asynchrone"""
        if self.player_switch_in_progress:
            print("Changement de joueur déjà en cours, ignoré")
            return

        self.player_switch_in_progress = True

        # Afficher un indicateur visuel que le changement est en cours
        status_label = tk.Label(
            window,
            text="Changement de joueur en cours...",
            font=("Helvetica", 12, "bold"),
            bg=COLORS["background"],
            fg="#FF5722"  # Orange pour attirer l'attention
        )
        status_label.pack(pady=5)
        window.update_idletasks()  # Force la mise à jour de l'interface

        # Arrêter la détection et programmer le changement de joueur
        self.schedule_stop_detection(lambda: (
            status_label.destroy(),
            self.handle_player_switch(window, video_source, objects_to_detect)
        ))

    def handle_player_switch(self, window, video_source, objects_to_detect):
        """Gère le changement de joueur après l'arrêt de la détection"""
        print("Changement de joueur effectif...")

        # Mise à jour du score en fonction des objets détectés
        detected_objects = get_detected_objects_list()
        points = len(detected_objects)
        total_objects = len(self.object_vars)
        time_used = self.max_time - self.remaining_time

        # Vérifie si tous les objets ont été trouvés
        all_found = len(detected_objects) == total_objects

        # Attribue les points et l'état de complétion au joueur actuel
        if self.current_player == 1:
            self.player1_score = points
            self.player1_completed = all_found
            if all_found:
                self.player1_time = time_used

            if hasattr(self, 'player1_score_label') and self.player1_score_label.winfo_exists():
                self.player1_score_label.config(text=f"{self.player1_name}: {self.player1_score}/{total_objects}")

            # Passage au joueur 2
            self.current_player = 2

            # Réinitialiser toutes les cases à cocher pour le joueur 2
            for obj, var in self.object_vars.items():
                var.set(False)  # Décocher tous les objets

            print(f"Passage au joueur 2")

            if hasattr(self, 'player_label') and self.player_label.winfo_exists():
                self.player_label.config(text=f"Au tour de: {self.player2_name}")

            # Réinitialiser le timer
            self.remaining_time = self.max_time
            if hasattr(self, 'timer_label') and self.timer_label.winfo_exists():
                self.timer_label.config(text=f"Temps restant: {self.remaining_time}s")

            # Réinitialiser les objets détectés
            reset_detected_objects()

            # Redémarrer le timer pour le joueur 2
            self.start_player_turn(self.canvas_reference, window, video_source, objects_to_detect)

        else:  # Joueur 2 a terminé
            self.player2_score = points
            self.player2_completed = all_found
            if all_found:
                self.player2_time = time_used

            if hasattr(self, 'player2_score_label') and self.player2_score_label.winfo_exists():
                self.player2_score_label.config(text=f"{self.player2_name}: {self.player2_score}/{total_objects}")

            # Les deux joueurs ont joué, afficher les résultats
            self.show_game_results(window)

        # Indiquer que le changement de joueur est terminé
        self.player_switch_in_progress = False


    def start_player_turn(self, canvas, window, video_source, objects_to_detect):
        """Démarre le tour d'un joueur"""
        if not canvas.winfo_exists():
            print("⚠ Canvas n'existe plus, abandon du tour")
            return

        # Arrêter l'ancien timer s'il existe
        if hasattr(self, 'timer_id') and self.timer_id:
            window.after_cancel(self.timer_id)
            self.timer_id = None

        # Activer le timer
        self.timer_active = True

        reset_detected_objects()

        # Réinitialiser le timer explicitement
        if hasattr(self, 'timer_label') and self.timer_label.winfo_exists():
            self.timer_label.config(text=f"Temps restant: {self.remaining_time}s")

        # Référence au nombre total d'objets à trouver
        total_objects = len(objects_to_detect)

        # Variable pour suivre le nombre d'objets trouvés dans ce tour
        objects_found = [0]

        # Démarrer le timer
        self.update_timer(window)

        def mark_detected(obj_name):
            """Marque un objet comme détecté et met à jour le score"""
            var = self.object_vars.get(obj_name)
            if var and not var.get():
                var.set(True)
                objects_found[0] += 1

                # Mettre à jour le score affiché
                if self.current_player == 1:
                    if hasattr(self, 'player1_score_label') and self.player1_score_label.winfo_exists():
                        self.player1_score_label.config(text=f"{self.player1_name}: {objects_found[0]}/{total_objects}")
                else:
                    if hasattr(self, 'player2_score_label') and self.player2_score_label.winfo_exists():
                        self.player2_score_label.config(text=f"{self.player2_name}: {objects_found[0]}/{total_objects}")

                # Vérifier si tous les objets ont été trouvés
                if objects_found[0] >= total_objects:
                    # Calculer le temps utilisé
                    time_used = self.max_time - self.remaining_time

                    # Enregistrer l'achèvement et le temps pour le joueur actuel
                    if self.current_player == 1:
                        self.player1_completed = True
                        self.player1_time = time_used
                        self.player1_score = total_objects
                        # Afficher un message et passer au joueur 2
                        success_message = f"Bravo {self.player1_name} ! Tous les objets trouvés en {time_used} secondes !"
                        self.show_success_message(window, success_message, lambda: self.schedule_next_player_turn(window, video_source, objects_to_detect))
                    else:
                        self.player2_completed = True
                        self.player2_time = time_used
                        self.player2_score = total_objects
                        # Afficher un message et montrer les résultats
                        success_message = f"Bravo {self.player2_name} ! Tous les objets trouvés en {time_used} secondes !"
                        self.show_success_message(window, success_message, lambda: self.show_game_results(window))

        # Démarrer la détection vidéo
        try:
            process_video(
                video_source,
                canvas,
                window,
                detection_label=None,
                fps_label=None,
                progress=None,
                objects_to_detect=objects_to_detect,
                on_object_detected=mark_detected
            )
        except Exception as e:
            print(f"Erreur lors du démarrage de la détection vidéo: {e}")

    def create_results_window(self, parent_window, title="Résultats du jeu"):
        """Crée une fenêtre de résultats cohérente avec les scores corrects"""
        results_window = Toplevel(parent_window)
        results_window.title(title)
        results_window.geometry("400x350")
        results_window.configure(bg=COLORS["background"])

        # Centre la fenêtre
        self.center_window(results_window, 400, 350)

        # Titre
        title_label = tk.Label(
            results_window,
            text="Fin du jeu!",
            font=("Helvetica", 16, "bold"),
            bg=COLORS["background"],
            fg=COLORS["text"]
        )
        title_label.pack(pady=20)

        # Total d'objets
        total_objects = len(self.object_vars)

        # Vérifier et récupérer les scores depuis les labels si nécessaire
        if hasattr(self, 'player1_score_label') and self.player1_score_label.winfo_exists():
            player1_label_text = self.player1_score_label.cget("text")
            if ":" in player1_label_text and "/" in player1_label_text:
                try:
                    score_part = player1_label_text.split(":")[1].strip().split("/")[0]
                    self.player1_score = int(score_part)
                except:
                    pass

        if hasattr(self, 'player2_score_label') and self.player2_score_label.winfo_exists():
            player2_label_text = self.player2_score_label.cget("text")
            if ":" in player2_label_text and "/" in player2_label_text:
                try:
                    score_part = player2_label_text.split(":")[1].strip().split("/")[0]
                    self.player2_score = int(score_part)
                except:
                    pass

        # Si nous sommes encore au tour du joueur 2, récupérer son score actuel
        if self.current_player == 2:
            detected_objects = get_detected_objects_list()
            if detected_objects:
                self.player2_score = len(detected_objects)

        # Afficher les scores
        player1_result = tk.Label(
            results_window,
            text=f"{self.player1_name}: {self.player1_score}/{total_objects} objets",
            font=("Helvetica", 14),
            bg=COLORS["background"],
            fg=COLORS["primary"]
        )
        player1_result.pack(pady=5)

        player2_result = tk.Label(
            results_window,
            text=f"{self.player2_name}: {self.player2_score}/{total_objects} objets",
            font=("Helvetica", 14),
            bg=COLORS["background"],
            fg=COLORS["accent"]
        )
        player2_result.pack(pady=5)

        # Déterminer le gagnant
        winner_text = "Match nul!"

        # Comparer les scores
        if self.player1_score > self.player2_score:
            winner_text = f"{self.player1_name} gagne avec {self.player1_score} objets trouvés !"
        elif self.player2_score > self.player1_score:
            winner_text = f"{self.player2_name} gagne avec {self.player2_score} objets trouvés !"
        else:
            winner_text = "Match nul avec le même nombre d'objets !"

        # Afficher le gagnant
        winner_label = tk.Label(
            results_window,
            text=winner_text,
            font=("Helvetica", 16, "bold"),
            bg=COLORS["background"],
            fg=COLORS["text"]
        )
        winner_label.pack(pady=20)

        # Bouton pour retourner au menu
        return_btn = TextOnlyButton(
            results_window,
            text="Retour au menu",
            command=lambda: (results_window.destroy(), parent_window.destroy(), self.show_main_window()),
            width=15,
            color=COLORS["primary"]
        )
        return_btn.pack(pady=10)

        return results_window

    def end_game(self, window):
        """Termine le jeu et affiche les résultats"""
        # CORRECTION: Sauvegarde des objets détectés pour le joueur actuel avant d'arrêter la détection
        detected_objects = get_detected_objects_list()
        if self.current_player == 1:
            self.player1_score = len(detected_objects)
            print(f"Score final du joueur 1 sauvegardé: {self.player1_score}")
        else:  # Joueur 2
            self.player2_score = len(detected_objects)
            print(f"Score final du joueur 2 sauvegardé: {self.player2_score}")

        # Arrêter la détection vidéo de manière sécurisée
        self.schedule_stop_detection(lambda: self.show_game_results(window))

    def show_success_message(self, window, message, callback=None):
        """Affiche un message de réussite et passe ensuite au joueur suivant"""
        try:
            # Arrêter le timer pendant l'affichage du message
            self.timer_active = False

            # Si c'est le joueur 2 qui a fini, sauvegarder son score
            if self.current_player == 2:
                detected_objects = get_detected_objects_list()
                self.player2_score = len(detected_objects)

            success_window = Toplevel(window)
            success_window.title("Réussite !")
            success_window.geometry("400x200")
            success_window.configure(bg=COLORS["background"])

            # Centre la fenêtre
            self.center_window(success_window, 400, 200)

            # Message
            msg_label = tk.Label(
                success_window,
                text=message,
                font=("Helvetica", 14, "bold"),
                bg=COLORS["background"],
                fg=COLORS["primary"]
            )
            msg_label.pack(pady=20)

            # Bouton pour continuer
            continue_btn = TextOnlyButton(
                success_window,
                text="Continuer",
                command=lambda: (success_window.destroy(), callback() if callback else None),
                width=15,
                color=COLORS["primary"]
            )
            continue_btn.pack(pady=10)

            # Effet de confettis
            canvas = Canvas(success_window, width=400, height=200, bg=COLORS["background"], highlightthickness=0)
            canvas.place(x=0, y=0)
            self.create_confetti_effect(canvas)

        except Exception as e:
            print(f"Erreur lors de l'affichage du message de réussite: {e}")
            # En cas d'erreur, exécuter quand même le callback
            if callback:
                callback()

    def show_game_results(self, window):
        """Affiche les résultats finaux du jeu"""
        if not hasattr(self, 'game_window') or not self.game_window.winfo_exists():
            return

        # Utiliser la nouvelle fonction pour créer l'écran de résultats
        self.create_results_window(window)

    def open_video_window(self, video_source, objects_to_detect=None):
        video_window = Toplevel()
        video_window.title("Analyse vidéo YOLO")
        video_window.geometry("1000x700")
        video_window.configure(bg=COLORS["background"])

        # Centre la fenêtre
        self.center_window(video_window, 1000, 700)

        # Titre
        title_frame = tk.Frame(video_window, bg=COLORS["dark_bg"], pady=10)
        title_frame.pack(fill=tk.X)

        window_title = tk.Label(
            title_frame,
            text="Détection d'objets en cours",
            font=("Helvetica", 14, "bold"),
            bg=COLORS["dark_bg"],
            fg=COLORS["light_text"]
        )
        window_title.pack()

        # Zone d'information
        if isinstance(video_source, int):
            source_text = "Source: Webcam"
        else:
            source_text = f"Source: {os.path.basename(video_source)}"

        source_label = tk.Label(
            video_window,
            text=source_text,
            font=("Helvetica", 10),
            bg=COLORS["background"],
            fg=COLORS["text"]  # Texte en bleu
        )
        source_label.pack(pady=(5, 0))

        # Afficher les objets à détecter si fournis
        if objects_to_detect:
            objects_text = ", ".join(objects_to_detect[:5])
            if len(objects_to_detect) > 5:
                objects_text += f" et {len(objects_to_detect) - 5} autres"

            objects_label = tk.Label(
                video_window,
                text=f"Objets à détecter: {objects_text}",
                font=("Helvetica", 10),
                bg=COLORS["background"],
                fg=COLORS["text"]  # Texte en bleu
            )
            objects_label.pack(pady=(5, 0))

        # Frame pour le canvas vidéo avec bordure
        video_frame = tk.Frame(
            video_window,
            bg=COLORS["dark_bg"],
            padx=3,
            pady=3,
            highlightbackground=COLORS["primary"],
            highlightthickness=2
        )
        video_frame.pack(pady=15)

        # Canvas pour afficher la vidéo
        canvas = Canvas(
            video_frame,
            width=800,
            height=500,
            bg=COLORS["dark_bg"],
            highlightthickness=0
        )
        canvas.pack()

        # Barre de progression
        progress_frame = tk.Frame(video_window, bg=COLORS["background"])
        progress_frame.pack(fill=tk.X, padx=50, pady=(5, 15))

        progress = ttk.Progressbar(
            progress_frame,
            orient="horizontal",
            length=900,
            mode="indeterminate"
        )
        progress.pack(fill=tk.X)
        progress.start(10)

        # Message de victoire (initialement caché)
        win_frame = tk.Frame(video_window, bg=COLORS["background"])
        win_frame.pack(fill=tk.X, pady=5)

        win_label = tk.Label(
            win_frame,
            text="🎉 VICTOIRE ! Tous les objets détectés ! 🎉",
            font=("Helvetica", 14, "bold"),
            bg=COLORS["background"],
            fg=COLORS["text"],  # Texte en bleu
        )
        win_label.pack()
        win_label.pack_forget()  # Caché initialement

        # Cadre pour les contrôles
        control_frame = tk.Frame(video_window, bg=COLORS["background"], pady=10)
        control_frame.pack()

        # État de pause
        is_paused = {'value': False}

        def toggle_video():
            is_paused['value'] = toggle_pause()
            # Utiliser du texte au lieu des icônes
            btn_toggle.config(text="▶ Play" if is_paused['value'] else "⏸ Pause")

        # Boutons de contrôle avec texte au lieu d'icônes
        btn_toggle = TextOnlyButton(
            control_frame,
            text="⏸ Pause",
            command=toggle_video,
            width=15,
            height=1,
            color=COLORS["primary"]
        )
        btn_toggle.pack(side=tk.LEFT, padx=10)

        btn_return = TextOnlyButton(
            control_frame,
            text="↩ Retour au menu",
            command=lambda: (stop_video(), self.show_main_window()),
            width=15,
            height=1,
            color=COLORS["accent"]
        )
        btn_return.pack(side=tk.LEFT, padx=10)

        # Étiquettes pour les détections et score
        stats_frame = tk.Frame(video_window, bg=COLORS["background"], pady=10)
        stats_frame.pack()

        # Si des objets spécifiques sont à détecter, afficher le format X/Y
        if objects_to_detect:
            detection_label = tk.Label(
                stats_frame,
                text=f"Objets détectés: 0/{len(objects_to_detect)}",
                font=("Helvetica", 11),
                bg=COLORS["background"],
                fg=COLORS["text"]  # Texte en bleu
            )
        else:
            detection_label = tk.Label(
                stats_frame,
                text="Objets détectés: 0",
                font=("Helvetica", 11),
                bg=COLORS["background"],
                fg=COLORS["text"]  # Texte en bleu
            )
        detection_label.pack(side=tk.LEFT, padx=20)

        fps_label = tk.Label(
            stats_frame,
            text="FPS: 0",
            font=("Helvetica", 11),
            bg=COLORS["background"],
            fg=COLORS["text"]  # Texte en bleu
        )
        fps_label.pack(side=tk.LEFT, padx=20)

        # Fonction pour vérifier si tous les objets ont été détectés
        last_detected_count = [0]
        win_shown = [False]

        def check_victory(detected_text):
            # Extraire le nombre d'objets détectés
            try:
                if objects_to_detect:
                    # Format "Objets détectés: X/Y"
                    parts = detected_text.split(': ')[1]
                    current = int(parts.split('/')[0])
                    total = int(parts.split('/')[1])

                    # Si tous les objets sont détectés et que le message de victoire n'a pas encore été affiché
                    if current == total and current > 0 and not win_shown[0]:
                        win_shown[0] = True
                        win_label.pack()  # Afficher le message de victoire
                        self.create_confetti_effect(canvas)  # Lancer l'effet de confettis

                    last_detected_count[0] = current
            except Exception as e:
                print(f"Erreur lors de l'analyse des détections: {e}")

        # Fonction pour mettre à jour l'étiquette de détection et vérifier la victoire
        original_update_label = detection_label.config

        def update_detection_label(**kwargs):
            if 'text' in kwargs:
                check_victory(kwargs['text'])
            original_update_label(**kwargs)

        detection_label.config = update_detection_label

        # Lancer le traitement vidéo avec les paramètres appropriés
        try:
            if objects_to_detect:
                process_video(video_source, canvas, video_window, detection_label, fps_label, progress, objects_to_detect)
            else:
                process_video(video_source, canvas, video_window, detection_label, fps_label, progress)
        except Exception as e:
            print(f"Erreur lors du démarrage du traitement vidéo: {e}")

    def run(self):
        self.root.mainloop()

# Point d'entrée de l'application
if __name__ == "__main__":
    app = VideoApp()
    app.run()
