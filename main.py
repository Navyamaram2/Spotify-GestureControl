import cv2
import mediapipe as mp
import numpy as np
import spotipy
import pyttsx3
import csv
import threading
import tkinter as tk
from datetime import datetime
from spotipy.oauth2 import SpotifyOAuth
import spotipy.exceptions
import os
from dotenv import load_dotenv

# --- Load environment variables ---
load_dotenv()
CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')
SCOPE = "user-modify-playback-state user-read-playback-state user-read-currently-playing"

# --- Voice Setup ---
tts = pyttsx3.init()

def speak(text):
    threading.Thread(target=lambda: tts.say(text) or tts.runAndWait(), daemon=True).start()

# --- Spotify API Setup ---
sp_oauth = SpotifyOAuth(client_id=CLIENT_ID,
                        client_secret=CLIENT_SECRET,
                        redirect_uri=REDIRECT_URI,
                        scope=SCOPE,
                        open_browser=True)
sp = spotipy.Spotify(auth_manager=sp_oauth)

# --- MediaPipe setup ---
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.8, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# --- Helper Functions ---
def get_active_device_id():
    devices = sp.devices()
    if devices and devices['devices']:
        return devices['devices'][0]['id']
    return None

def change_song(direction):
    threading.Thread(target=_change_song, args=(direction,), daemon=True).start()

def _change_song(direction):
    device_id = get_active_device_id()
    if not device_id:
        return
    try:
        if direction == 'left':
            sp.previous_track(device_id=device_id)
            speak("Previous track")
            log_action("Previous track")
        elif direction == 'right':
            sp.next_track(device_id=device_id)
            speak("Next track")
            log_action("Next track")
    except spotipy.exceptions.SpotifyException as e:
        print("❌ Failed to change song:", e)

def adjust_volume(up):
    threading.Thread(target=_adjust_volume, args=(up,), daemon=True).start()

def _adjust_volume(up):
    device_id = get_active_device_id()
    if not device_id:
        return
    try:
        current_volume = sp.devices()['devices'][0]['volume_percent']
        new_volume = max(0, min(100, current_volume + (10 if up else -10)))
        sp.volume(new_volume, device_id=device_id)
        speak(f"Volume {new_volume}")
        log_action(f"Volume {'Up' if up else 'Down'} to {new_volume}")
    except spotipy.exceptions.SpotifyException as e:
        print("❌ Failed to adjust volume:", e)

def get_current_track_name():
    try:
        current = sp.current_user_playing_track()
        if current and current.get('item'):
            name = current['item']['name']
            artist = current['item']['artists'][0]['name']
            return f"{name} - {artist}"
    except:
        return "No track playing"
    return "No track playing"

def count_fingers(hand_landmarks):
    tip_ids = [4, 8, 12, 16, 20]
    fingers = []
    for i in range(1, 5):
        if hand_landmarks.landmark[tip_ids[i]].y < hand_landmarks.landmark[tip_ids[i] - 2].y:
            fingers.append(1)
        else:
            fingers.append(0)
    return sum(fingers)

def detect_thumbs_up(hand_landmarks):
    thumb_tip = hand_landmarks.landmark[4]
    index_mcp = hand_landmarks.landmark[5]
    return thumb_tip.y < index_mcp.y

def log_action(action):
    with open("gesture_log.csv", mode='a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now(), action])

# --- GUI Buttons ---
def create_gui():
    def play():
        threading.Thread(target=lambda: sp.start_playback(device_id=get_active_device_id()), daemon=True).start()
        log_action("Play (GUI)")

    def pause():
        threading.Thread(target=lambda: sp.pause_playback(device_id=get_active_device_id()), daemon=True).start()
        log_action("Pause (GUI)")

    def next_song():
        change_song('right')

    def prev_song():
        change_song('left')

    window = tk.Tk()
    window.title("Spotify Control Panel")

    tk.Button(window, text="▶️ Play", command=play, width=20).pack(pady=5)
    tk.Button(window, text="⏸ Pause", command=pause, width=20).pack(pady=5)
    tk.Button(window, text="⏭ Next", command=next_song, width=20).pack(pady=5)
    tk.Button(window, text="⏮ Previous", command=prev_song, width=20).pack(pady=5)

    window.mainloop()

threading.Thread(target=create_gui, daemon=True).start()

# --- Main Loop ---
gesture_cooldown = 0
prev_center = None
muted = False
frame_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1
    if frame_count % 2 != 0:
        continue

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)
    h, w, _ = frame.shape

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            wrist = hand_landmarks.landmark[0]
            center = np.array([wrist.x * w, wrist.y * h])

            if prev_center is not None and gesture_cooldown == 0:
                dx = center[0] - prev_center[0]
                dy = center[1] - prev_center[1]

                if abs(dx) > 80:
                    change_song('right' if dx > 0 else 'left')
                    gesture_cooldown = 20

                elif abs(dy) > 80:
                    adjust_volume(dy < 0)
                    gesture_cooldown = 20

            fingers = count_fingers(hand_landmarks)
            device_id = get_active_device_id()

            if fingers == 0 and gesture_cooldown == 0 and device_id:
                threading.Thread(target=lambda: sp.pause_playback(device_id=device_id), daemon=True).start()
                speak("Paused")
                log_action("Paused")
                gesture_cooldown = 20
            elif fingers == 5 and gesture_cooldown == 0 and device_id:
                threading.Thread(target=lambda: sp.start_playback(device_id=device_id), daemon=True).start()
                speak("Playing")
                log_action("Playing")
                gesture_cooldown = 20
            elif fingers == 2 and gesture_cooldown == 0:
                threading.Thread(target=lambda: sp.shuffle(state=True), daemon=True).start()
                speak("Shuffle on")
                log_action("Shuffle on")
                gesture_cooldown = 20
            elif fingers == 3 and gesture_cooldown == 0:
                threading.Thread(target=lambda: sp.repeat('track'), daemon=True).start()
                speak("Repeat on")
                log_action("Repeat on")
                gesture_cooldown = 20
            elif fingers == 4 and gesture_cooldown == 0:
                def toggle_mute():
                    global muted
                    device = get_active_device_id()
                    if not device:
                        return
                    if not muted:
                        sp.volume(0, device_id=device)
                        muted = True
                        speak("Muted")
                        log_action("Muted")
                    else:
                        sp.volume(50, device_id=device)
                        muted = False
                        speak("Unmuted")
                        log_action("Unmuted")
                threading.Thread(target=toggle_mute, daemon=True).start()
                gesture_cooldown = 20

            if detect_thumbs_up(hand_landmarks) and gesture_cooldown == 0:
                speak("Liked")
                log_action("Liked")
                cv2.putText(frame, '👍 Liked', (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,0), 2)
                gesture_cooldown = 20

            prev_center = center

    if gesture_cooldown > 0:
        gesture_cooldown -= 1

    current_track = get_current_track_name()
    cv2.putText(frame, f'Playing: {current_track}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

    cv2.imshow("Spotify Music Control", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
