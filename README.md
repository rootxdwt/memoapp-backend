# Audio Transcription API

A Flask API that transcribes audio files to text using [parakeet-mlx](https://github.com/senstella/parakeet-mlx), an MLX-optimized speech recognition model.

## Features

- Audio file transcription to text
- Multiple audio format support (WAV, MP3, MP4, M4A, FLAC, OGG, AAC, WebM)
- CORS enabled for frontend integration

## Prerequisites

- Python 3.8+
- macOS with Apple Silicon (for MLX support)
- ffmpeg installed on your system

### Install ffmpeg

```bash
brew install ffmpeg
```

## Installation

1. Install dependencies:

```bash
pip install -r requirements.txt
```

Or using uv (recommended):

```bash
uv pip install -r requirements.txt
```

2. The parakeet-mlx model will be downloaded automatically on first run.

## Usage

### Start the Server

```bash
python app.py
```

The API will be available at `http://localhost:5001`

### API Endpoints

#### Transcribe Audio

```bash
POST /transcribe
```

Parameters:
- `audio` (file, required): Audio file to transcribe

Example using curl:

```bash
# Basic transcription
curl -X POST http://localhost:5001/transcribe \
  -F "audio=@path/to/your/audio.wav"
```

Response (with timestamps):
```json
[
    {
      "text": "This is the transcribed text from your audio file.",
      "start": 0.0,
      "end": 3.5
    }
]
```

## Supported Audio Formats

- WAV
- MP3
- MP4
- M4A
- FLAC
- OGG
- AAC
- WebM

## Configuration

You can modify these settings in [app.py](app.py):

- `MAX_FILE_SIZE`: Maximum upload file size (default: 100MB)
- `ALLOWED_EXTENSIONS`: Allowed audio file extensions
- Model: Change the model in the `from_pretrained()` call

## Performance Notes

- The model loads once at startup, so first request after starting the server may take a moment
- Transcription speed depends on audio length and your hardware
- MLX is optimized for Apple Silicon (M1/M2/M3 chips)

## License

This project uses parakeet-mlx which is licensed under Apache 2.0.
