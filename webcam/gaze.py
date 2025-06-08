import os
import cv2
import numpy as np
import mediapipe as mp
import warnings
import logging
import tensorflow as tf

# ========== [Silenzia output] ==========
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
warnings.filterwarnings("ignore")
tf.get_logger().setLevel('ERROR')
logging.getLogger('absl').setLevel(logging.ERROR)

# ========== [Costanti] ==========
FACE_LANDMARKS = [1, 159, 386, 78, 95, 88, 178, 87, 14, 317, 402, 318, 324, 308,
                  191, 80, 81, 82, 13, 312, 311, 310, 415, 474, 475, 476, 477,
                  469, 470, 471, 472, 33, 133, 362, 61, 199, 263, 291]
GAZE_POSE_INDICES = [1, 33, 61, 199, 263, 291]
CONFIDENCE = 0.5
FRAME_SKIP = 2           # Elabora 1 frame ogni N
DRAW_ENABLED = True      # Disegna i punti del volto

# ========== [Inizializza FaceMesh] ==========
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True,
                                  min_detection_confidence=CONFIDENCE,
                                  min_tracking_confidence=CONFIDENCE)

# ========== [Gaze Detection] ==========
def estimate_gaze_direction(face_results, img_h, img_w):
    if not face_results or not face_results.multi_face_landmarks:
        return "NO FACE"

    landmarks_3d = np.array([[lm.x, lm.y, lm.z] for lm in face_results.multi_face_landmarks[0].landmark])
    landmarks_2d = np.array([[lm.x * img_w, lm.y * img_h] for lm in face_results.multi_face_landmarks[0].landmark])

    points_3d = np.multiply(landmarks_3d[GAZE_POSE_INDICES], [img_w, img_h, 1]).astype(np.float64)
    points_2d = landmarks_2d[GAZE_POSE_INDICES].astype(np.float64)

    cam_matrix = np.array([[img_w, 0, img_h / 2], [0, img_w, img_w / 2], [0, 0, 1]])
    dist_coeffs = np.zeros((4, 1), dtype=np.float64)

    success, rvec, tvec = cv2.solvePnP(points_3d, points_2d, cam_matrix, dist_coeffs)
    if not success:
        return "PnP Fail"

    rot_mat, _ = cv2.Rodrigues(rvec)
    angles, *_ = cv2.RQDecomp3x3(rot_mat)

    angle_x, angle_y = angles[0] * 360, angles[1] * 360
    return classify_gaze_direction(angle_x, angle_y)

def classify_gaze_direction(angle_x, angle_y, threshold=10, down_thresh=5):
    if angle_y < -threshold:
        return "Right"
    elif angle_y > threshold:
        return "Left"
    elif angle_x < -down_thresh:
        return "Down"
    elif angle_x > threshold:
        return "Up"
    return "Forward"

# ========== [Disegna punti facciali] ==========
def draw_face_landmarks(frame, face_results):
    if not DRAW_ENABLED or not face_results or not face_results.multi_face_landmarks:
        return
    h, w = frame.shape[:2]
    for idx in FACE_LANDMARKS:
        lm = face_results.multi_face_landmarks[0].landmark[idx]
        cv2.circle(frame, (int(lm.x * w), int(lm.y * h)), 2, (0, 255, 0), -1)

# ========== [Testo con sfondo evidenziato] ==========
def draw_text_with_background(frame, text, pos, font=cv2.FONT_HERSHEY_SIMPLEX,
                              font_scale=0.8, text_color=(0, 255, 0),
                              bg_color=(0, 0, 0), thickness=2, pad=5):
    x, y = pos
    (text_w, text_h), baseline = cv2.getTextSize(text, font, font_scale, thickness)
    top_left = (x - pad, y - text_h - pad)
    bottom_right = (x + text_w + pad, y + baseline + pad)
    cv2.rectangle(frame, top_left, bottom_right, bg_color, -1)
    cv2.putText(frame, text, (x, y), font, font_scale, text_color, thickness)

# ========== [Loop Principale] ==========
def run_gaze_detection():
    cap = cv2.VideoCapture(0)
    frame_count = 0
    last_direction = "..."
    last_face_results = None

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        img_h, img_w = frame.shape[:2]

        small_frame = cv2.resize(frame, (0, 0), fx=0.75, fy=0.75)
        small_rgb = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # Gaze detection ogni N frame
        if frame_count % FRAME_SKIP == 0:
            face_results = face_mesh.process(small_rgb)
            direction = estimate_gaze_direction(face_results, img_h, img_w) if face_results else last_direction
            if direction not in ["NO FACE", "PnP Fail"]:
                last_direction = direction
            if face_results and face_results.multi_face_landmarks:
                last_face_results = face_results
        else:
            face_results = None

        # Disegni e overlay
        draw_face_landmarks(frame, last_face_results)
        draw_text_with_background(frame, f"Gaze: {last_direction}", (50, 50),
                                  font_scale=1.0, text_color=(0, 255, 0), bg_color=(0, 0, 0))

        cv2.imshow("Gaze Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# ========== [Avvio] ==========
if __name__ == "__main__":
    run_gaze_detection()
