import os
import json
import azure.cognitiveservices.speech as speechsdk
import io
from io import BytesIO

class SpeechTranscriber:
    def __init__(self):
        # Get values from .env file
        self.speech_key = os.getenv('AZURE_COGNITIVE_SERVICE_KEY')
        self.speech_region = os.getenv('AZURE_SPEECH_REGION')

    def transcribe_with_fine_tuned_model(self, audio_input):
        # Configure speech recognition with the fine-tuned model
        speech_config = speechsdk.SpeechConfig(subscription=self.speech_key, region=self.speech_region)
        speech_config.endpoint_id = self.endpoint_id

        # Determine if input is a file path or audio data
        if isinstance(audio_input, str):
            audio_config = speechsdk.audio.AudioConfig(filename=audio_input)
        else:
            audio_config = speechsdk.audio.AudioConfig(stream=audio_input)

        # Create speech recognizer with the fine-tuned model
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

        # Perform speech recognition
        result = speech_recognizer.recognize_once_async().get()

        # Prepare the result
        transcription_result = {
            "text": result.text,
            "confidence": result.confidence
        }

        return json.dumps(transcription_result)

    def transcribe(self, audio_input, model="standard"):
        # Configure speech recognition
        speech_config = speechsdk.SpeechConfig(subscription=self.speech_key, region=self.speech_region)
        speech_config.speech_recognition_language = "it-IT"
        in_memory_stream = None
        audio_config = None
        
        if model.lower() != "standard":
            return self.transcribe_with_fine_tuned_model(audio_input)

        # Determine if input is a file path or audio data
        if isinstance(audio_input, str):
            audio_config = speechsdk.audio.AudioConfig(filename=audio_input)
        else:
            # Initialize the in-memory stream
            in_memory_stream = InMemoryStream(audio_input)
            pull_stream = speechsdk.audio.PullAudioInputStream(callback=in_memory_stream)
            audio_config = speechsdk.audio.AudioConfig(stream=pull_stream)


        # Create speech recognizer
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

        # Perform speech recognition
        result = speech_recognizer.recognize_once_async().get()

        # Prepare the result
        transcription_result = {
            "text": result.text,
            "confidence": result.confidence
        }

        return json.dumps(transcription_result)

class InMemoryStream(speechsdk.audio.PullAudioInputStreamCallback):
    def __init__(self, audio_bytes):
        super().__init__()
        self.audio = io.BytesIO(audio_bytes)
    
    def read(self, buffer):
        data = self.audio.read(len(buffer))
        if not data:
            return 0  # No more data
        buffer[:len(data)] = data
        return len(data)
    
    def get_format(self):
        # Define the audio format. Adjust based on your audio file's specifications.
        return speechsdk.audio.AudioStreamFormat(samples_per_second=16000, bits_per_sample=16, channels=1)
