# yolo_processor.py
import cv2
import datetime
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk
from ultralytics import YOLO
import threading
import queue
import time

CONFIDENCE_THRESHOLD_LIMIT = 0.5
DEVICE = "mps"  # Pour Mac avec GPU, utilisez "cuda" pour NVIDIA GPU ou "cpu" pour CPU

# Chargement du modèle YOLO
print("Chargement du modèle YOLO...")
model = YOLO("yolov8m.pt")
print("Modèle YOLO chargé!")

# Variables de contrôle globales
stop_detection = False
_paused = False
processing_lock = threading.Lock()
detection_thread = None
frame_queue = queue.Queue(maxsize=1)

# Set pour stocker les objets déjà détectés
detected_objects_set = set()

def toggle_pause():
    """Active/désactive la pause du traitement vidéo"""
    global _paused
    _paused = not _paused
    return _paused

def is_paused():
    """Retourne l'état de pause actuel"""
    return _paused

def reset_detected_objects():
    """Réinitialise le set des objets détectés"""
    global detected_objects_set
    with processing_lock:
        detected_objects_set = set()
    print("Objets détectés réinitialisés")

def get_detectable_objects():
    """Renvoie la liste des objets détectables par YOLO"""
    return list(model.names.values())

def get_detected_objects_list():
    """Renvoie la liste des noms d'objets détectés dans le set global"""
    global detected_objects_set
    with processing_lock:
        return [model.names[cls_id] for cls_id in detected_objects_set if cls_id in model.names]

