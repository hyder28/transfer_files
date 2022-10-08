from vosk import Model, KaldiRecognizer, SetLogLevel
from pydub import AudioSegment
import wave

from time import perf_counter
from pathlib import Path
import os
import json

SetLogLevel(0)

input_fpath = "/Users/hyderali/Documents/data/docs-archives/audio"

results = {}

for fname in os.listdir(input_fpath):
    input_fname = os.path.join(input_fpath, fname)

    temp_folder = Path("tmp/")
    if not os.path.isdir(temp_folder):
        os.mkdir(temp_folder)

    for f in os.listdir(temp_folder):
        os.remove(os.path.join(temp_folder, f))

    t0 = perf_counter()

    if input_fname.endswith('.mp3') or input_fname.endswith('.MP3'):
        sound = AudioSegment.from_mp3(input_fname)
    elif input_fname.endswith('.wav') or input_fname.endswith('.WAV'):
        sound = AudioSegment.from_wav(input_fname)
    elif input_fname.endswith('.ogg'):
        sound = AudioSegment.from_ogg(input_fname)
    elif input_fname.endswith('.flac'):
        sound = AudioSegment.from_file(input_fname, "flac")
    elif input_fname.endswith('.3gp'):
        sound = AudioSegment.from_file(input_fname, "3gp")
    elif input_fname.endswith('.3g'):
        sound = AudioSegment.from_file(input_fname, "3g")
    else:
        sound = None

    sound = sound.set_frame_rate(16000)
    sound = sound.set_channels(1)

    sound.export(os.path.join(temp_folder, "audio_file.wav"), format="wav")
    wf = wave.open(os.path.join(temp_folder, "audio_file.wav"))

    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        print("Audio file must be WAV format mono PCM.")

    model = Model("models/vosk-model-en-us-0.22")
    rec = KaldiRecognizer(model, wf.getframerate())

    transcription = []

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break

        if rec.AcceptWaveform(data):
            result_dict = json.loads(rec.Result())
            transcription.append(result_dict.get("text", ""))

    final_result = json.loads(rec.FinalResult())
    transcription.append(final_result.get("text", ""))

    transcription_text = " ".join(transcription)
    transcription_text = " ".join(transcription_text.strip().split())

    elapsed = perf_counter() - t0

    result = {"transcribed_text": transcription_text, "elapsed_time": f"{elapsed}s"}
    print(transcription_text)

    results[fname] = result

print(json.dumps(results, indent=4))