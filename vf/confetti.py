import random
import math

class Confetti:
    def __init__(self, canvas, x, y, colors):
        self.canvas = canvas
        self.x = x
        self.y = y

        self.size = random.randint(5, 15)
        self.color = random.choice(colors)
        self.vx = random.uniform(-1, 1)
        self.vy = random.uniform(1, 3)

        # Rotation et animation
        self.angle = random.uniform(0, 2 * math.pi)
        self.rotation_speed = random.uniform(-0.1, 0.1)
        self.oscillation_speed = random.uniform(0.05, 0.1)

        # Création de la forme
        shape_type = random.choice(["oval", "rect"])
        if shape_type == "oval":
            self.id = canvas.create_oval(
                x - self.size/2, y - self.size/2,
                x + self.size/2, y + self.size/2,
                fill=self.color, outline=""
            )
        else:
            self.id = canvas.create_rectangle(
                x - self.size/2, y - self.size/2,
                x + self.size/2, y + self.size/2,
                fill=self.color, outline=""
            )

        # Durée de vie
        self.lifetime = random.randint(50, 100)
        self.opacity = 1.0
        self.age = 0

    def update(self):
        # Vieillissement
        self.age += 1

        # Vérification de fin de vie
        if self.age > self.lifetime or self.y > self.canvas.winfo_height():
            return False

        # Mise à jour de l'angle
        self.angle += self.rotation_speed

        self.vx += math.sin(self.angle) * self.oscillation_speed

        # Effet de gravité
        self.vy += 0.05

        self.vx *= 0.99

        # Mise à jour de la position
        self.x += self.vx
        self.y += self.vy

        # Déplacement sur le canvas
        self.canvas.move(self.id, self.vx, self.vy)

        return True
