import pandas as pd
import os
import spacy
from fuzzywuzzy import process  # Untuk fuzzy matching

# File dataset
file_path = 'brain.csv'

# Load dataset atau buat baru jika belum ada
if os.path.exists(file_path):
    df = pd.read_csv(file_path)
else:
    df = pd.DataFrame(columns=['Question', 'Answer', 'POS_Tags'])
    df.to_csv(file_path, index=False)

# Load model bahasa spaCy
nlp = spacy.load('en_core_web_sm')

# 🔥 Fungsi untuk mencari jawaban dengan fuzzy matching
def get_answer(question):
    global df
    if df.empty:
        return None
    
    # Gunakan fuzzy matching untuk mencari pertanyaan yang paling mirip
    match = process.extractOne(question, df['Question']) if not df.empty else (None, 0, None)
    if match and match[0]:  
        best_match, score = match[0], match[1]
        if score > 80:  # Jika kemiripan lebih dari 80%
            matched_row = df[df['Question'] == best_match]
            return matched_row['Answer'].values[0]
    
    return None  # Jika tidak ada match yang cukup mirip

# 🔥 Fungsi untuk menambahkan data baru + POS tagging
def add_new_data(question, answer):
    global df
    # Analisis jenis kata dengan spaCy
    doc = nlp(question)
    pos_tags = ", ".join([f"{token.text}/{token.pos_}" for token in doc])  # Simpan jenis kata

    # Simpan ke dataset
    new_data = pd.DataFrame([[question, answer, pos_tags]], columns=['Question', 'Answer', 'POS_Tags'])
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_csv(file_path, index=False)
    print("✅ Data baru disimpan dengan POS tagging!")

# 🔥 Fungsi untuk memahami jenis kata dalam kalimat
def analyze_sentence(sentence):
    doc = nlp(sentence)
    pos_info = {token.text: token.pos_ for token in doc}  # Simpan dalam dictionary
    return pos_info

# Loop interaksi AI
while True:
    user_input = input("kamu: ")
    if user_input.lower() == 'exit':
        break

    # Analisis kalimat untuk memahami kata-kata
    pos_analysis = analyze_sentence(user_input)
    
    # Cek apakah AI sudah tahu jawaban dari pertanyaan ini
    answer = get_answer(user_input)
    if answer:
        print("🤖 AI:", answer)
    else:
        new_answer = input("Aku belum tahu, kasih tahu dong jawabannya: ")
        add_new_data(user_input, new_answer)
        print("🙏 Thanks! Aku sudah belajar jawaban baru.")
    
    # Jika pengguna mengetik "remake", AI akan meminta jawaban yang benar
    if user_input.lower() == 'remake':
        print("🤖 AI: Oops, jawabannya salah. Tolong beri tahu jawabannya yang benar.")
        user_input = input("Masukkan Pertanyaan: ")
        correct_answer = input("Masukkan jawaban yang benar: ")
        add_new_data(user_input, correct_answer)
        print(f"✅ Jawaban yang benar telah ditambahkan untuk pertanyaan '{user_input}'.")
