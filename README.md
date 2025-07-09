# 🎵 Spotify Gesture Control with MediaPipe

Control Spotify playback using hand gestures via webcam with real-time GUI and voice feedback.

---

## ✨ Features

- 🎮 Play/Pause with hand  
- ⏭️ Swipe to skip songs  
- 🔊 Volume control by hand movement  
- 🔀 Shuffle, 🔁 repeat, 🔇 mute, 👍 like with finger gestures  
- 🖱️ GUI buttons for manual control  
- 🗣️ Voice feedback using `pyttsx3`  

---

## 📸 Gestures

| Gesture              | Action             |
|----------------------|--------------------|
| ✊ Fist               | Pause              |
| ✋ Open hand          | Play               |
| ✌️ Two fingers        | Shuffle            |
| 🤟 Three fingers      | Repeat             |
| 🖖 Four fingers       | Mute toggle        |
| 👍 Thumbs up          | Like track         |
| ↔️ Swipe Left/Right   | Previous/Next song |
| ↕️ Move Up/Down       | Volume control     |

---

## 🚀 Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/spotify-gesture-control.git
cd spotify-gesture-control
```

### 2. Install Requirements

```bash
pip install -r requirements.txt
```

### 3. Create a `.env` File

Add your Spotify credentials in a `.env` file:

```ini
SPOTIPY_CLIENT_ID=your_client_id
SPOTIPY_CLIENT_SECRET=your_secret
SPOTIPY_REDIRECT_URI=http://127.0.0.1:8000/callback
```

> ⚠️ Make sure to replace `your_client_id` and `your_secret` with your actual Spotify Developer credentials.

### 4. Run the App

```bash
python main.py
```

---

## 📋 Notes

- You must have a **Spotify Premium** account.  
- **Webcam access** is required to use gesture controls.  
- Make sure your environment supports GUI for tkinter.  

---

## 📂 Logs

All gesture actions are saved in a file:

```
gesture_log.csv
```

This log contains timestamps and recognized gesture actions.

---

## 🛠️ Tech Stack

- Python  
- OpenCV  
- MediaPipe  
- Spotipy  
- pyttsx3  
- Tkinter  

---

## 🙌 Contributions

Feel free to fork and contribute! Pull requests are welcome.

---

## 📜 License

This project is licensed under the MIT License.
