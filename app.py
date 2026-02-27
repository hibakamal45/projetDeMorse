import streamlit as st
import cv2
import time
import numpy as np
from gtts import gTTS
import os
import pygame
from eye_blink_detector import EyeBlinkDetector
from morse_translator import get_char_from_sequence, MORSE_CODE_DICT

# Initialize pygame for audio
pygame.mixer.init()

# Streamlit Page Config
st.set_page_config(page_title="EyeSpeak - Morse Eye Communication", layout="wide")

# Custom CSS for styling
st.markdown("""
<style>
    .main {
        background-color: #f0f2f6;
    }
    .stButton>button {
        width: 100%;
    }
    .morse-code {
        font-family: monospace;
        font-size: 24px;
        font-weight: bold;
        color: #1e88e5;
    }
    .translated-text {
        font-size: 32px;
        color: #2e7d32;
        border: 2px solid #2e7d32;
        padding: 10px;
        border-radius: 5px;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if 'translated_text' not in st.session_state:
    st.session_state.translated_text = ""
if 'current_morse' not in st.session_state:
    st.session_state.current_morse = ""
if 'last_blink_time' not in st.session_state:
    st.session_state.last_blink_time = time.time()
if 'is_running' not in st.session_state:
    st.session_state.is_running = False

# Sidebar: Settings and Info
with st.sidebar:
    st.title("👁️ Paramètres")
    blink_thresh = st.slider("Sensibilité du clignement (Seuil EAR)", 0.05, 0.50, 0.15, format="%.2f")
    short_blink = st.slider("Durée max point (.) (sec)", 0.1, 1.0, 0.4)
    long_blink = st.slider("Durée max trait (-) (sec)", 0.5, 3.0, 1.2)
    char_pause = st.slider("Pause entre caractères (sec)", 1.0, 5.0, 2.0)
    word_pause = st.slider("Pause entre mots (sec)", 3.0, 10.0, 5.0)
    
    st.divider()
    st.header("📖 Guide Morse")
    for char, code in list(MORSE_CODE_DICT.items())[:10]: # Just some for reference
        st.write(f"**{char}**: {code}")
    if st.button("Voir tout le guide"):
        st.write(MORSE_CODE_DICT)

# Main App Layout
st.title("EyeSpeak – Assistance à la Communication")
st.write("Communiquez en clignant des yeux : court pour '.', long pour '-'.")

tab1, tab2 = st.tabs(["💬 Communication en temps réel", "🎓 Apprentissage Morse"])

with tab1:
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("📹 Flux Vidéo")
        run_btn = st.button("Démarrer / Arrêter la Caméra", key="run_comm")
        if run_btn:
            st.session_state.is_running = not st.session_state.is_running
        
        video_placeholder = st.empty()
        
    with col2:
        st.header("📝 Communication")
        st.subheader("Code Morse en cours :")
        morse_display = st.empty()
        
        st.subheader("Texte traduit :")
        text_display = st.empty()
        
        if st.button("🔊 Lire le texte (TTS)"):
            if st.session_state.translated_text:
                try:
                    tts = gTTS(text=st.session_state.translated_text, lang='fr')
                    tts.save("temp_voice.mp3")
                    st.audio("temp_voice.mp3", autoplay=True)
                except Exception as e:
                    st.error(f"Erreur TTS : {e}")
                    
        if st.button("🗑️ Effacer"):
            st.session_state.translated_text = ""
            st.session_state.current_morse = ""

with tab2:
    st.header("🎓 Entraînement au Code Morse")
    st.write("Exercez-vous à cligner pour chaque lettre.")
    
    target_char = st.selectbox("Sélectionnez une lettre à pratiquer :", list(MORSE_CODE_DICT.keys()))
    st.info(f"Le code Morse pour **{target_char}** est : `{MORSE_CODE_DICT[target_char]}`")
    
    col_learn1, col_learn2 = st.columns([2, 1])
    with col_learn1:
        learn_video_placeholder = st.empty()
    with col_learn2:
        learn_status = st.empty()
        learn_morse = st.empty()
        if st.button("Vérifier"):
            if st.session_state.current_morse == MORSE_CODE_DICT[target_char]:
                st.success(f"Bravo ! Vous avez cligné '{target_char}' avec succès.")
            else:
                st.error(f"Pas tout à fait. Essayez encore. Attendu: `{MORSE_CODE_DICT[target_char]}`, Reçu: `{st.session_state.current_morse}`")

# Main processing loop
if st.session_state.is_running:
    cap = cv2.VideoCapture(0)
    detector = EyeBlinkDetector(blink_threshold=blink_thresh, short_blink_limit=short_blink, long_blink_limit=long_blink)
    
    while st.session_state.is_running:
        ret, frame = cap.read()
        if not ret:
            st.error("Impossible d'accéder à la caméra.")
            break
            
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        blink_event, ear, frame, landmarks = detector.process_frame(frame)
        
        # Draw landmarks for debugging
        if landmarks:
            # Draw all eye landmarks
            for idx in [detector.LEFT_UPPER, detector.LEFT_LOWER, detector.RIGHT_UPPER, detector.RIGHT_LOWER]:
                lm = landmarks[idx]
                px, py = int(lm.x * w), int(lm.y * h)
                cv2.circle(frame, (px, py), 2, (0, 255, 255), -1)
            
            # Draw a circle around the face to show it's detected
            cv2.putText(frame, "VISAGE DETECTE", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "VISAGE NON DETECTE", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # Display EAR on frame
        cv2.putText(frame, f"EAR: {ear:.4f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        if detector.is_blinking:
            cv2.putText(frame, "CLIGNEMENT!", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
        # Update video
        if video_placeholder:
            video_placeholder.image(frame, channels="BGR")
        if learn_video_placeholder:
            learn_video_placeholder.image(frame, channels="BGR")
        
        # Logic for Morse events
        if blink_event:
            if blink_event == "reset":
                st.session_state.current_morse = ""
                st.session_state.translated_text = ""
            else:
                st.session_state.current_morse += blink_event
                st.session_state.last_blink_time = time.time()
                
        # Logic for pauses (detect end of character or word)
        current_time = time.time()
        time_since_last = current_time - st.session_state.last_blink_time
        
        if st.session_state.current_morse != "":
            if time_since_last > char_pause:
                # End of character
                char = get_char_from_sequence(st.session_state.current_morse)
                if char != "?":
                    st.session_state.translated_text += char
                st.session_state.current_morse = ""
                st.session_state.last_blink_time = current_time # Reset for word pause detection
            elif time_since_last > word_pause and st.session_state.translated_text != "" and not st.session_state.translated_text.endswith(" "):
                st.session_state.translated_text += " "
        
        # Update displays
        morse_display.markdown(f'<div class="morse-code">{st.session_state.current_morse}</div>', unsafe_allow_html=True)
        text_display.markdown(f'<div class="translated-text">{st.session_state.translated_text}</div>', unsafe_allow_html=True)
        
        # Small delay for responsiveness
        time.sleep(0.01)
        
    cap.release()
else:
    st.info("Appuyez sur 'Démarrer la Caméra' pour commencer.")
