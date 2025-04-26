     # Récupère la liste des objets sélectionnés
        objects_to_detect = [obj for obj, var in self.selected_objects.items() if var.get()]

        # Ferme la fenêtre de sélection
        select_window.destroy()

        # Cache la fenêtre principale
        self.hide_main_window()

        # Affiche les objets sélectionnés et passe à la configuration des joueurs
        self.show_selected_objects(objects_to_detect)
