import tkinter as tk
from tkinter import Toplevel, Canvas
import random

from ui_components import GameButton, COLORS

def show_selected_objects(app, selected_objects):
    # Création de la fenêtre de sélection des objets
    objects_window = Toplevel(app.root)
    objects_window.title("Objets à trouver")
    objects_window.geometry("600x500")
    objects_window.configure(bg=COLORS["background"])

    app.center_window(objects_window, 800, 700)

    #  un canvas pour le fond
    canvas = Canvas(
        objects_window,
        width=600,
        height=500,
        highlightthickness=0,
        bg=COLORS["background"]
    )
    canvas.pack(fill=tk.BOTH, expand=True)

    # Ajouter des éléments décoratifs (nuages, petits arbres)
    for i in range(7):
        # Nuages
        cloud_x = 70 + i * 110
        cloud_y = 40
        cloud_size = 30

        cloud_part1 = canvas.create_oval(
            cloud_x - cloud_size/2, cloud_y - cloud_size/4,
            cloud_x + cloud_size/2, cloud_y + cloud_size/4,
            fill="white", outline=""
        )

        cloud_part2 = canvas.create_oval(
            cloud_x - cloud_size/4, cloud_y - cloud_size/2,
            cloud_x + cloud_size/4, cloud_y + cloud_size/2,
            fill="white", outline=""
        )

    # Ligne d'arbres en bas
    ground_y = 480
    for i in range(10):
        tree_x = 40 + i * 80
        tree_y = ground_y

        # Taille aléatoire
        tree_size = random.randint(30, 50)

        # Tronc
        canvas.create_rectangle(
            tree_x - tree_size//10, tree_y,
            tree_x + tree_size//10, tree_y - tree_size * 0.3,
            fill="#8B4513", outline=""
        )

        # Type d'arbre aléatoire
        if random.choice([True, False]):
            # Sapin
            for j in range(3):
                factor = 1-j*0.2
                canvas.create_polygon(
                    int(tree_x - tree_size/2 * factor), int(tree_y - tree_size * 0.3 * j),
                    tree_x, int(tree_y - tree_size * 0.3 * (j+1)),
                    int(tree_x + tree_size/2 * factor), int(tree_y - tree_size * 0.3 * j),
                    fill=random.choice([COLORS["forest_green"], COLORS["primary"]]),
                    outline=""
                )
        else:
            # Arbre rond
            canvas.create_oval(
                int(tree_x - tree_size/2), int(tree_y - tree_size * 1.1),
                int(tree_x + tree_size/2), int(tree_y - tree_size * 0.3),
                fill=random.choice([COLORS["forest_green"], COLORS["primary"]]),
                outline=""
            )

    from forest_badge import create_forest_badge
    badge = create_forest_badge(canvas, 300, 50, 140, 140, "Objets")

    # Instructions en dessous du badge
    instructions = tk.Label(
        objects_window,
        text="Trouvez ces objets le plus rapidement possible!",
        font=("Arial Rounded MT Bold", 14),
        bg=COLORS["background"],
        fg=COLORS["dark_bg"]
    )
    instructions.place(relx=0.5, rely=0.3, anchor=tk.CENTER)

    # Cadre pour la liste des objets
    objects_frame = tk.Frame(objects_window, bg=COLORS["dark_bg"], bd=4, relief=tk.RAISED)
    objects_frame.place(relx=0.5, rely=0.48, anchor=tk.CENTER, width=400, height=180)

    # Liste des objets
    for i, obj in enumerate(selected_objects):
        row = i // 2
        col = i % 2

        # Créer un mini-cadre pour chaque objet
        obj_frame = tk.Frame(objects_frame, bg=COLORS["dark_bg"], padx=10, pady=5)
        obj_frame.grid(row=row, column=col, padx=10, pady=8)

        # Cercle coloré devant le texte
        canvas_indicator = Canvas(
            obj_frame,
            width=30,
            height=30,
            bg=COLORS["dark_bg"],
            highlightthickness=0
        )
        canvas_indicator.pack(side=tk.LEFT, padx=(0, 5))

        indicator = canvas_indicator.create_oval(
            5, 5, 25, 25,
            fill=COLORS["accent"],
            outline="white",
            width=2
        )

        # Numéro
        canvas_indicator.create_text(
            15, 15,
            text=str(i+1),
            fill="white",
            font=("Arial Rounded MT Bold", 12, "bold")
        )

        # Texte de l'objet
        obj_label = tk.Label(
            obj_frame,
            text=obj,
            font=("Arial Rounded MT Bold", 12, "bold"),
            bg=COLORS["dark_bg"],
            fg=COLORS["light_text"],
            anchor="w"
        )
        obj_label.pack(side=tk.LEFT)

    # Configuration des joueurs
    players_frame = tk.Frame(objects_window, bg=COLORS["background"])
    players_frame.place(relx=0.5, rely=0.75, anchor=tk.CENTER)

    player1_label = tk.Label(
        players_frame,
        text="Joueur 1:",
        font=("Arial Rounded MT Bold", 14),
        bg=COLORS["background"],
        fg=COLORS["dark_bg"]
    )
    player1_label.grid(row=0, column=0, padx=10, pady=8, sticky="e")

    player1_entry = tk.Entry(
        players_frame,
        font=("Arial Rounded MT Bold", 14),
        width=15,
        bd=3,
        relief=tk.SUNKEN
    )
    player1_entry.grid(row=0, column=1, padx=10, pady=8)
    player1_entry.insert(0, "Joueur 1")

    player2_label = tk.Label(
        players_frame,
        text="Joueur 2:",
        font=("Arial Rounded MT Bold", 14),
        bg=COLORS["background"],
        fg=COLORS["dark_bg"]
    )
    player2_label.grid(row=1, column=0, padx=10, pady=8, sticky="e")

    player2_entry = tk.Entry(
        players_frame,
        font=("Arial Rounded MT Bold", 14),
        width=15,
        bd=3,
        relief=tk.SUNKEN
    )
    player2_entry.grid(row=1, column=1, padx=10, pady=8)
    player2_entry.insert(0, "Joueur 2")

    # Bouton de démarrage
    start_btn = GameButton(
        objects_window,
        text="Démarrer le jeu",
        command=lambda: (
            app.game_manager.start_game_with_objects(
                selected_objects,
                player1_entry.get(),
                player2_entry.get()
            ),
            objects_window.destroy()
        ),
        width=15,
        color="#FF9800"  # Orange
    )
    start_btn.place(relx=0.5, rely=0.92, anchor=tk.CENTER)
