import logging
from RealtimeSTT import AudioToTextRecorder
from threading import Thread
from ollama import Client, chat, ChatResponse
from pydub import AudioSegment
from pydub.playback import play
from kokoro_onnx import Kokoro
from kokoro_onnx.tokenizer import Tokenizer
from tts import AudioStream
import numpy as np
import os

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to desired logging level (DEBUG, INFO, WARNING, ERROR)
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Outputs logs to console
    ]
)

logger = logging.getLogger(__name__)

# Initialize Ollama client with localhost and gemma3 model
ollama_client = Client(host="http://localhost:11434")  # change url if needed

# Initialize all sound files used for various events in the program
start_up_audio = AudioSegment.from_file("audio/start_up.mp3", format="mp3")
wake_word_audio = AudioSegment.from_file("audio/PM_CSPH_Beeps_47.mp3", format="mp3")
kill_yourself_audio = AudioSegment.from_file("audio/kill_yourself.mp3", format="mp3")

# Initialize Kokoro STT server for speech-to-text conversion
kokoro = Kokoro("kokoro/kokoro-v1.0.onnx", "kokoro/voices-v1.0.bin")
tokenizer = Tokenizer()
voice = "im_nicola"
blend_voice_name = "bm_george"

# Retrieve and blend voice styles for text-to-speech output
first_voice = kokoro.get_voice_style(voice)
second_voice = kokoro.get_voice_style(blend_voice_name)
blended_voice = np.add(first_voice * (50 / 100), second_voice * (50 / 100))


def on_wakeword():
    """Callback function executed when the wake word is detected."""
    logger.info("Wake word detected, please speak...")
    play(wake_word_audio)


def on_recording_stop():
    """Callback function executed when recording stops."""
    logger.debug("Recording stopped, waiting for transcription...")


def process_text(text):
    """
    Process the transcribed text and take appropriate actions:
    - Respond with an audio message if specific phrases are detected.
    - Shut down the system if a shutdown command is detected.
    - Otherwise, use the Ollama client to generate a response.

    Args:
        text (str): Transcribed text from speech-to-text conversion.
    """

    # Check for specific phrases that trigger pre-defined responses
    if "kill yourself" in text.lower() or "kill your self" in text.lower():
        logger.debug("Detected kill word, return back to standby")
        play(kill_yourself_audio)
        return

    # Check for shutdown command in the transcribed text
    if "shutdown now" in text.lower() or "shut down now" in text.lower():
        logger.info("Shutdown command received. Shutting down...")
        recorder.shutdown()  # Properly call the shutdown method
        exit()  # exit the program after shutdown

    # Use Ollama client to process and respond to the transcribed text
    logger.debug(f"Ollama Input: {text}")
    response: ChatResponse = chat(
        model="gemma3:4b",
        messages=[
            {
                "role": "user",
                "content": text,
            },
        ],
    )
    # Check if a valid response is received from the Ollama client
    if isinstance(response, ChatResponse):
        phonemes = tokenizer.phonemize(response.message.content, lang="en-us")
        samples, sample_rate = kokoro.create(
            phonemes, voice=blended_voice, speed=1.0, is_phonemes=True
        )

        # Set variable for output directory to remove after use
        output_dir = "output"  # Change string here for difference save location
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        output_path = os.path.join(output_dir, "output.wav")

        logger.debug(f"Sample length: {len(samples)}, Sample rate: {sample_rate}")

        audio_stream = AudioStream()
        audio_stream.samples = samples
        audio_stream.sample_rate = sample_rate

        # Save the generated audio in the output directory
        # Current setup is designed to replace previous output.
        audio_stream.save(output_path)
        ollama_output_audio = AudioSegment.from_file(output_path, format="wav")
        logger.debug(f"Ollama Response: {response.message.content}")
        play(ollama_output_audio)
    else:
        logger.error("Failed to get a valid response from Ollama")


# Main entry point of the program
if __name__ == "__main__":
    with AudioToTextRecorder(
        model="medium.en",
        language="en",
        wakeword_backend="pvporcupine",
        wake_words="grasshopper",
        on_wakeword_detected=on_wakeword,
        on_recording_stop=on_recording_stop,
    ) as recorder:
        logger.info('Say "grasshopper" to start.')
        play(start_up_audio)
        while True:
            recorder.text(process_text)
