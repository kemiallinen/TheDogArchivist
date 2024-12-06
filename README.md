# 🐶 The Dog Archivist
**The Dog Archivist** is a Raspberry Pi-based system designed to detect, track, and archive information about dogs (and their owners) passing in front of a camera. The project uses **YOLOv5** for object detection, **OpenCV** for tracking, and stores data locally in an **SQLite** database, with images neatly organized in a file system.

---
## 📑 Features
- **Real-Time Detection:** Detect dogs and people using YOLOv5.
- **Object Tracking:** Track detected objects in real-time using OpenCV trackers.
- **Unique Identification:** Assign unique IDs to each detected object.
- **Image Archiving:** Save unique images of dogs and their owners in structured directories.
- **Logging:** Record key events in structured log files.
- **Configurable:** Manage project settings through a JSON configuration file.

---
## 🛠️ Requirements
### Hardware
- Raspberry Pi 4 Model B (or newer)
- Raspberry Pi Camera (e.g., Camera Module 3)
### Software
- Python 3.11
- YOLOv5
- OpenCV 4.9.0 or higher
- Flask (for video streaming)
- SQLite (for local database storage)

---
## 🚀 Installation
1. **Set up Raspberry Pi:**
- Enable the camera in Raspberry Pi settings (`sudo raspi-config`).
- Install required system libraries:
```
sudo apt update
sudo apt install python3-pip libopencv-dev
```
2. **Clone the repository:**

```
git clone https://github.com/kemiallinen/TheDogArchivist.git
cd TheDogArchivist
```
3. **Set up a virtual environment:**
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
4. Run the application:
```
python main.py
```

---
## 🗂️ Project Structure
```
TheDogArchivist/
├── app/
│   ├── base/              # Core modules (e.g., BBox, Tracker, Category)
│   ├── config/            # Configuration management
│   ├── camera.py          # PiCamera handler
|   ├── database.py        # Database management
│   ├── io.py              # Image saving and database interaction
│   ├── logger.py          # Logging setup
│   └── routes.py          # Flask routes and main application logic
├── tests/                 # Unit tests for the project
├── static/                # Static files (e.g., YOLOv5 models)
├── requirements.txt       # Python dependencies
├── main.py                # Entry point for the application
└── README.md              # Project documentation
```

---
## 💡 How It Works
1. The system continuously captures video frames using the Raspberry Pi camera.
2. Every N frames (configurable), YOLOv5 detects objects (dogs and people) in the frame.
3. Detected objects are assigned unique IDs and tracked in real-time using OpenCV trackers.
4. The system archives images of new objects, saving them in directories based on their category (e.g., dogs or owners).
5. Key events and updates are logged for debugging and monitoring purposes.

---
## 🧪 Testing
Run unit tests to ensure the application is working correctly:
```
pytest tests/
```

---
## 📖 Configuration
The system uses a JSON file (config/config.json) to manage settings like:

- Path to the YOLOv5 model.
- IoU threshold for filtering duplicate detections.
- Max time gap for inactive trackers.

Example config.json:

```
{
  "detection": {
    "model_path": "static/models/yolov5n.pt",
    "iou_threshold": 0.5
  },
  "tracker": {
    "max_time_gap": 30
  },
  "logging": {
    "level": "DEBUG",
    "log_dir": "logs"
  }
}
```

---
## 🛠️ Future Enhancements
- Add support for remote database storage (e.g., Firebase or PostgreSQL).
- Implement more advanced tracking algorithms (e.g., SORT or DeepSORT).
- Extend functionality to detect additional objects or behaviors.
- Create a web interface for browsing archived images and logs.

---
## 🤝 Contributing
Contributions are welcome! Feel free to open issues or submit pull requests to improve the project.

---
## 📜 License
This project is licensed under the MIT License. See LICENSE for more details.