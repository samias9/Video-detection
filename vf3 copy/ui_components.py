import tkinter as tk
from PIL import Image, ImageTk
import os
import sys
# Définition des couleurs (à utiliser dans les composants)
COLORS = {
    "primary": "#3498db",
    "secondary": "#2980b9",
    "background": "#f5f5f5",
    "text": "#0066cc",  # Texte en bleu
    "accent": "#e74c3c",
    "dark_bg": "#34495e",
    "light_text": "#ecf0f1"
}

class TextOnlyButton(tk.Button):
    def __init__(self, master, text, command=None, color=COLORS["primary"],
                 hover_color=COLORS["secondary"], text_color=COLORS["text"],  # Texte en bleu
                 width=18, height=2, **kwargs):
        super().__init__(
            master,
            text=text,
            command=command,
            bg=color,
            fg=text_color,
            activebackground=hover_color,
            activeforeground=text_color,
            relief=tk.FLAT,
            borderwidth=0,
            width=width,
            height=height,
            cursor="hand2",
            font=("Helvetica", 11, "bold"),
            **kwargs
        )

        # Effets de survol
        self.bind("<Enter>", lambda e: self.config(background=hover_color))
        self.bind("<Leave>", lambda e: self.config(background=color))

class ObjectCheckButton(tk.Checkbutton):
    def __init__(self, master, text, var, **kwargs):
        super().__init__(
            master,
            text=text,
            variable=var,
            font=kwargs.pop("font", ("Helvetica", 11)),
            bg=COLORS["background"],
            fg=COLORS["text"],  # Texte en bleu
            activebackground=COLORS["secondary"],
            activeforeground=COLORS["light_text"],
            selectcolor=COLORS["primary"],
            **kwargs
        )

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def load_icon(filename, size=(32, 32)):
    try:
        # Essayer d'abord le chemin direct
        direct_path = os.path.join("icons", filename)
        if os.path.exists(direct_path):
            img = Image.open(direct_path).resize(size, Image.LANCZOS)
            return ImageTk.PhotoImage(img)

        # Sinon, essayer avec resource_path
        full_path = resource_path(os.path.join("icons", filename))
        print(f"Recherche de l'icône: {full_path}")
        if not os.path.exists(full_path):
            print(f"[AVERTISSEMENT] Icône non trouvée: {filename}")
            # Créer une icône de substitution colorée
            return create_placeholder_icon(size, filename)
        img = Image.open(full_path).resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception as e:
        print(f"[ERREUR] Impossible de charger l'icône {filename}: {e}")
        return create_placeholder_icon(size, filename)

def create_placeholder_icon(size, filename):
    img = Image.new('RGBA', size, color=(52, 152, 219, 255))  # Bleu par défaut

    # Couleurs différentes selon le type d'icône
    if "play" in filename:
        img = Image.new('RGBA', size, color=(46, 204, 113, 255))  # Vert
    elif "pause" in filename:
        img = Image.new('RGBA', size, color=(241, 196, 15, 255))  # Jaune
    elif "stop" in filename or "return" in filename:
        img = Image.new('RGBA', size, color=(231, 76, 60, 255))   # Rouge
    elif "webcam" in filename:
        img = Image.new('RGBA', size, color=(155, 89, 182, 255))  # Violet

    return ImageTk.PhotoImage(img)
