import tkinter as tk
from tkinter import Button
from PIL import Image, ImageTk
import os

# Palette de couleurs style forestier/jeu
COLORS = {
    "primary": "#4CAF50",     # Vert forêt
    "accent": "#FF9800",      # Orange pour boutons
    "background": "#81D4FA",  # Bleu ciel
    "dark_bg": "#2E7D32",     # Vert foncé
    "text": "#FFFFFF",        # Texte blanc
    "light_text": "#FFFFFF",  # Texte blanc
    "button_border": "#FFFFFF", # Bordure blanche
    "forest_green": "#388E3C", # Vert pour les arbres
    "mountain": "#795548",    # Marron pour les montagnes
    "grass": "#8BC34A"        # Vert pour l'herbe
}

class GameButton(Button):
    def __init__(self, master=None, text="", command=None, width=15, height=1, color=COLORS["accent"]):
        bg_color = color
        hover_color = self._lighten_color(color)
        active_color = self._darken_color(color)

        text_color = "#000000"

        super().__init__(
            master,
            text=text,
            command=command,
            width=width,
            height=height,
            bg=bg_color,
            fg=text_color,
            activebackground= "#2E7D32",
            activeforeground=text_color,
            relief=tk.RAISED,
            bd=2,
            font=("Arial Rounded MT Bold", 16, "bold")
        )

        self.config(highlightbackground=COLORS["button_border"], highlightthickness=2)

        # Survol
        self.bind("<Enter>", lambda e: self.config(bg=hover_color))
        self.bind("<Leave>", lambda e: self.config(bg=bg_color))

    def _lighten_color(self, hex_color, factor=0.2):
        r, g, b = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)
        r = min(255, int(r + (255 - r) * factor))
        g = min(255, int(g + (255 - g) * factor))
        b = min(255, int(b + (255 - b) * factor))
        return f"#{r:02x}{g:02x}{b:02x}"

    def _darken_color(self, hex_color, factor=0.2):
        r, g, b = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)
        r = max(0, int(r * (1 - factor)))
        g = max(0, int(g * (1 - factor)))
        b = max(0, int(b * (1 - factor)))
        return f"#{r:02x}{g:02x}{b:02x}"

class CircleIconButton(Button):
    def __init__(self, master=None, text="", icon_path=None, command=None, size=60, color="#FF5722"):
        bg_color = color
        hover_color = self._lighten_color(color)
        active_color = self._darken_color(color)

        super().__init__(
            master,
            text="",
            command=command,
            bg=bg_color,
            activebackground=active_color,
            relief=tk.RAISED,
            bd=3,
            width=size//10,
            height=size//20
        )

        self.config(highlightbackground=COLORS["button_border"], highlightthickness=3)

        self.icon = None
        if icon_path and os.path.exists(icon_path):
            try:
                img = Image.open(icon_path).resize((size-20, size-20))
                self.icon = ImageTk.PhotoImage(img)
                self.config(image=self.icon, compound=tk.CENTER)
            except Exception as e:
                print(f"Erreur lors du chargement de l'icône {icon_path}: {e}")
                self.config(text=text, fg="white", font=("Arial Rounded MT Bold", 12, "bold"))
        else:
            self.config(text=text, fg="white", font=("Arial Rounded MT Bold", 12, "bold"))

        # Survol
        self.bind("<Enter>", lambda e: self.config(bg=hover_color))
        self.bind("<Leave>", lambda e: self.config(bg=bg_color))

        self.bind("<Configure>", self._make_circle)

    def _make_circle(self, event=None):
        width = self.winfo_width()
        height = self.winfo_height()
        if width > 0 and height > 0:
            size = min(width, height)
            self.config(width=size//10, height=size//20)


    def _lighten_color(self, hex_color, factor=0.2):
        r, g, b = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)
        r = min(255, int(r + (255 - r) * factor))
        g = min(255, int(g + (255 - g) * factor))
        b = min(255, int(b + (255 - b) * factor))
        return f"#{r:02x}{g:02x}{b:02x}"

    def _darken_color(self, hex_color, factor=0.2):
        r, g, b = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)
        r = max(0, int(r * (1 - factor)))
        g = max(0, int(g * (1 - factor)))
        b = max(0, int(b * (1 - factor)))
        return f"#{r:02x}{g:02x}{b:02x}"

def load_icon(filename, size=(32, 32)):
    try:
        # Vérification de l'existence du fichier
        icon_path = os.path.join("icons", filename)
        if os.path.exists(icon_path):
            img = Image.open(icon_path).resize(size, Image.LANCZOS)
            return ImageTk.PhotoImage(img)
        else:
            print(f"Icône non trouvée: {icon_path}")
            return create_placeholder_icon(size)
    except Exception as e:
        print(f"Erreur lors du chargement de l'icône {filename}: {e}")
        return create_placeholder_icon(size)

def create_placeholder_icon(size=(32, 32)):
    img = Image.new("RGB", size, COLORS["primary"])
    return ImageTk.PhotoImage(img)
