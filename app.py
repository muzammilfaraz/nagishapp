from flask import Flask, render_template, request
from gtts import gTTS
import os
import pygame
import speech_recognition as sr
import tempfile
from pathlib import Path

app = Flask(__name__)
recognizer = sr.Recognizer()

# Ensure correct template folder path
app = Flask(__name__, template_folder='templates')

# Initialize pygame mixer only once to avoid re-initialization
pygame.mixer.init()

# Create temp directory if it doesn't exist
TEMP_AUDIO_DIR = os.path.join('static', 'temp_audio')
os.makedirs(TEMP_AUDIO_DIR, exist_ok=True)

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Text-to-voice route
@app.route('/text_to_voice', methods=['GET', 'POST'])
def text_to_voice():
    if request.method == 'POST':
        text = request.form.get('text')
        language = request.form.get('language', 'en')  # Default to English if not provided
        
        if text:
            try:
                # Generate TTS using gTTS
                tts = gTTS(text=text, lang=language, slow=False)
                
                # Create a unique temporary file
                temp_file = os.path.join(TEMP_AUDIO_DIR, f"{language}_{next(tempfile._get_candidate_names())}.mp3")
                
                # Save the audio file
                tts.save(temp_file)
                
                try:
                    # Play the audio
                    pygame.mixer.music.load(temp_file)
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        pygame.time.Clock().tick(10)
                finally:
                    # Clean up the file after playing
                    try:
                        os.remove(temp_file)
                    except:
                        pass  # Ignore cleanup errors
                        
            except Exception as e:
                return render_template('text_to_voice.html', error=f"Error: {str(e)}")
    
    return render_template('text_to_voice.html')

# Voice-to-text route
@app.route('/voice_to_text', methods=['GET', 'POST'])
def voice_to_text():
    if request.method == 'POST':
        language = request.form.get('language')
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
            try:
                text = recognizer.recognize_google(audio, language=language)
                return render_template('voice_to_text.html', result=text)
            except sr.UnknownValueError:
                return render_template('voice_to_text.html', result="Could not understand the audio.")
            except sr.RequestError as e:
                return render_template('voice_to_text.html', result=f"Request error: {e}")
    
    return render_template('voice_to_text.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)