from RealtimeSTT import AudioToTextRecorder
from threading import Thread
from ollama import Client, chat, ChatResponse
from pydub import AudioSegment
from pydub.playback import play

# Initialize Ollama client with localhost and gemma3 model
start_up_audio = AudioSegment.from_file("audio/start_up.mp3", format="mp3")
wake_word_audio = AudioSegment.from_file("audio/PM_CSPH_Beeps_47.mp3", format="mp3")
kill_yourself_audio = AudioSegment.from_file("audio/kill_yourself.mp3", format="mp3")
ollama_client = Client(host="http://localhost:11434")

def on_wakeword():
    print("Wake word detected, please speak...")
    play(wake_word_audio)

def on_recording_stop():
    print("Recording stopped, waiting for transcription...")

def process_text(text):
    if "kill yourself" in text.lower() or "kill your self" in text.lower():
        play(kill_yourself_audio)
        return
    
    # Check for shutdown command in the transcribed text
    if "shutdown now" in text.lower() or "shut down now" in text.lower():
        print("Shutdown command received. Shutting down...")
        recorder.shutdown()  # Properly call the shutdown method
        exit()  # exit the program after shutdown
        
    # Use Ollama client to process and respond to the transcribed text
    print(f"Ollama Input: {text}")
    response: ChatResponse = chat(model='gemma3:4b', messages=[
      {
        'role': 'user',
        'content': text,
      },
    ])
    if isinstance(response, ChatResponse):
        print(f"Ollama Response: {response.message.content}")
    else:
        print("Failed to get a valid response from Ollama")
    
if __name__ == '__main__':
    with AudioToTextRecorder(
        model="medium.en",
        language="en",
        wakeword_backend="pvporcupine",
        wake_words="grasshopper",
        on_wakeword_detected=on_wakeword,
        on_recording_stop=on_recording_stop
    ) as recorder:
        print('Say "grasshopper" to start.')
        play(start_up_audio)
        while True:
            recorder.text(process_text)
