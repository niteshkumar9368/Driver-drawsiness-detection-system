import math
import queue
import threading
import time
import winsound

import cv2
import mediapipe as mp
import requests


EYE_AR_THRESH = 0.22
DROWSY_FRAMES = 30
ALARM_FREQUENCY = 2500
ALARM_DURATION_MS = 700
API_LOG_URL = "http://127.0.0.1:8000/api/log/"
API_TIMEOUT_SECONDS = 0.5

LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]

COUNTER = 0
alarm_on = False
previous_status = "Awake"
last_sent_status = None
log_queue = queue.Queue(maxsize=1)
stop_logging = threading.Event()
stop_alarm = threading.Event()


def distance(point_a, point_b):
    return math.hypot(point_a[0] - point_b[0], point_a[1] - point_b[1])


def eye_aspect_ratio(landmarks, eye_indices):
    p1, p2, p3, p4, p5, p6 = [landmarks[index] for index in eye_indices]

    vertical_1 = distance(p2, p6)
    vertical_2 = distance(p3, p5)
    horizontal = distance(p1, p4)

    if horizontal == 0:
        return 0.0

    return (vertical_1 + vertical_2) / (2.0 * horizontal)


def draw_eye_landmarks(frame, landmarks, eye_indices):
    for index in eye_indices:
        cv2.circle(frame, landmarks[index], 2, (0, 255, 0), -1)


def beep_loop():
    while not stop_alarm.is_set():
        winsound.Beep(ALARM_FREQUENCY, ALARM_DURATION_MS)
        time.sleep(0.1)


def start_beep_loop():
    stop_alarm.clear()
    threading.Thread(target=beep_loop, daemon=True).start()


def stop_beep_loop():
    stop_alarm.set()


def print_debug_log(ear_value, counter, status):
    print(f"EAR: {ear_value:.3f} | COUNTER: {counter} | Status: {status}")


def api_log_worker():
    while not stop_logging.is_set():
        try:
            status, ear_value = log_queue.get(timeout=0.2)
        except queue.Empty:
            continue

        try:
            requests.post(
                API_LOG_URL,
                json={"status": status, "ear_value": ear_value},
                timeout=API_TIMEOUT_SECONDS,
            )
        except requests.RequestException:
            # Keep the camera loop smooth even if the Django server is off.
            pass
        finally:
            log_queue.task_done()


def send_status_to_api(status, ear_value):
    global last_sent_status

    if status == last_sent_status:
        return

    last_sent_status = status
    payload = (status, float(ear_value))

    if log_queue.full():
        try:
            log_queue.get_nowait()
            log_queue.task_done()
        except queue.Empty:
            pass

    log_queue.put_nowait(payload)


threading.Thread(target=api_log_worker, daemon=True).start()

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
)

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Cannot access webcam")
    exit()

while True:
    status = previous_status
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    frame = cv2.flip(frame, 1)
    height, width = frame.shape[:2]
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    rgb_frame.flags.writeable = False
    result = face_mesh.process(rgb_frame)

    ear = 0.0
    face_detected = False

    if result.multi_face_landmarks:
        face_detected = True
        face_landmarks = result.multi_face_landmarks[0]
        landmarks = [
            (int(point.x * width), int(point.y * height))
            for point in face_landmarks.landmark
        ]

        left_ear = eye_aspect_ratio(landmarks, LEFT_EYE)
        right_ear = eye_aspect_ratio(landmarks, RIGHT_EYE)
        ear = (left_ear + right_ear) / 2.0

        draw_eye_landmarks(frame, landmarks, LEFT_EYE)
        draw_eye_landmarks(frame, landmarks, RIGHT_EYE)

    if face_detected and ear < EYE_AR_THRESH:
        COUNTER += 1

        if COUNTER >= DROWSY_FRAMES:
            status = "Drowsy"

            if not alarm_on:
                start_beep_loop()
                alarm_on = True
    else:
        COUNTER = 0
        status = "Awake"

        if alarm_on:
            stop_beep_loop()
            alarm_on = False

    cv2.putText(
        frame,
        f"EAR: {ear:.2f}",
        (30, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2,
    )
    cv2.putText(
        frame,
        f"COUNTER: {COUNTER}",
        (30, 75),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2,
    )
    cv2.putText(
        frame,
        f"Status: {status}",
        (30, 110),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0) if status == "Awake" else (0, 0, 255),
        2,
    )

    if status == "Drowsy":
        cv2.putText(
            frame,
            "DROWSY ALERT!",
            (30, 155),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            3,
        )

    print_debug_log(ear, COUNTER, status)
    send_status_to_api(status, ear)
    previous_status = status

    cv2.imshow("Drowsiness Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

stop_beep_loop()
stop_logging.set()
cap.release()
face_mesh.close()
cv2.destroyAllWindows()
