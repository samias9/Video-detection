import random
import tkinter as tk

# Classe pour l'animation des confettis
class Confetti:
    def __init__(self, canvas, x, y, colors):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.size = random.randint(5, 15)
        self.color = random.choice(colors)
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-5, -2)
        self.gravity = 0.1

        # Créer la forme du confetti (carré, cercle ou triangle)
        shape_type = random.randint(0, 2)
        if shape_type == 0:  # Carré
            self.id = canvas.create_rectangle(
                x, y, x + self.size, y + self.size,
                fill=self.color, outline=""
            )
        elif shape_type == 1:  # Cercle
            self.id = canvas.create_oval(
                x, y, x + self.size, y + self.size,
                fill=self.color, outline=""
            )
        else:  # Triangle
            self.id = canvas.create_polygon(
                x, y,
                x + self.size, y + self.size,
                x - self.size, y + self.size,
                fill=self.color, outline=""
            )

    def update(self):
        # Mise à jour de la position
        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy

        # Rotation aléatoire (simplement déplacer le confetti)
        self.canvas.move(self.id, self.vx, self.vy)

        # Vérifier si le confetti est toujours visible
        if self.y > self.canvas.winfo_height() + 20:
            return False
        return True
