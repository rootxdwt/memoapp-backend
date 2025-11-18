# Audio Transcription API

A Flask API that transcribes audio files to text using [parakeet-mlx](https://github.com/senstella/parakeet-mlx), an MLX-optimized speech recognition model.

## Features

- Audio file transcription to text
- Multiple audio format support (WAV, MP3, MP4, M4A, FLAC, OGG, AAC, WebM)
- Optional sentence-level timestamps
- CORS enabled for frontend integration
- Health check endpoint

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

The API will be available at `http://localhost:5000`

### API Endpoints

#### Health Check

```bash
GET /health
```

Response:
```json
{
  "status": "healthy",
  "model": "mlx-community/parakeet-tdt-0.6b-v3"
}
```

#### Transcribe Audio

```bash
POST /transcribe
```

Parameters:
- `audio` (file, required): Audio file to transcribe
- `include_timestamps` (form field, optional): Set to "true" to include sentence-level timestamps

Example using curl:

```bash
# Basic transcription
curl -X POST http://localhost:5000/transcribe \
  -F "audio=@path/to/your/audio.wav"

# With timestamps
curl -X POST http://localhost:5000/transcribe \
  -F "audio=@path/to/your/audio.wav" \
  -F "include_timestamps=true"
```

Response (without timestamps):
```json
{
  "text": "This is the transcribed text from your audio file.",
  "success": true
}
```

Response (with timestamps):
```json
{
  "text": "This is the transcribed text from your audio file.",
  "success": true,
  "sentences": [
    {
      "text": "This is the transcribed text from your audio file.",
      "start": 0.0,
      "end": 3.5
    }
  ]
}
```

#### Transcribe Audio (Streaming)

```bash
POST /transcribe/stream
```

This endpoint uses Server-Sent Events (SSE) to stream transcription results in real-time as the audio is being processed.

Parameters:
- `audio` (file, required): Audio file to transcribe

Example using curl:

```bash
curl -X POST http://localhost:5000/transcribe/stream \
  -F "audio=@path/to/your/audio.wav" \
  -N
```

Response (Server-Sent Events stream):
```
data: {"text": "First chunk of transcribed text", "is_final": false, "sentences": [...]}

data: {"text": "Second chunk of transcribed text", "is_final": false, "sentences": [...]}

data: {"text": "", "is_final": true, "success": true}
```

### Example with Python requests

```python
import requests
import json

# Basic transcription
with open('audio.wav', 'rb') as f:
    files = {'audio': f}
    data = {'include_timestamps': 'true'}
    response = requests.post('http://localhost:5000/transcribe',
                            files=files,
                            data=data)

print(response.json())

# Streaming transcription
with open('audio.wav', 'rb') as f:
    files = {'audio': f}
    response = requests.post('http://localhost:5000/transcribe/stream',
                            files=files,
                            stream=True)

    for line in response.iter_lines():
        if line:
            # Remove 'data: ' prefix and parse JSON
            data = json.loads(line.decode('utf-8').replace('data: ', ''))
            if not data.get('is_final'):
                print(f"Partial: {data['text']}")
            else:
                if data.get('success'):
                    print("Transcription complete!")
                else:
                    print(f"Error: {data.get('error')}")
```

### Example with JavaScript/Fetch

```javascript
// Basic transcription
const formData = new FormData();
formData.append('audio', audioFile);
formData.append('include_timestamps', 'true');

const response = await fetch('http://localhost:5000/transcribe', {
  method: 'POST',
  body: formData
});

const result = await response.json();
console.log(result.text);

// Streaming transcription
const streamFormData = new FormData();
streamFormData.append('audio', audioFile);

const streamResponse = await fetch('http://localhost:5000/transcribe/stream', {
  method: 'POST',
  body: streamFormData
});

const reader = streamResponse.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;

  const chunk = decoder.decode(value);
  const lines = chunk.split('\n');

  for (const line of lines) {
    if (line.startsWith('data: ')) {
      const data = JSON.parse(line.slice(6));
      if (!data.is_final) {
        console.log('Partial:', data.text);
      } else if (data.success) {
        console.log('Transcription complete!');
      } else {
        console.error('Error:', data.error);
      }
    }
  }
}
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

## Error Handling

The API returns appropriate HTTP status codes:

- `200`: Success
- `400`: Bad request (invalid file or missing parameters)
- `500`: Server error (transcription failed)
- `501`: Not implemented (streaming endpoint)

## Performance Notes

- The model loads once at startup, so first request after starting the server may take a moment
- Transcription speed depends on audio length and your hardware
- MLX is optimized for Apple Silicon (M1/M2/M3 chips)

## License

This project uses parakeet-mlx which is licensed under Apache 2.0.
