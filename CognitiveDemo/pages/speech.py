import streamlit as st
import sounddevice as sd
import numpy as np
import io
import wave
import time
from modules.speech_module import SpeechTranscriber
from io import BytesIO

# Initialize session state variables
if 'audio_recorder_state' not in st.session_state:
    st.session_state.audio_recorder_state = False
    st.session_state.audio_chunks = []
    st.session_state.start_time = None
    st.session_state.recorded_audio = None

def show_speech():
    # Combo box for selection
    model_type = st.selectbox("Select Model Type:", ["Standard", "Fine Tuned"])

    st.header("Speech Page")
    st.write(f"You selected: {model_type}")

    transcriber = SpeechTranscriber()

    # Option to upload an audio file
    uploaded_file = st.file_uploader("Upload an audio file", type=['wav', 'mp3', 'ogg'])
    
    if uploaded_file is not None:
        st.audio(uploaded_file, format=uploaded_file.type)
        # Read the uploaded file as bytes
        audio_bytes = uploaded_file.read()
        from pydub import AudioSegment

        audio = AudioSegment.from_file(uploaded_file)
        sample_rate = audio.frame_rate
        channels = audio.channels
        bits = audio.sample_width * 8
        
        st.write(f"Sample Rate: {sample_rate} Hz")
        st.write(f"Channels: {channels}")
        st.write(f"Bits: {bits}")

        if st.button('Transcribe Uploaded Audio'):
            with st.spinner('Transcribing...'):
                transcription = transcriber.transcribe(audio_bytes, model=model_type.lower())
                st.json(transcription)

    # Option to record audio
    if st.button('Record Audio'):
        st.subheader("Audio Recording")
        
        def toggle_recording():
            st.session_state.audio_recorder_state = not st.session_state.audio_recorder_state
            if st.session_state.audio_recorder_state:
                st.session_state.start_time = time.time()
                st.session_state.audio_chunks = []
            else:
                duration = time.time() - st.session_state.start_time
                st.write(f"Recording stopped. Duration: {duration:.2f} seconds")

        record_button = st.button("Start/Stop Recording", on_click=toggle_recording)

        if st.session_state.audio_recorder_state:
            st.write("Recording... Click the button again to stop.")
            
            sample_rate = 44100  # Sample rate in Hz
            channels = 1  # Mono audio

            def audio_callback(indata, frames, time, status):
                st.session_state.audio_chunks.append(indata.copy())

            with sd.InputStream(samplerate=sample_rate, channels=channels, callback=audio_callback):
                while st.session_state.audio_recorder_state:
                    st.empty()  # This allows the Streamlit app to update
                    time.sleep(0.1)

        if not st.session_state.audio_recorder_state and len(st.session_state.audio_chunks) > 0:
            recording = np.concatenate(st.session_state.audio_chunks, axis=0)
            buffer = io.BytesIO()
            with wave.open(buffer, 'wb') as wf:
                wf.setnchannels(channels)
                wf.setsampwidth(2)  # 2 bytes per sample
                wf.setframerate(sample_rate)
                wf.writeframes((recording * 32767).astype(np.int16).tobytes())

            st.session_state.recorded_audio = buffer.getvalue()
            st.audio(st.session_state.recorded_audio, format='audio/wav')
            st.success("Audio recorded successfully!")

    if st.button('Transcribe Recorded Audio'):
        if st.session_state.get('recorded_audio') is not None:
            with st.spinner('Transcribing...'):
                transcription = transcriber.transcribe(st.session_state.recorded_audio, model=model_type.lower())
                st.json(transcription)
        else:
            st.warning("Please record audio first before transcribing.")