# Text to Speech Web Application

A web application that converts text to speech using the Kokoro TTS model.

## Project Structure

```
src/
├── backend/
│   ├── __init__.py
│   ├── app.py
│   └── tts_service.py
└── frontend/
    ├── index.html
    ├── styles.css
    └── script.js
```

## Setup

1. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. Start the backend server:
```bash
cd src/backend
python app.py
```

4. Open the frontend:
- Navigate to `src/frontend`
- Open `index.html` in your web browser
- Or use a local server to serve the frontend files

## Usage

1. Enter the text you want to convert to speech in the text area
2. Click the "Convert to Speech" button
3. The audio will be generated and played automatically
4. You can use the audio player controls to play/pause/seek the audio

## Features

- Text to speech conversion using Kokoro TTS model
- Modern and responsive web interface
- Real-time audio playback
- Error handling and user feedback 