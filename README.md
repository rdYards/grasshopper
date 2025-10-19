# Grasshopper, voice assistant
## Speech-to-Text & Text-to-Speech Application

## Overview
Grasshopper is a voice-activated assistant application built to be an assistant in personal RPG campaigns. This project leverages the following libraries and models for both speech-to-text (STT) and text-to-speech (TTS) functionalities, making it a robust solution for interactive conversations.

The project is built to work via localhost [Ollama](https://github.com/ollama/ollama) using gemma3:4b. You can change the model if needed bu the hardcoded variable *model* found in `src/main.py`

## Features
- **Wake Word Detection**: Activates the system with specific wake words.
- **Real-Time Speech Transcription**: Converts spoken language to written text in real-time.
- **Intelligent Response Generation**: Utilizes Ollama's client API to generate contextually appropriate responses.
- **Text-to-Speech Synthesis**: Converts generated text back into speech using advanced TTS models.

## Components
### 1. [RealtimeSTT (AudioToTextRecorder)](https://github.com/KoljaB/RealtimeTTS)
RealtimeTTS is a state-of-the-art text-to-speech (TTS) library designed for real-time applications. It stands out in its ability to convert text streams fast into high-quality auditory output with minimal latency.
### 2. [Ollama Client](https://github.com/ollama/ollama-python)
The Ollama Python library provides the easiest way to integrate Python 3.8+ projects with [Ollama](https://github.com/ollama/ollama).
### 3. [Kokoro-ONNX](https://github.com/thewh1teagle/kokoro-onnx)
TTS with onnx runtime based on [Kokoro-TTS](https://huggingface.co/spaces/hexgrad/Kokoro-TTS)

## Setup
To set up the project, follow these steps:
1. **Clone the Repository**:
    ```sh
    git clone https://github.com/yourusername/grasshopper.git
    cd grasshopper
    ```
2. **Install Dependencies**:
    Ensure you have Python installed on your system. Then install all required libraries using:
    ```sh
    pip install -r requirements.txt
    ```
3. **Kokoro Models**: If needd download the `kokoro-v1.0.onnx` model file and `voices-v1.0.bin` file, and place them in a folder named `kokoro/` within your project root.

## Usage
Run the main application with:

```sh
python src/main.py
```

Once started, the system will play a startup audio notification and listen for the wake word ("grasshopper") to activate transcription and response generation. You can speak commands or queries which will be processed, responded to, and played back through TTS.

## Specific Commands
- **"Cancel now"**: Cancels transcription when wakeword detected.
- **"Shutdown now"**: Initiates a shutdown sequence for the program.

## Audio Files Source
All sounds used in this project were sourced from Zapsplat:
- [Zapsplat](https://www.zapsplat.com/)
- Author: PMSFX [Author Profile](https://www.zapsplat.com/author/pmsfx/)

## License
This project is open source and available under the MIT License.