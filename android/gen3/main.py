import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import os
import re
import subprocess

# Inisialisasi Together AI
from together import Together
client = Together(api_key="4eb3afd18344fdf6c699280f9e5e2f08ba5d4c2cc9989b55e7c5c14910af9706")

def clean_text(text):
    """Hapus tag XML/HTML dari output AI"""
    clean = re.sub(r"<.*?>", "", text)  # Hapus semua tag dalam <>, untuk membersihkan hasil raw
    return clean.strip()

def text_to_speech(text):
    """Mengubah teks menjadi suara dan langsung diputar"""
    tts = gTTS(text=text, lang="en")  # Ubah ke "en" untuk Bahasa Inggris
    tts.save("response.mp3")

    # Putar langsung tanpa delay dengan Termux API
    subprocess.run(["termux-media-player", "play", "response.mp3"])

def speech_to_text():
    """Mengubah suara menjadi teks"""
    recognizer = sr.Recognizer()
    
    # Gunakan termux API untuk merekam suara
    print("🎤 Say something...")
    subprocess.run(["termux-microphone-record", "-d", "10", "audio.wav"])
    
    # Proses file audio
    with sr.AudioFile("audio.wav") as source:
        audio = recognizer.record(source)
    
    try:
        text = recognizer.recognize_google(audio, language="en-US")  # Ubah ke "en-US" untuk Bahasa Inggris
        print(f"📝 You said: {text}")
        return text
    except sr.UnknownValueError:
        print("❌ Could not understand the audio.")
        return ""
    except sr.RequestError:
        print("❌ Error with Google Speech Recognition.")
        return ""

def ai_chat(prompt):
    """Mendapatkan jawaban dari Together AI"""
    # Tambahkan peran atau persona untuk AI
    persona = "You are a helpful assistant named 'exora' not descriptive and not talk much but if someone ask you about cryptocurrency you smart at it"

    # Gabungkan persona dengan input pengguna
    full_prompt = f"{persona} {prompt}"
    
    response = client.chat.completions.create(
        model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        messages=[{"role": "user", "content": full_prompt}],
    )
    
    raw_output = response.choices[0].message.content
    return clean_text(raw_output)  # Bersihkan sebelum dikembalikan

# Main Loop
while True:
    user_input = speech_to_text()
    if user_input.lower() == "stop":
        print("👋 Exiting program...")
        break

    if user_input:
        response = ai_chat(user_input)
        print(f"🤖 AI: {response}")
        text_to_speech(response)
