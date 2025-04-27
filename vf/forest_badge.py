import tkinter as tk
from tkinter import Canvas
import math
from ui_components import COLORS

class BadgeWithRibbon:
    def __init__(self, canvas, x, y, width, height, title, bg_color="#EEEEEE", ribbon_color=COLORS["primary"]):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.title = title
        self.bg_color = bg_color
        self.ribbon_color = ribbon_color

        self.draw_badge()

    def draw_badge(self):
        center_x = self.x + self.width/2
        center_y = self.y + self.height/2
        radius = min(self.width, self.height) / 2 * 0.9

        #  la forme en étoile/fleur
        points = []
        inner_radius = radius * 0.85  # Rayon intérieur pour effet d'ondulation
        num_points = 12

        for i in range(num_points * 2):
            angle = math.pi * 2 * i / (num_points * 2)
            r = radius if i % 2 == 0 else inner_radius
            points.append(center_x + r * math.cos(angle))
            points.append(center_y + r * math.sin(angle))

        #  le fond du badge
        self.badge_bg = self.canvas.create_polygon(
            points,
            fill=self.bg_color,
            outline="white",
            width=4,
            smooth=True
        )

        # Ombre intérieure
        inner_points = []
        inner_radius2 = inner_radius * 0.9

        for i in range(num_points * 2):
            angle = math.pi * 2 * i / (num_points * 2)
            r = inner_radius * 0.95 if i % 2 == 0 else inner_radius2
            inner_points.append(center_x + r * math.cos(angle))
            inner_points.append(center_y + r * math.sin(angle))

        self.inner_shadow = self.canvas.create_polygon(
            inner_points,
            fill=self._darken_color(self.bg_color),
            outline="",
            smooth=True
        )

        #  le ruban
        ribbon_width = self.width * 1.2
        ribbon_height = self.height * 0.2
        ribbon_y = center_y

        # Points du ruban (forme incurvée)
        ribbon_points = [
            center_x - ribbon_width/2, ribbon_y,
            center_x - ribbon_width/2 + ribbon_height*0.5, ribbon_y - ribbon_height/2,
            center_x + ribbon_width/2 - ribbon_height*0.5, ribbon_y - ribbon_height/2,
            center_x + ribbon_width/2, ribbon_y,
            center_x + ribbon_width/2 - ribbon_height*0.5, ribbon_y + ribbon_height/2,
            center_x - ribbon_width/2 + ribbon_height*0.5, ribbon_y + ribbon_height/2
        ]

        # Rectangle du ruban
        self.ribbon = self.canvas.create_polygon(
            ribbon_points,
            fill=self.ribbon_color,
            outline="white",
            width=3,
            smooth=True
        )

        # Extrémités du ruban (triangles)
        left_ribbon_end = [
            center_x - ribbon_width/2, ribbon_y,
            center_x - ribbon_width/2 - ribbon_height, ribbon_y - ribbon_height,
            center_x - ribbon_width/2 - ribbon_height, ribbon_y + ribbon_height
        ]

        right_ribbon_end = [
            center_x + ribbon_width/2, ribbon_y,
            center_x + ribbon_width/2 + ribbon_height, ribbon_y - ribbon_height,
            center_x + ribbon_width/2 + ribbon_height, ribbon_y + ribbon_height
        ]

        self.left_end = self.canvas.create_polygon(
            left_ribbon_end,
            fill=self.ribbon_color,
            outline="white",
            width=3,
            smooth=True
        )

        self.right_end = self.canvas.create_polygon(
            right_ribbon_end,
            fill=self.ribbon_color,
            outline="white",
            width=3,
            smooth=True
        )

        self.text = self.canvas.create_text(
            center_x, ribbon_y,
            text=self.title,
            font=("Arial Rounded MT Bold", int(ribbon_height*0.9), "bold"),
            fill="white"
        )

    def _darken_color(self, hex_color, factor=0.1):
        r, g, b = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)
        r = max(0, int(r * (1 - factor)))
        g = max(0, int(g * (1 - factor)))
        b = max(0, int(b * (1 - factor)))
        return f"#{r:02x}{g:02x}{b:02x}"

def create_forest_badge(canvas, x, y, width, height, title="Forest"):
    badge = BadgeWithRibbon(
        canvas,
        x,
        y,
        width,
        height,
        title,
        bg_color="#F5F5DC",
        ribbon_color="#4CAF50"
    )
    return badge
