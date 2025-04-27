import random
from confetti import Confetti

def create_confetti_effect(app, canvas, duration=3000):
    app.confetti_active = True
    app.confetti_particles = []

    confetti_colors = ["#FF5252", "#FFEB3B", "#4CAF50", "#2196F3", "#9C27B0", "#FF9800"]

    # Création des particules
    width = canvas.winfo_width()
    height = canvas.winfo_height()

    for _ in range(100):
        x = random.randint(0, width)
        y = random.randint(-50, 0)
        app.confetti_particles.append(Confetti(canvas, x, y, confetti_colors))

    # Animation
    def animate_confetti():
        if not app.confetti_active:
            for confetti in app.confetti_particles:
                canvas.delete(confetti.id)
            app.confetti_particles = []
            return

        active_particles = []
        for confetti in app.confetti_particles:
            if confetti.update():
                active_particles.append(confetti)
            else:
                canvas.delete(confetti.id)

        app.confetti_particles = active_particles

        # Boucle d'animation
        if app.confetti_particles:
            canvas.after(33, animate_confetti)
        else:
            app.confetti_active = False

    # Démarrage de l'animation
    animate_confetti()

    # Arrêt programmé
    canvas.after(duration, lambda: setattr(app, 'confetti_active', False))
