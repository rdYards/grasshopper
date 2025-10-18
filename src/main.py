from RealtimeSTT import AudioToTextRecorder
from playsound import playsound
from threading import Thread
from ollama import Client

def on_wakeword():
    print("Wake word detected, please speak...")

def on_recording_stop():
    print("Recording stopped, waiting for transcription...")

def process_text(text):
    print(f"Transcription: {text}")
    if "kill yourself" in text.lower() or "kill your self" in text.lower():
        Thread(target=playsound, args=('audio/kill_yourself.mp3')).start()
        return
    
    # Check for shutdown command in the transcribed text
    if "shutdown now" in text.lower() or "shut down now" in text.lower():
        print("Shutdown command received. Shutting down...")
        recorder.shutdown()  # Properly call the shutdown method
        exit()  # Optional: exit the program after shutdown
    
if __name__ == '__main__':
    Thread(target=playsound, args=('audio/start_up.mp3')).start()
    with AudioToTextRecorder(
        model="medium.en",
        language="en",
        wakeword_backend="pvporcupine",
        wake_words="grasshopper",
        on_wakeword_detected=on_wakeword,
        on_recording_stop=on_recording_stop
    ) as recorder:
        print('Say "grasshopper" to start.')
        while True:
            recorder.text(process_text)
