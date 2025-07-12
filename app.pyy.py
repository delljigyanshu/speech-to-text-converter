from flask import Flask, render_template, request, redirect
import os
import speech_recognition as sr
from pydub import AudioSegment
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'audio_files')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        return redirect(request.url)

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Convert mp3 to wav if needed
        if file_path.endswith('.mp3'):
            sound = AudioSegment.from_mp3(file_path)
            wav_path = file_path.replace('.mp3', '.wav')
            sound.export(wav_path, format='wav')
            file_path = wav_path

        recognizer = sr.Recognizer()

        try:
            with sr.AudioFile(file_path) as source:
                audio_data = recognizer.record(source)

            text = recognizer.recognize_google(audio_data)
        except sr.UnknownValueError:
            text = "Sorry, speech was not recognized."
        except sr.RequestError:
            text = "Google Speech Recognition service is unavailable."
        except Exception as e:
            text = f"Error: {str(e)}"

        return render_template('index.html', transcription=text)

    return redirect('/')


@app.route('/microphone', methods=['POST'])
def microphone_input():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("\nListening... Speak now!")
        audio_data = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio_data)
    except sr.UnknownValueError:
        text = "Sorry, speech was not recognized."
    except sr.RequestError:
        text = "Google Speech Recognition service is unavailable."
    except Exception as e:
        text = f"Error: {str(e)}"

    return render_template('index.html', transcription=text)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000, debug=True)
