import speech_recognition as sr
import requests
from gtts import gTTS
import os
import re

# API Key for Together API
API_KEY = "4eb3afd18344fdf6c699280f9e5e2f08ba5d4c2cc9989b55e7c5c14910af9706"
API_URL = "https://api.together.ai/v1/chat/completions"  # Example endpoint (verify the actual URL)

def clean_text(text):
    """Hapus tag XML/HTML dari output AI"""
    clean = re.sub(r"<.*?>", "", text)  # Hapus semua tag dalam <>, untuk membersihkan hasil raw
    return clean.strip()

def text_to_speech(text):
    """Mengubah teks menjadi suara dan langsung diputar menggunakan mpg123"""
    tts = gTTS(text=text, lang="en")  # Ubah ke "en" untuk Bahasa Inggris
    tts.save("response.mp3")

    # Gunakan mpg123 untuk memutar file MP3 di Termux
    os.system("mpg123 response.mp3")

def speech_to_text():
    """Mengubah suara menjadi teks"""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Say something...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

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

    # Membuat data untuk dikirim ke API
    data = {
        "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",  # Gantilah jika modelnya berbeda
        "messages": [{"role": "user", "content": full_prompt}],
    }
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # Kirim permintaan ke API Together
    response = requests.post(API_URL, json=data, headers=headers)

    if response.status_code == 200:
        raw_output = response.json()["choices"][0]["message"]["content"]
        return clean_text(raw_output)  # Bersihkan sebelum dikembalikan
    else:
        print(f"❌ Error: {response.status_code}")
        return "Sorry, I couldn't process that request."

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
