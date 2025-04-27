import tkinter as tk
from tkinter import Toplevel, Canvas
from tkinter import Canvas
from confetti_effect import create_confetti_effect

from ui_components import GameButton, COLORS

def show_ready_dialog(app):
    ready_window = Toplevel(app.root)
    ready_window.title("Nouveau jeu")
    ready_window.geometry("400x300")
    ready_window.configure(bg=COLORS["background"])

    app.center_window(ready_window, 400, 300)

    # Créer un canvas pour le fond
    canvas = Canvas(
        ready_window,
        width=400,
        height=300,
        highlightthickness=0,
        bg=COLORS["background"]
    )
    canvas.pack(fill=tk.BOTH, expand=True)

    # quelques éléments graphiques (petits arbres, nuages)
    for i in range(5):
        # Nuages
        cloud_x = 50 + i * 80
        cloud_y = 30
        cloud_size = 30

        canvas.create_oval(
            cloud_x - cloud_size/2, cloud_y - cloud_size/4,
            cloud_x + cloud_size/2, cloud_y + cloud_size/4,
            fill="white", outline=""
        )

        canvas.create_oval(
            cloud_x - cloud_size/4, cloud_y - cloud_size/2,
            cloud_x + cloud_size/4, cloud_y + cloud_size/2,
            fill="white", outline=""
        )

        # Petits arbres
        if i % 2 == 0:
            tree_x = 30 + i * 90
            tree_y = 250

            # Tronc
            canvas.create_rectangle(
                tree_x - 5, tree_y,
                tree_x + 5, tree_y - 20,
                fill="#8B4513", outline=""
            )

            # Feuillage
            canvas.create_polygon(
                tree_x - 15, tree_y - 15,
                tree_x, tree_y - 40,
                tree_x + 15, tree_y - 15,
                fill=COLORS["forest_green"], outline=""
            )

    # Titre
    title_label = tk.Label(
        ready_window,
        text="Êtes-vous prêts à jouer?",
        font=("Arial Rounded MT Bold", 16, "bold"),
        bg=COLORS["background"],
        fg=COLORS["dark_bg"]
    )
    title_label.place(relx=0.5, rely=0.2, anchor=tk.CENTER)

    # Explication
    explanation = tk.Label(
        ready_window,
        text="Deux joueurs vont s'affronter pour trouver les objets\ndans la maison le plus rapidement possible!",
        font=("Arial Rounded MT Bold", 12),
        bg=COLORS["background"],
        fg=COLORS["dark_bg"],
        justify=tk.CENTER
    )
    explanation.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

    # Boutons de choix
    btn_yes = GameButton(
        ready_window,
        text="Oui, commencer!",
        command=lambda: (ready_window.destroy(), app.game_manager.select_random_objects()),
        width=15,
        color=COLORS["accent"]
    )
    btn_yes.place(relx=0.5, rely=0.65, anchor=tk.CENTER)

    btn_no = GameButton(
        ready_window,
        text="Non, retour",
        command=ready_window.destroy,
        width=15,
        color="#F44336"
    )
    btn_no.place(relx=0.5, rely=0.85, anchor=tk.CENTER)

def show_timeout_message(parent_window, app, message, callback=None):
    timeout_window = Toplevel(parent_window)
    timeout_window.title("Temps écoulé")
    timeout_window.geometry("300x150")
    timeout_window.configure(bg=COLORS["background"])

    app.center_window(timeout_window, 300, 150)

    # Message
    msg_label = tk.Label(
        timeout_window,
        text=message,
        font=("Helvetica", 12, "bold"),
        bg=COLORS["background"],
        fg=COLORS["text"]
    )
    msg_label.pack(pady=20)

    continue_btn = GameButton(
        timeout_window,
        text="Continuer",
        command=lambda: (timeout_window.destroy(), callback() if callback else None),
        width=15,
        color=COLORS["primary"]
    )
    continue_btn.pack(pady=10)

def show_success_message(parent_window, app, message, callback=None):
    try:

        app.timer_active = False

        success_window = Toplevel(parent_window)
        success_window.title("Réussite !")
        success_window.geometry("400x200")
        success_window.configure(bg=COLORS["background"])

        app.center_window(success_window, 400, 200)

        # Message de félicitations
        msg_label = tk.Label(
            success_window,
            text=message,
            font=("Helvetica", 14, "bold"),
            bg=COLORS["background"],
            fg=COLORS["primary"]
        )
        msg_label.pack(pady=20)

        continue_btn = GameButton(
            success_window,
            text="Continuer",
            command=lambda: (success_window.destroy(), callback() if callback else None),
            width=15,
            color=COLORS["primary"]
        )
        continue_btn.pack(pady=10)

        canvas = Canvas(success_window, width=400, height=200, bg=COLORS["background"], highlightthickness=0)
        canvas.place(x=0, y=0)
        create_confetti_effect(app, canvas)

    except Exception as e:
        print(f"Erreur lors de l'affichage du message de réussite: {e}")
        if callback:
            callback()

def create_results_window(parent_window, app, title="Résultats du jeu"):
    results_window = Toplevel(parent_window)
    results_window.title(title)
    results_window.geometry("400x350")
    results_window.configure(bg=COLORS["background"])

    app.center_window(results_window, 400, 350)

    # Titre et résultats
    title_label = tk.Label(
        results_window,
        text="Fin du jeu!",
        font=("Helvetica", 16, "bold"),
        bg=COLORS["background"],
        fg=COLORS["text"]
    )
    title_label.pack(pady=20)

    # Affichage des scores
    total_objects = len(getattr(app, 'object_vars', {}))

    player1_result = tk.Label(
        results_window,
        text=f"{app.player1_name}: {app.player1_score}/{total_objects} objets",
        font=("Helvetica", 14),
        bg=COLORS["background"],
        fg=COLORS["primary"]
    )
    player1_result.pack(pady=5)

    player2_result = tk.Label(
        results_window,
        text=f"{app.player2_name}: {app.player2_score}/{total_objects} objets",
        font=("Helvetica", 14),
        bg=COLORS["background"],
        fg=COLORS["accent"]
    )
    player2_result.pack(pady=5)

    # Détermination du gagnant
    if app.player1_score > app.player2_score:
        winner_text = f"{app.player1_name} gagne avec {app.player1_score} objets trouvés !"
    elif app.player2_score > app.player1_score:
        winner_text = f"{app.player2_name} gagne avec {app.player2_score} objets trouvés !"
    else:
        winner_text = "Match nul avec le même nombre d'objets !"

    winner_label = tk.Label(
        results_window,
        text=winner_text,
        font=("Helvetica", 16, "bold"),
        bg=COLORS["background"],
        fg=COLORS["text"]
    )
    winner_label.pack(pady=20)

    # Bouton retour
    return_btn = GameButton(
        results_window,
        text="Retour au menu",
        command=lambda: (results_window.destroy(), parent_window.destroy(), app.show_main_window()),
        width=15,
        color=COLORS["primary"]
    )
    return_btn.pack(pady=10)

    return results_window
