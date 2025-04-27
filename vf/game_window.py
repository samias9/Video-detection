import tkinter as tk
from tkinter import Toplevel, Canvas

from ui_components import GameButton, COLORS
from yolo_processor import process_video, stop_video, get_detected_objects_list, reset_detected_objects
from dialogs import show_timeout_message, show_success_message, create_results_window

class GameWindow:
    def __init__(self, app, video_source, objects_to_detect):
        self.app = app
        self.video_source = video_source
        self.objects_to_detect = objects_to_detect
        self.player_switch_in_progress = False
        self.object_vars = {}

        self.create_window()
        self.app.object_vars = self.object_vars

        self.app.remaining_time = self.app.max_time
        self.update_timer()
        self.start_player_turn()

    def create_window(self):
        # Fenêtre principale du jeu
        self.window = Toplevel()
        self.window.title("Jeu de détection d'objets")
        self.window.geometry("1000x750")
        self.window.configure(bg=COLORS["background"])
        self.app.game_window = self.window
        self.app.center_window(self.window, 1000, 750)

        title_frame = tk.Frame(self.window, bg=COLORS["dark_bg"], pady=10)
        title_frame.pack(fill=tk.X)

        self.player_label = tk.Label(
            title_frame,
            text=f"Au tour de: {self.app.player1_name if self.app.current_player == 1 else self.app.player2_name}",
            font=("Helvetica", 14, "bold"),
            bg=COLORS["dark_bg"],
            fg=COLORS["light_text"]
        )
        self.player_label.pack()

        # Affichage des scores
        scores_frame = tk.Frame(self.window, bg=COLORS["background"], pady=5)
        scores_frame.pack(fill=tk.X)

        self.player1_score_label = tk.Label(
            scores_frame,
            text=f"{self.app.player1_name}: {self.app.player1_score} points",
            font=("Helvetica", 12),
            bg=COLORS["background"],
            fg=COLORS["primary"]
        )
        self.player1_score_label.pack(side=tk.LEFT, padx=20)

        self.player2_score_label = tk.Label(
            scores_frame,
            text=f"{self.app.player2_name}: {self.app.player2_score} points",
            font=("Helvetica", 12),
            bg=COLORS["background"],
            fg=COLORS["accent"]
        )
        self.player2_score_label.pack(side=tk.RIGHT, padx=20)

        # Compteur de temps
        timer_frame = tk.Frame(self.window, bg=COLORS["background"])
        timer_frame.pack()

        self.timer_label = tk.Label(
            timer_frame,
            text=f"Temps restant: {self.app.remaining_time}s",
            font=("Helvetica", 14),
            bg=COLORS["background"],
            fg=COLORS["text"]
        )
        self.timer_label.pack(pady=10)

        # Liste des objets à trouver
        objects_frame = tk.Frame(self.window, bg=COLORS["background"], pady=10)
        objects_frame.pack()

        objects_title = tk.Label(
            objects_frame,
            text="Objets à trouver:",
            font=("Helvetica", 12, "bold"),
            bg=COLORS["background"],
            fg=COLORS["text"]
        )
        objects_title.pack(pady=(0, 5))

        # Liste des objets avec checkboxes
        objects_list_frame = tk.Frame(objects_frame, bg=COLORS["background"])
        objects_list_frame.pack()

        for i, obj in enumerate(self.objects_to_detect):
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
            height=400,
            bg=COLORS["dark_bg"],
            highlightthickness=0
        )
        self.canvas.pack()
        self.app.canvas_reference = self.canvas

        # Boutons de contrôle
        control_frame = tk.Frame(self.window, bg=COLORS["background"], pady=10)
        control_frame.pack()

        next_turn_btn = GameButton(
            control_frame,
            text="Passer au joueur suivant",
            command=self.schedule_next_player_turn,
            width=20,
            color=COLORS["primary"]
        )
        next_turn_btn.pack(side=tk.LEFT, padx=10)

        end_game_btn = GameButton(
            control_frame,
            text="Terminer le jeu",
            command=self.end_game,
            width=20,
            color=COLORS["accent"]
        )
        end_game_btn.pack(side=tk.LEFT, padx=10)

    def update_timer(self):
        if not hasattr(self, 'timer_label') or not self.timer_label.winfo_exists():
            return

        if not getattr(self.app, 'timer_active', True):
            return

        if self.app.remaining_time > 0:
            self.app.remaining_time -= 1
            self.timer_label.config(text=f"Temps restant: {self.app.remaining_time}s")

            if hasattr(self, 'window') and self.window.winfo_exists():
                self.app.timer_id = self.window.after(1000, self.update_timer)
        else:
            # Temps écoulé
            self.app.timer_active = False
            message = f"Temps écoulé pour {self.app.player1_name if self.app.current_player == 1 else self.app.player2_name}!"

            # Sauvegarde du score
            detected_objects = get_detected_objects_list()

            if self.app.current_player == 1:
                self.app.player1_score = len(detected_objects)
                show_timeout_message(self.window, self.app, message, self.schedule_next_player_turn)
            else:
                self.app.player2_score = len(detected_objects)
                show_timeout_message(self.window, self.app, message, lambda: self.show_game_results())

    def schedule_stop_detection(self, callback=None):
        print("Arrêt programmé de la détection...")
        self.app.timer_active = False

        if hasattr(self.app, 'timer_id') and self.app.timer_id:
            self.window.after_cancel(self.app.timer_id)
            self.app.timer_id = None

        with self.app.thread_lock:
            stop_video()
            self.window.after(100, callback if callback else lambda: None)

    def schedule_next_player_turn(self):
        if self.player_switch_in_progress:
            print("Changement de joueur déjà en cours, ignoré")
            return

        self.player_switch_in_progress = True

        # Indicateur visuel
        status_label = tk.Label(
            self.window,
            text="Changement de joueur en cours...",
            font=("Helvetica", 12, "bold"),
            bg=COLORS["background"],
            fg="#FF5722"
        )
        status_label.pack(pady=5)
        self.window.update_idletasks()

        self.schedule_stop_detection(lambda: (
            status_label.destroy(),
            self.handle_player_switch()
        ))

    def handle_player_switch(self):
        print("Changement de joueur effectif...")

        # Calcul des scores et états
        detected_objects = get_detected_objects_list()
        points = len(detected_objects)
        total_objects = len(self.object_vars)
        time_used = self.app.max_time - self.app.remaining_time
        all_found = len(detected_objects) == total_objects

        if self.app.current_player == 1:
            # Mise à jour du joueur 1
            self.app.player1_score = points
            self.app.player1_completed = all_found
            if all_found:
                self.app.player1_time = time_used

            if hasattr(self, 'player1_score_label') and self.player1_score_label.winfo_exists():
                self.player1_score_label.config(text=f"{self.app.player1_name}: {self.app.player1_score}/{total_objects}")

            # Passage au joueur 2
            self.app.current_player = 2

            # Réinitialisation
            for obj, var in self.object_vars.items():
                var.set(False)

            if hasattr(self, 'player_label') and self.player_label.winfo_exists():
                self.player_label.config(text=f"Au tour de: {self.app.player2_name}")

            self.app.remaining_time = self.app.max_time
            if hasattr(self, 'timer_label') and self.timer_label.winfo_exists():
                self.timer_label.config(text=f"Temps restant: {self.app.remaining_time}s")

            reset_detected_objects()
            self.start_player_turn()

        else:
            # Mise à jour du joueur 2
            self.app.player2_score = points
            self.app.player2_completed = all_found
            if all_found:
                self.app.player2_time = time_used

            if hasattr(self, 'player2_score_label') and self.player2_score_label.winfo_exists():
                self.player2_score_label.config(text=f"{self.app.player2_name}: {self.app.player2_score}/{total_objects}")

            # Fin du jeu
            self.show_game_results()

        self.player_switch_in_progress = False

    def start_player_turn(self):
        if not self.canvas.winfo_exists():
            print("⚠ Canvas n'existe plus, abandon du tour")
            return

        # Préparation du tour
        if hasattr(self.app, 'timer_id') and self.app.timer_id:
            self.window.after_cancel(self.app.timer_id)
            self.app.timer_id = None

        self.app.timer_active = True
        reset_detected_objects()

        if hasattr(self, 'timer_label') and self.timer_label.winfo_exists():
            self.timer_label.config(text=f"Temps restant: {self.app.remaining_time}s")

        total_objects = len(self.objects_to_detect)
        objects_found = [0]
        self.update_timer()

        def mark_detected(obj_name):
            var = self.object_vars.get(obj_name)
            if var and not var.get():
                var.set(True)
                objects_found[0] += 1

                # Mise à jour visuelle
                if self.app.current_player == 1:
                    if hasattr(self, 'player1_score_label') and self.player1_score_label.winfo_exists():
                        self.player1_score_label.config(text=f"{self.app.player1_name}: {objects_found[0]}/{total_objects}")
                else:
                    if hasattr(self, 'player2_score_label') and self.player2_score_label.winfo_exists():
                        self.player2_score_label.config(text=f"{self.app.player2_name}: {objects_found[0]}/{total_objects}")

                # Vérification de victoire
                if objects_found[0] >= total_objects:
                    time_used = self.app.max_time - self.app.remaining_time

                    if self.app.current_player == 1:
                        self.app.player1_completed = True
                        self.app.player1_time = time_used
                        self.app.player1_score = total_objects
                        success_message = f"Bravo {self.app.player1_name} ! Tous les objets trouvés en {time_used} secondes !"
                        show_success_message(self.window, self.app, success_message, self.schedule_next_player_turn)
                    else:
                        self.app.player2_completed = True
                        self.app.player2_time = time_used
                        self.app.player2_score = total_objects
                        success_message = f"Bravo {self.app.player2_name} ! Tous les objets trouvés en {time_used} secondes !"
                        show_success_message(self.window, self.app, success_message, self.show_game_results)

        # Démarrer l'analyse vidéo
        try:
            process_video(
                self.video_source,
                self.canvas,
                self.window,
                detection_label=None,
                fps_label=None,
                progress=None,
                objects_to_detect=self.objects_to_detect,
                on_object_detected=mark_detected
            )
        except Exception as e:
            print(f"Erreur lors du démarrage de la détection vidéo: {e}")

    def end_game(self):
        # Sauvegarde des scores
        detected_objects = get_detected_objects_list()
        if self.app.current_player == 1:
            self.app.player1_score = len(detected_objects)
            print(f"Score final du joueur 1 sauvegardé: {self.app.player1_score}")
        else:
            self.app.player2_score = len(detected_objects)
            print(f"Score final du joueur 2 sauvegardé: {self.app.player2_score}")

        self.schedule_stop_detection(self.show_game_results)

    def show_game_results(self):
        if not hasattr(self, 'window') or not self.window.winfo_exists():
            return

        create_results_window(self.window, self.app)
