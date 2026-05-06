import cv2
import face_recognition
import os
from config import FACE_MATCH_THRESHOLD

camera = None
known_encodings = []
known_names = []


def load_known_faces():
    global known_encodings, known_names

    path = "known_faces"

    for file in os.listdir(path):
        file_path = os.path.join(path, file)

        try:
            # load image
            img = face_recognition.load_image_file(file_path)

            # get face encodings
            enc = face_recognition.face_encodings(img)

            if enc:
                known_encodings.append(enc[0])
                known_names.append(file.split('.')[0])
                print("Loaded:", file)
            else:
                print("No face found in:", file)

        except Exception as e:
            print("Skipping bad image:", file)


def start_camera():
    global camera
    if camera is None:
        camera = cv2.VideoCapture(0)


def process_frame():
    global camera

    success, frame = camera.read()
    if not success:
        return None, "❌ Camera Error", False

    # convert BGR to RGB
    rgb = frame[:, :, ::-1]

    # detect faces
    faces = face_recognition.face_locations(rgb)
    encodings = face_recognition.face_encodings(rgb, faces)

    unknown_detected = False
    names = []

    for encoding in encodings:
        matches = face_recognition.compare_faces(
            known_encodings, encoding, FACE_MATCH_THRESHOLD
        )

        name = "Unknown"

        if True in matches:
            idx = matches.index(True)
            name = known_names[idx]
        else:
            unknown_detected = True

        names.append(name)

    # draw boxes
    for (top, right, bottom, left), name in zip(faces, names):
        color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)

        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.putText(
            frame,
            name,
            (left, top - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            color,
            2,
        )

    count = len(faces)

    if count == 0:
        status = "✅ No Person"
    elif unknown_detected:
        status = "🚨 UNKNOWN PERSON DETECTED"
    else:
        status = f"👤 {count} Known Person(s)"

    _, buffer = cv2.imencode(".jpg", frame)

    return buffer.tobytes(), status, unknown_detected
