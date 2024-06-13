import os
import fitz  # PyMuPDF
from gtts import gTTS
from flask import Flask, request, redirect, url_for, send_from_directory, render_template, flash
from werkzeug.utils import secure_filename
from pydub import AudioSegment

# Configuration
UPLOAD_FOLDER = 'uploads'
AUDIOBOOK_FOLDER = 'audiobooks'
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['AUDIOBOOK_FOLDER'] = AUDIOBOOK_FOLDER
app.secret_key = 'supersecretkey'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(AUDIOBOOK_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        document = fitz.open(pdf_path)
        for page_num in range(len(document)):
            page = document.load_page(page_num)
            text += page.get_text()
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None

def save_text_as_audio(text, audio_path):
    try:
        # Split text into chunks
        text_chunks = [text[i:i + 5000] for i in range(0, len(text), 5000)]
        audio_segments = []

        for chunk in text_chunks:
            tts = gTTS(text=chunk, lang='en')
            chunk_path = audio_path.replace('.mp3', f'_{len(audio_segments)}.mp3')
            tts.save(chunk_path)
            audio_segments.append(AudioSegment.from_mp3(chunk_path))
        
        # Concatenate all audio segments
        combined_audio = sum(audio_segments)
        combined_audio.export(audio_path, format='mp3')

        # Remove temporary chunk files
        for chunk in text_chunks:
            os.remove(chunk_path)
        
    except Exception as e:
        print(f"Error converting text to audio: {e}")
        return False
    return True

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            text = extract_text_from_pdf(file_path)
            if text is None:
                flash('Failed to extract text from PDF.')
                return redirect(request.url)
            
            audio_filename = os.path.splitext(filename)[0] + '.mp3'
            audio_path = os.path.join(app.config['AUDIOBOOK_FOLDER'], audio_filename)
            
            if save_text_as_audio(text, audio_path):
                return redirect(url_for('uploaded_file', filename=audio_filename))
            else:
                flash('Failed to convert text to audio.')
                return redirect(request.url)
    return render_template('index.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['AUDIOBOOK_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
