import cv2
import os, sys
import json
from collections import deque, Counter
from gaze import estimate_gaze_direction
import mediapipe as mp

MODULE_FULL_NAME = "WEBCAM/GAZE_DETECTION"

### To import UDPCLient ###
def get_modules_folder_dir():
    current_dir = os.path.abspath(os.path.dirname(__file__))
    
    while not os.path.exists(os.path.join(current_dir, 'Modules')):
        current_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
        if current_dir == os.path.abspath(os.sep):
            print("Le dossier 'Modules' n'a pas été trouvé.")
            sys.exit(1)
    
    return os.path.join(current_dir, 'Modules')
    
modules_folder_dir = get_modules_folder_dir()
sys.path.append(modules_folder_dir)
from UDPClient import UDPClient

### To have the whiteboard ip ###
ip_witeboard_file = os.path.join(modules_folder_dir, 'IP_whiteboard.txt')
with open(ip_witeboard_file, 'r') as txt_file:
    ip_whiteboard = txt_file.read()
    
# Setup UDP Client
udp_client = UDPClient(ip_whiteboard)

BUFFER_SECONDS = 2
FPS_ESTIMATE = 10
THRESHOLD_RATIO = 0.8

# === Sliding window buffer ===
buffer_size = BUFFER_SECONDS * FPS_ESTIMATE
gaze_buffer = deque(maxlen=buffer_size)
last_stable_direction = None

def is_stable(buffer, threshold_ratio=THRESHOLD_RATIO):
    if not buffer:
        return False, None
    count = Counter(buffer)
    most_common, freq = count.most_common(1)[0]
    if freq / len(buffer) >= threshold_ratio:
        return True, most_common
    return False, most_common

def send_gaze_update(direction):
    payload = json.dumps({"gaze": direction})
    udp_client.send(f"USER_CONTEXT_PERCEPTION:{payload}")
    print(f"[Gaze UDP] Sent: USER_CONTEXT_PERCEPTION:{payload}")

# === MediaPipe init ===
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)
cap = cv2.VideoCapture(0)

udp_client.send(f'COMMON:MODULE_SUCCESSFULLY_ACTIVATED:{MODULE_FULL_NAME}')

# === MAIN LOOP ===
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    img_h, img_w = frame.shape[:2]
    small = cv2.resize(frame, (0, 0), fx=0.75, fy=0.75)
    rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    direction = estimate_gaze_direction(results, img_h, img_w)

    if direction not in ["NO FACE", "PnP Fail"]:
        gaze_buffer.append(direction)

        stable, current = is_stable(gaze_buffer)
        if stable and current != last_stable_direction:
            send_gaze_update(current)
            last_stable_direction = current

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
udp_client.close()
