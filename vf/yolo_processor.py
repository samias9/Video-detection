import cv2
import datetime
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk
from ultralytics import YOLO
import threading
import queue
import time

# Configuration globale
CONFIDENCE_THRESHOLD_LIMIT = 0.5
DEVICE = "mps"  # Options: "mps" (Mac GPU), "cuda" (NVIDIA GPU), "cpu"

# Initialisation du modèle
print("Chargement du modèle YOLO...")
model = YOLO("yolov8m.pt")
print("Modèle YOLO chargé!")

# Variables de contrôle
stop_detection = False
_paused = False
processing_lock = threading.Lock()
detection_thread = None
frame_queue = queue.Queue(maxsize=1)
detected_objects_set = set()

def toggle_pause():
    global _paused
    _paused = not _paused
    return _paused

def is_paused():
    return _paused

def reset_detected_objects():
    global detected_objects_set
    with processing_lock:
        detected_objects_set = set()
    print("Objets détectés réinitialisés")

def get_detectable_objects():
    return list(model.names.values())

def get_detected_objects_list():
    global detected_objects_set
    with processing_lock:
        return [model.names[cls_id] for cls_id in detected_objects_set if cls_id in model.names]

def show_victory_message(window, objects_detected):
    try:
        victory_window = tk.Toplevel(window)
        victory_window.title("Victoire !")
        victory_window.geometry("400x300")

        # Couleurs de style
        primary_color = "#3498db"
        light_text = "#ecf0f1"
        dark_bg = "#34495e"

        victory_window.configure(bg=dark_bg)

        # Titre principal
        title_label = tk.Label(
            victory_window,
            text="VOUS AVEZ GAGNÉ !",
            font=("Helvetica", 24, "bold"),
            bg=dark_bg,
            fg=light_text
        )
        title_label.pack(pady=20)

        # Message de félicitations
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

        # Bouton de continuation
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

        # Centrage de la fenêtre
        victory_window.update_idletasks()
        width = victory_window.winfo_width()
        height = victory_window.winfo_height()
        x = (window.winfo_rootx() + window.winfo_width() // 2) - (width // 2)
        y = (window.winfo_rooty() + window.winfo_height() // 2) - (height // 2)
        victory_window.geometry(f"+{x}+{y}")

        # Focus modal
        victory_window.transient(window)
        victory_window.grab_set()
    except Exception as e:
        print(f"Erreur lors de l'affichage du message de victoire: {e}")

def process_frame(frame, object_ids=None, on_object_detected=None):
    global detected_objects_set

    try:
        # Mesure du temps pour calcul FPS
        start = datetime.datetime.now()

        # Analyse de l'image avec YOLO
        result = model(frame)[0]

        # Extraction des résultats
        bboxes = np.array(result.boxes.xyxy.cpu(), dtype="int")
        classes = np.array(result.boxes.cls.cpu(), dtype="int")
        confidence = np.array(result.boxes.conf.cpu(), dtype="float")

        detected_count = 0
        current_frame_detections = set()

        # Traitement de chaque détection
        for cls, bbox, conf in zip(classes, bboxes, confidence):
            # Filtrage selon les objets demandés
            if object_ids is not None and cls not in object_ids:
                continue

            # Filtrage selon le seuil de confiance
            if conf < CONFIDENCE_THRESHOLD_LIMIT:
                continue

            object_name = model.names[cls]

            # Gestion des nouvelles détections
            with processing_lock:
                if cls not in detected_objects_set:
                    detected_objects_set.add(cls)
                    if on_object_detected:
                        on_object_detected(object_name)

            # Affichage sur l'image
            (x, y, x2, y2) = bbox
            color = (0, 255, 0) if conf > 0.6 else (66, 224, 245) if conf > 0.3 else (78, 66, 245)
            cv2.rectangle(frame, (x, y), (x2, y2), color, 2)
            cv2.putText(frame, f"{object_name}: {conf:.2f}", (x, y - 5), cv2.FONT_HERSHEY_PLAIN, 2, color, 2)

            detected_count += 1
            current_frame_detections.add(cls)

        # Calcul et affichage du FPS
        end = datetime.datetime.now()
        fps = 1 / (end - start).total_seconds()
        cv2.putText(frame, f"FPS: {fps:.2f}", (50, 50), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 2)

        return frame, fps, detected_count, len(detected_objects_set)
    except Exception as e:
        print(f"Erreur lors du traitement de la frame: {e}")
        return frame, 0, 0, 0

def video_processing_thread(video_source, on_object_detected=None, object_ids=None):
    global stop_detection, _paused

    try:
        # Ouverture de la source vidéo
        cap = cv2.VideoCapture(video_source)
        if not cap.isOpened():
            print(f"Erreur lors de l'ouverture de la source vidéo: {video_source}")
            return

        print(f"Traitement vidéo démarré - Source: {video_source}")

        # Boucle principale de traitement
        while not stop_detection:
            if _paused:
                time.sleep(0.1)
                continue

            ret, frame = cap.read()
            if not ret:
                print("Fin du flux vidéo")
                break

            # Analyse avec YOLO
            processed_frame, fps, detected_count, total_detected = process_frame(
                frame,
                object_ids=object_ids,
                on_object_detected=on_object_detected
            )

            # Conversion pour affichage
            display_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)

            # Envoi à l'interface
            try:
                if frame_queue.full():
                    frame_queue.get_nowait()
                frame_queue.put((display_frame, fps, detected_count, total_detected), block=False)
            except queue.Full:
                pass

        # Libération des ressources
        cap.release()
        print("Traitement vidéo terminé")

    except Exception as e:
        print(f"Erreur dans le thread de traitement vidéo: {e}")
    finally:
        if 'cap' in locals() and cap.isOpened():
            cap.release()

def process_video(video_source, canvas, window, detection_label=None, fps_label=None, progress=None, objects_to_detect=None, on_object_detected=None):
    global stop_detection, _paused, detection_thread, detected_objects_set

    # Réinitialisation des variables de contrôle
    with processing_lock:
        stop_detection = False
        _paused = False
        detected_objects_set = set()

    # Conversion des noms d'objets en IDs
    object_ids = None
    if objects_to_detect:
        name_to_id = {v: k for k, v in model.names.items()}
        object_ids = [name_to_id[obj] for obj in objects_to_detect if obj in name_to_id]

    # Arrêt du thread existant si nécessaire
    if detection_thread and detection_thread.is_alive():
        with processing_lock:
            stop_detection = True
        detection_thread.join(timeout=1.0)

    # Nettoyage de la queue
    while not frame_queue.empty():
        try:
            frame_queue.get_nowait()
        except:
            pass

    # Suivi de l'état d'affichage du message de victoire
    victory_shown = [False]

    # Démarrage du thread de traitement
    detection_thread = threading.Thread(
        target=video_processing_thread,
        args=(video_source, on_object_detected, object_ids),
        daemon=True
    )
    detection_thread.start()

    # Fonction de mise à jour de l'interface
    def update_ui():
        if stop_detection or not canvas.winfo_exists():
            return

        try:
            if not frame_queue.empty():
                display_frame, fps, detected_count, total_detected = frame_queue.get_nowait()

                # Redimensionnement pour l'affichage
                pil_img = Image.fromarray(display_frame)
                img_width, img_height = pil_img.size
                canvas_width = canvas.winfo_width()
                canvas_height = canvas.winfo_height()

                if canvas_width > 1 and canvas_height > 1:
                    ratio = min(canvas_width/img_width, canvas_height/img_height)
                    new_width = int(img_width * ratio)
                    new_height = int(img_height * ratio)
                    pil_img = pil_img.resize((new_width, new_height), Image.LANCZOS)

                # Affichage dans le canvas
                tk_img = ImageTk.PhotoImage(pil_img)
                canvas.delete("all")
                canvas.create_image(
                    canvas_width//2 if canvas_width > 1 else 0,
                    canvas_height//2 if canvas_height > 1 else 0,
                    anchor=tk.CENTER,
                    image=tk_img
                )
                canvas.image = tk_img

                # Mise à jour des informations
                if fps_label and fps_label.winfo_exists():
                    fps_label.config(text=f"FPS: {fps:.2f}")

                if detection_label and detection_label.winfo_exists():
                    if objects_to_detect:
                        detection_label.config(text=f"Objets détectés: {total_detected}/{len(object_ids)}")
                    else:
                        detection_label.config(text=f"Objets détectés: {detected_count}")

                # Vérification de la victoire
                if object_ids and not victory_shown[0] and total_detected >= len(object_ids):
                    victory_shown[0] = True
                    with processing_lock:
                        detected_names = [model.names[obj_id] for obj_id in detected_objects_set if obj_id in model.names]
                    window.after(100, lambda: show_victory_message(window, detected_names))

            # Planification de la prochaine mise à jour
            if not stop_detection and window.winfo_exists():
                window.after(10, update_ui)

        except Exception as e:
            print(f"Erreur dans update_ui: {e}")
            if not stop_detection and window.winfo_exists():
                window.after(10, update_ui)

    # Démarrage de la mise à jour UI
    window.after(10, update_ui)

    # Gestion de la fermeture de fenêtre
    def on_window_close():
        global stop_detection
        with processing_lock:
            stop_detection = True
        window.destroy()

    window.protocol("WM_DELETE_WINDOW", on_window_close)

def stop_video():
    global stop_detection

    print("Arrêt du traitement vidéo demandé...")
    with processing_lock:
        stop_detection = True

    if detection_thread and detection_thread.is_alive():
        detection_thread.join(timeout=2.0)
        print("Thread de traitement vidéo arrêté")
