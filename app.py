from flask import Flask, request, jsonify
from flask_cors import CORS
from parakeet_mlx import from_pretrained,DecodingConfig,SentenceConfig
import os
import tempfile

app = Flask(__name__)
CORS(app)

# Configure upload settings
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'mp4', 'm4a', 'flac', 'ogg', 'aac', 'webm'}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

# Initialize the model (load once at startup)
model = from_pretrained("mlx-community/parakeet-tdt-0.6b-v3")


config = DecodingConfig(
    sentence = SentenceConfig(
       silence_gap=0.2
    )
)

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    """
    Transcribe audio file to text.

    Expects:
        - 'audio' file in multipart/form-data
        - Optional 'include_timestamps' boolean parameter

    Returns:
        - JSON with transcription text and optional sentence-level timestamps
    """
    # Check if audio file is present
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio']

    # Check if file is selected
    if audio_file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    # Validate file type
    if not allowed_file(audio_file.filename):
        return jsonify({
            'error': f'Invalid file type. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'
        }), 400

    try:
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio_file.filename)[1]) as temp_file:
            audio_file.save(temp_file.name)
            temp_path = temp_file.name

        # Transcribe the audio
        result = model.transcribe(temp_path,  decoding_config=config)
        response_data={}

        # Add timestamps if exist
        if hasattr(result, 'sentences'):
            sentences = []
            for sentence in result.sentences:
                sentences.append({
                    'text': sentence.text,
                    'start': sentence.start,
                    'end': sentence.end
                })
            response_data = sentences

        # Clean up temporary file
        os.unlink(temp_path)

        return jsonify(response_data), 200

    except Exception as e:
        # Clean up temporary file if it exists
        if 'temp_path' in locals():
            try:
                os.unlink(temp_path)
            except:
                pass

        return jsonify({
            'error': f'Transcription failed: {str(e)}',
            'success': False
        }), 500


if __name__ == '__main__':
    # Run the Flask app
    app.run(host='0.0.0.0', port=5001, debug=True)
