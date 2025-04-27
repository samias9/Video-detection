import tkinter as tk
from tkinter import Canvas
import random
from ui_components import COLORS

class ForestBackground:
    def __init__(self, canvas, width, height):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.elements = []

        # Dessiner le fond
        self.draw_sky()
        self.draw_ground()
        self.draw_mountains()
        self.draw_trees()
        self.draw_clouds()
        self.draw_mushrooms()

    def draw_sky(self):
        # Ciel
        self.sky = self.canvas.create_rectangle(
            0, 0, self.width, self.height,
            fill=COLORS["background"],
            outline=""
        )

    def draw_ground(self):
        # Sol
        ground_height = int(self.height * 0.35)
        self.ground = self.canvas.create_rectangle(
            0, self.height - ground_height, self.width, self.height,
            fill=COLORS["grass"],
            outline=""
        )

        # La texture au sol (petits triangles verts)
        for _ in range(300):
            x = random.randint(0, self.width)
            y = random.randint(int(self.height - ground_height), self.height)
            size = random.randint(3, 8)
            shade = random.choice([
                self._lighten_color(COLORS["grass"]),
                self._darken_color(COLORS["grass"])
            ])

            triangle = self.canvas.create_polygon(
                x, y,
                x - size/2, y + size,
                x + size/2, y + size,
                fill=shade,
                outline=""
            )
            self.elements.append(triangle)

    def draw_mountains(self):
        # Montagnes en arrière-plan
        ground_start = int(self.height - (self.height * 0.35))
        mountain_height = int(self.height * 0.25)

        #  plusieurs montagnes de tailles différentes
        mountain_positions = [
            int(self.width * 0.1),
            int(self.width * 0.25),
            int(self.width * 0.4),
            int(self.width * 0.6),
            int(self.width * 0.75),
            int(self.width * 0.9)
        ]

        for x_pos in mountain_positions:
            # Taille aléatoire
            size_factor = random.uniform(0.7, 1.2)
            m_height = mountain_height * size_factor
            m_width = m_height * 1.2

            # Forme de la montagne
            mountain_points = [
                x_pos - m_width/2, ground_start,
                x_pos, ground_start - m_height,
                x_pos + m_width/2, ground_start
            ]

            color = self._get_random_mountain_color()

            mountain = self.canvas.create_polygon(
                mountain_points,
                fill=color,
                outline=""
            )
            self.elements.append(mountain)

            snow_points = [
                x_pos - m_width/5, ground_start - m_height * 0.75,
                x_pos, ground_start - m_height,
                x_pos + m_width/5, ground_start - m_height * 0.75
            ]

            snow = self.canvas.create_polygon(
                snow_points,
                fill="white",
                outline=""
            )
            self.elements.append(snow)

    def draw_trees(self):
        ground_start = int(self.height - (self.height * 0.35))

        # Grandes arbres en arrière-plan
        for _ in range(15):
            x = random.randint(0, self.width)
            y = random.randint(int(ground_start * 0.9), ground_start)
            size = random.randint(30, 80)
            self._draw_tree(x, y, size)

        # Petites arbres au premier plan
        for _ in range(20):
            x = random.randint(0, self.width)
            y = random.randint(ground_start, int(self.height * 0.85))
            size = random.randint(15, 40)
            self._draw_tree(x, y, size)

    def _draw_tree(self, x, y, size):
        tree_type = random.choice(["pine", "round", "bush"])

        if tree_type == "pine":
            # Tronc
            trunk = self.canvas.create_rectangle(
                x - size/10, y,
                x + size/10, y + size * 0.3,
                fill="#8B4513",
                outline=""
            )
            self.elements.append(trunk)

            # Feuillage (sapin)
            for i in range(3):
                factor = 1 - (i * 0.25)
                triangle = self.canvas.create_polygon(
                    x - size/2 * factor, y - size * 0.3 * i,
                    x, y - size * 0.3 * (i+1),
                    x + size/2 * factor, y - size * 0.3 * i,
                    fill=self._get_random_tree_color(),
                    outline=""
                )
                self.elements.append(triangle)

        elif tree_type == "round":
            # Tronc
            trunk = self.canvas.create_rectangle(
                x - size/15, y,
                x + size/15, y + size * 0.4,
                fill="#8B4513",
                outline=""
            )
            self.elements.append(trunk)

            # Feuillage rond
            leaf_color = self._get_random_tree_color()
            for i in range(2):
                offset_x = random.uniform(-size/5, size/5)
                offset_y = random.uniform(-size/6, size/10)
                radius = size/2 * random.uniform(0.8, 1.1)

                leaves = self.canvas.create_oval(
                    x - radius + offset_x, y - radius + offset_y,
                    x + radius + offset_x, y - radius * 0.5 + offset_y,
                    fill=leaf_color,
                    outline=""
                )
                self.elements.append(leaves)

        else:
            # Buisson (plus petit, pas de tronc)
            for i in range(3):
                offset_x = random.uniform(-size/3, size/3)
                offset_y = random.uniform(-size/4, size/4)
                radius = size/3 * random.uniform(0.7, 1.2)

                bush = self.canvas.create_oval(
                    x - radius + offset_x, y - radius + offset_y,
                    x + radius + offset_x, y + radius * 0.8 + offset_y,
                    fill=self._get_random_tree_color(),
                    outline=""
                )
                self.elements.append(bush)

    def draw_clouds(self):
        # Quelques nuages flottants
        for _ in range(5):
            x = random.randint(0, self.width)
            y = random.randint(int(self.height * 0.1), int(self.height * 0.3))
            size = random.randint(40, 100)

            cloud_color = "#FFFFFF"

            # Plusieurs cercles pour former un nuage
            for i in range(4):
                offset_x = random.uniform(-size/2, size/2)
                offset_y = random.uniform(-size/4, size/4)
                radius = size/2 * random.uniform(0.5, 1.0)

                cloud_part = self.canvas.create_oval(
                    x - radius + offset_x, y - radius + offset_y,
                    x + radius + offset_x, y + radius * 0.4 + offset_y,
                    fill=cloud_color,
                    outline=""
                )
                self.elements.append(cloud_part)

    def draw_mushrooms(self):
        # Petits champignons par terre
        ground_start = int(self.height - (self.height * 0.35))

        for _ in range(8):
            x = random.randint(0, self.width)
            y = random.randint(ground_start, int(self.height * 0.9))
            size = random.randint(8, 15)

            # Pied du champignon
            stem = self.canvas.create_rectangle(
                x - size/6, y,
                x + size/6, y - size * 0.8,
                fill="#F5F5DC",
                outline=""
            )
            self.elements.append(stem)

            # Chapeau du champignon
            cap_color = random.choice(["#FF0000", "#FF6347", "#FF4500"])
            cap = self.canvas.create_oval(
                x - size/2, y - size * 1.2,
                x + size/2, y - size * 0.7,
                fill=cap_color,
                outline=""
            )
            self.elements.append(cap)

            # Points blancs sur le chapeau
            for _ in range(3):
                dot_x = x + random.uniform(-size/3, size/3)
                dot_y = y - size + random.uniform(-size/6, size/6)
                dot_size = random.uniform(1, 3)

                dot = self.canvas.create_oval(
                    dot_x - dot_size, dot_y - dot_size,
                    dot_x + dot_size, dot_y + dot_size,
                    fill="white",
                    outline=""
                )
                self.elements.append(dot)

    def _get_random_tree_color(self):
        colors = [
            "#2E7D32",  # Vert foncé
            "#388E3C",  # Vert
            "#43A047",  # Vert clair
            "#1B5E20",  # Vert très foncé
            "#4CAF50"   # Vert moyen
        ]
        return random.choice(colors)

    def _get_random_mountain_color(self):
        # Retourne une couleur aléatoire pour les montagnes
        colors = [
            "#795548",  # Marron
            "#6D4C41",  # Marron foncé
            "#5D4037",  # Marron très foncé
            "#8D6E63",  # Marron clair
            "#4E342E"   # Marron grisâtre
        ]
        return random.choice(colors)

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
