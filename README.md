# Driver Drowsiness Detection System

A real-time driver drowsiness detection system built with Python, OpenCV, MediaPipe, Django, and Django REST Framework. The application monitors a driver's eye activity through a webcam, calculates the Eye Aspect Ratio (EAR), triggers an audible alert when drowsiness is detected, and records detection events in a web dashboard.

## Project Links

- Repository: https://github.com/niteshkumar9368/Driver-drawsiness-detection-system
- Deployment URL: https://driver-drowsiness-detection-system.onrender.com

## Features

- Real-time webcam-based face and eye landmark detection
- Eye Aspect Ratio (EAR) calculation for drowsiness detection
- Audible warning alert when drowsiness persists for multiple frames
- Django dashboard with live camera feed
- REST API for saving and retrieving detection logs
- Daily drowsiness alert count
- Log table with timestamp, status, and EAR value
- Drowsiness trend chart using Chart.js

## Tech Stack

- Python
- OpenCV
- MediaPipe
- Django
- Django REST Framework
- SQLite
- Chart.js

## Project Structure

```text
Driver-drawsiness-detection-system/
|-- drowsiness_backend/      # Django project configuration
|-- monitor/                 # Django app for dashboard, API, and logs
|   |-- migrations/
|   |-- templates/
|   |   `-- monitor/
|   |       `-- dashboard.html
|   |-- models.py
|   |-- serializers.py
|   |-- urls.py
|   `-- views.py
|-- main.py                  # Standalone OpenCV drowsiness detector
|-- manage.py
|-- requirements.txt
`-- README.md
```

## How It Works

The system uses MediaPipe Face Mesh to detect facial landmarks from the webcam stream. Eye landmarks are used to calculate the Eye Aspect Ratio (EAR). If the EAR remains below the configured threshold for a set number of frames, the driver is marked as drowsy and an alarm is played.

Detection status and EAR values are sent to the Django REST API, where they are stored in the database. The dashboard displays the live video feed, current status, recent logs, total drowsy alerts for the day, and an EAR trend graph.

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/niteshkumar9368/Driver-drawsiness-detection-system.git
cd Driver-drawsiness-detection-system
```

### 2. Create and Activate a Virtual Environment

```bash
python -m venv .venv
```

On Windows:

```bash
.venv\Scripts\activate
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply Database Migrations

```bash
python manage.py migrate
```

## Usage

### Run the Django Dashboard

```bash
python manage.py runserver
```

Open the dashboard in your browser:

```text
http://127.0.0.1:8000/
```

The dashboard includes:

- Live camera feed
- Current driver status
- Last detection time
- Total drowsy alerts for the current day
- EAR trend graph
- Detection logs table

### Run the Standalone Detector

```bash
python main.py
```

Press `q` in the camera window to stop the detector.

## Deployment

This repository includes Render deployment configuration:

- `render.yaml` defines the Django web service and PostgreSQL database.
- `build.sh` installs production dependencies, collects static files, and runs migrations.
- `requirements-render.txt` uses the headless OpenCV package for Linux hosting.
- `runtime.txt` pins the Python version used by Render.

To deploy:

1. Push the latest code to GitHub.
2. Open Render and create a new Blueprint.
3. Select this repository.
4. Apply the blueprint and wait for the build to complete.

The hosted app will run the Django dashboard and API. Real webcam detection still needs to run on a local machine because cloud servers cannot access a user's physical webcam directly.

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/api/log/` | Save a drowsiness detection log |
| `GET` | `/api/logs/` | Retrieve today's detection logs and drowsy count |
| `GET` | `/video_feed/` | Stream live camera frames to the dashboard |

Example log payload:

```json
{
  "status": "Drowsy",
  "ear_value": 0.18
}
```

## Configuration

Key detection values are defined in `main.py` and `monitor/views.py`:

```python
EYE_AR_THRESH = 0.22
DROWSY_FRAMES = 30
ALARM_FREQUENCY = 2500
ALARM_DURATION_MS = 700
```

You can adjust these values based on lighting conditions, camera quality, and detection sensitivity requirements.

## Requirements and Notes

- A working webcam is required.
- The audible alarm uses the Windows `winsound` module, so alarm playback is designed for Windows.
- The project uses SQLite by default for local development.
- `db.sqlite3`, virtual environments, and Python cache files are intentionally ignored by Git.
- For production deployment, move sensitive Django settings such as `SECRET_KEY`, `DEBUG`, and `ALLOWED_HOSTS` to environment variables.

## License

This project is intended for educational and demonstration purposes.