def show_victory_message(window, objects_detected):
    """Affiche un message de victoire dans une fenêtre pop-up"""
    try:
        victory_window = tk.Toplevel(window)
        victory_window.title("Victoire !")
        victory_window.geometry("400x300")

        # Style colors
        primary_color = "#3498db"
        light_text = "#ecf0f1"
        dark_bg = "#34495e"

        # Configuration de la fenêtre
        victory_window.configure(bg=dark_bg)

        # Titre
        title_label = tk.Label(
            victory_window,
            text="VOUS AVEZ GAGNÉ !",
            font=("Helvetica", 24, "bold"),
            bg=dark_bg,
            fg=light_text
        )
        title_label.pack(pady=20)

        # Message
        msg_label = tk.Label(
            victory_window,
            text=f"Tous les objets sélectionnés ont été détectés!",
            font=("Helvetica", 14),
            bg=dark_bg,
            fg=light_text,
            wraplength=350
        )
        msg_label.pack(pady=10)

        # Liste des objets détectés
        objects_text = "\n".join([f"✓ {obj}" for obj in objects_detected])
        objects_label = tk.Label(
            victory_window,
            text=objects_text,
            font=("Helvetica", 12),
            bg=dark_bg,
            fg=light_text,
            justify=tk.LEFT
        )
        objects_label.pack(pady=10)

        # Bouton pour fermer
        close_btn = tk.Button(
            victory_window,
            text="Continuer",
            command=victory_window.destroy,
            bg=primary_color,
            fg=light_text,
            font=("Helvetica", 12, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=5
        )
        close_btn.pack(pady=20)

        # Centrer la fenêtre
        victory_window.update_idletasks()
        width = victory_window.winfo_width()
        height = victory_window.winfo_height()
        x = (window.winfo_rootx() + window.winfo_width() // 2) - (width // 2)
        y = (window.winfo_rooty() + window.winfo_height() // 2) - (height // 2)
        victory_window.geometry(f"+{x}+{y}")

        # Empêcher l'interaction avec la fenêtre parent
        victory_window.transient(window)
        victory_window.grab_set()
    except Exception as e:
        print(f"Erreur lors de l'affichage du message de victoire: {e}")

def process_frame(frame, object_ids=None, on_object_detected=None):
    """Traite une frame avec YOLO et retourne la frame annotée et les détections"""
    global detected_objects_set

    try:
        # Mesure du temps de traitement pour le FPS
        start = datetime.datetime.now()

        # Analyse de la frame avec YOLO
        result = model(frame)[0]

        # Récupération des résultats
        bboxes = np.array(result.boxes.xyxy.cpu(), dtype="int")
        classes = np.array(result.boxes.cls.cpu(), dtype="int")
        confidence = np.array(result.boxes.conf.cpu(), dtype="float")

        # Compteur d'objets détectés dans cette frame
        detected_count = 0
        current_frame_detections = set()

        # Traitement des détections
        for cls, bbox, conf in zip(classes, bboxes, confidence):
            # Ignorer les objets qui ne sont pas dans la liste si une liste est fournie
            if object_ids is not None and cls not in object_ids:
                continue

            # Ignorer les détections de faible confiance
            if conf < CONFIDENCE_THRESHOLD_LIMIT:
                continue

            # Récupérer le nom de l'objet
            object_name = model.names[cls]

            # Vérifier si c'est une nouvelle détection
            with processing_lock:
                if cls not in detected_objects_set:
                    detected_objects_set.add(cls)
                    # Notifier la détection d'un nouvel objet
                    if on_object_detected:
                        on_object_detected(object_name)

            # Dessiner le rectangle et le texte sur la frame
            (x, y, x2, y2) = bbox
            color = (0, 255, 0) if conf > 0.6 else (66, 224, 245) if conf > 0.3 else (78, 66, 245)
            cv2.rectangle(frame, (x, y), (x2, y2), color, 2)
            cv2.putText(frame, f"{object_name}: {conf:.2f}", (x, y - 5), cv2.FONT_HERSHEY_PLAIN, 2, color, 2)

            detected_count += 1
            current_frame_detections.add(cls)

        # Calcul du FPS
        end = datetime.datetime.now()
        fps = 1 / (end - start).total_seconds()

        # Afficher le FPS sur la frame
        cv2.putText(frame, f"FPS: {fps:.2f}", (50, 50), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 2)

        return frame, fps, detected_count, len(detected_objects_set)
    except Exception as e:
        print(f"Erreur lors du traitement de la frame: {e}")
        return frame, 0, 0, 0

def video_processing_thread(video_source, on_object_detected=None, object_ids=None):
    """Thread dédié au traitement vidéo pour éviter de bloquer l'interface"""
    global stop_detection, _paused

    try:
        # Ouverture de la source vidéo
        cap = cv2.VideoCapture(video_source)
        if not cap.isOpened():
            print(f"Erreur lors de l'ouverture de la source vidéo: {video_source}")
            return

        print(f"Traitement vidéo démarré - Source: {video_source}")

        while not stop_detection:
            # Si en pause, attendre
            if _paused:
                time.sleep(0.1)
                continue

            # Lire une frame
            ret, frame = cap.read()
            if not ret:
                print("Fin du flux vidéo")
                break

            # Traiter la frame avec YOLO
            processed_frame, fps, detected_count, total_detected = process_frame(
                frame,
                object_ids=object_ids,
                on_object_detected=on_object_detected
            )

            # Convertir pour l'affichage
            display_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)

            # Mettre la frame dans la queue pour l'interface
            try:
                # Vider la queue si elle est pleine pour toujours avoir la frame la plus récente
                if frame_queue.full():
                    frame_queue.get_nowait()
                frame_queue.put((display_frame, fps, detected_count, total_detected), block=False)
            except queue.Full:
                pass  # Ignorer si la queue est pleine

        # Libérer les ressources
        cap.release()
        print("Traitement vidéo terminé")

    except Exception as e:
        print(f"Erreur dans le thread de traitement vidéo: {e}")
    finally:
        # S'assurer que les ressources sont libérées
        if 'cap' in locals() and cap.isOpened():
            cap.release()

def process_video(video_source, canvas, window, detection_label=None, fps_label=None, progress=None, objects_to_detect=None, on_object_detected=None):
    """Fonction principale pour démarrer le traitement vidéo"""
    global stop_detection, _paused, detection_thread, detected_objects_set

    # Réinitialiser les variables globales
    with processing_lock:
        stop_detection = False
        _paused = False
        detected_objects_set = set()

    # Convertir les noms d'objets en IDs
    object_ids = None
    if objects_to_detect:
        name_to_id = {v: k for k, v in model.names.items()}
        object_ids = [name_to_id[obj] for obj in objects_to_detect if obj in name_to_id]

    # Arrêter le thread existant s'il est actif
    if detection_thread and detection_thread.is_alive():
        with processing_lock:
            stop_detection = True
        detection_thread.join(timeout=1.0)

    # Vider la queue
    while not frame_queue.empty():
        try:
            frame_queue.get_nowait()
        except:
            pass

    # Variable pour suivre si le message de victoire a été affiché
    victory_shown = [False]

    # Démarrer le thread de traitement vidéo
    detection_thread = threading.Thread(
        target=video_processing_thread,
        args=(video_source, on_object_detected, object_ids),
        daemon=True
    )
    detection_thread.start()

    # Fonction pour mettre à jour l'interface
    def update_ui():
        if stop_detection or not canvas.winfo_exists():
            return

        try:
            # Vérifier si une nouvelle frame est disponible
            if not frame_queue.empty():
                display_frame, fps, detected_count, total_detected = frame_queue.get_nowait()

                # Redimensionner pour l'affichage
                pil_img = Image.fromarray(display_frame)
                img_width, img_height = pil_img.size
                canvas_width = canvas.winfo_width()
                canvas_height = canvas.winfo_height()

                # Calculer les dimensions pour maintenir le ratio
                if canvas_width > 1 and canvas_height > 1:  # S'assurer que le canvas est initialisé
                    ratio = min(canvas_width/img_width, canvas_height/img_height)
                    new_width = int(img_width * ratio)
                    new_height = int(img_height * ratio)
                    pil_img = pil_img.resize((new_width, new_height), Image.LANCZOS)

                # Convertir en format PhotoImage pour Tkinter
                tk_img = ImageTk.PhotoImage(pil_img)

                # Afficher l'image dans le canvas
                canvas.delete("all")
                canvas.create_image(
                    canvas_width//2 if canvas_width > 1 else 0,
                    canvas_height//2 if canvas_height > 1 else 0,
                    anchor=tk.CENTER,
                    image=tk_img
                )
                canvas.image = tk_img  # Garder une référence

                # Mettre à jour les étiquettes d'information
                if fps_label and fps_label.winfo_exists():
                    fps_label.config(text=f"FPS: {fps:.2f}")

                if detection_label and detection_label.winfo_exists():
                    if objects_to_detect:
                        detection_label.config(text=f"Objets détectés: {total_detected}/{len(object_ids)}")
                    else:
                        detection_label.config(text=f"Objets détectés: {detected_count}")

                # Vérifier la victoire (tous les objets détectés)
                if object_ids and not victory_shown[0] and total_detected >= len(object_ids):
                    victory_shown[0] = True
                    with processing_lock:
                        detected_names = [model.names[obj_id] for obj_id in detected_objects_set if obj_id in model.names]
                    window.after(100, lambda: show_victory_message(window, detected_names))

            # Programmer la prochaine mise à jour
            if not stop_detection and window.winfo_exists():
                window.after(10, update_ui)

        except Exception as e:
            print(f"Erreur dans update_ui: {e}")
            if not stop_detection and window.winfo_exists():
                window.after(10, update_ui)

    # Démarrer la mise à jour de l'interface
    window.after(10, update_ui)

    # Gérer la fermeture de la fenêtre
    def on_window_close():
        global stop_detection
        with processing_lock:
            stop_detection = True
        window.destroy()

    window.protocol("WM_DELETE_WINDOW", on_window_close)

def stop_video():
    """Arrête le traitement vidéo en cours"""
    global stop_detection

    print("Arrêt du traitement vidéo demandé...")
    with processing_lock:
        stop_detection = True

    # Attendre que le thread se termine (avec timeout)
    if detection_thread and detection_thread.is_alive():
        detection_thread.join(timeout=2.0)
        print("Thread de traitement vidéo arrêté")
