import asyncio
import sounddevice as sd
import numpy as np
import soundfile as sf
import logging

# Configure logging for this module
logger = logging.getLogger(__name__)

# AudioStream is an abstraction of Kokoro controls. Providing the following functions:
# play: Plays audio samples.
# stop: Stops playing audio.
# pause: Pauses playing audio.
# resume: Resumes paused audio.
# save: Saves current audio samples to a file.
#
# Note! for pause and resume to work properly must be used in a asyncio enviroment.
# All other functions work outside of an asyncio enviroment.


class AudioStream:
    def __init__(self):
        self.stream = None
        self.is_playing = False
        self.samples = []
        self.sample_rate = 0

    async def play(self, samples, sample_rate):
        """
        Play the given audio samples at the specified sample rate.

        Args:
            samples (numpy.ndarray): The audio samples to be played.
            sample_rate (int): The sampling rate of the audio data in Hz.
        """
        if self.is_playing or self.stream is not None:
            logger.info("Audio is already playing")
            return

        loop = asyncio.get_event_loop()

        def audio_callback(outdata, frames, time, status):
            """Callback function to provide audio data for sounddevice stream."""
            if len(self.samples) == 0 or not self.is_playing:
                outdata[:] = np.zeros_like(outdata)
                raise sd.CallbackStop()
            else:
                chunksize = min(len(self.samples), frames)
                outdata[:chunksize] = self.samples[:chunksize].reshape(-1, 1)[
                    :chunksize
                ]
                self.samples = self.samples[chunksize:]

        # Set up for playing new samples
        self.is_playing = True
        self.samples = (
            samples.copy()
        )  # Create a copy to avoid modifying the original array
        self.sample_rate = sample_rate

        # Initialize sounddevice output stream with our callback function
        self.stream = sd.OutputStream(
            callback=audio_callback, channels=1, samplerate=sample_rate
        )
        await loop.run_in_executor(None, self.stream.start)

    def stop(self):
        """
        Stop playing the audio.

        This method stops the audio playback immediately.
        """
        if self.stream and self.is_playing:
            logger.info("Audio stopped")
            self.is_playing = False
            if self.stream is not None:
                # Clean up stream resources
                self.stream.stop()
                self.stream.close()
                self.stream = None

    def pause(self):
        """
        Pause the audio playback.

        This method pauses the current audio playback and saves the remaining samples.
        """
        if self.stream and self.is_playing:
            logger.info("Audio paused")
            self.is_playing = False  # Indicate that playing has been paused
            # Save the remaining samples before pausing
            self.samples_remaining = self.samples.copy()
            if self.stream is not None:
                self.stream.stop()

    async def resume(self):
        """
        Resume playing the audio.

        This method resumes playback from where it was paused.
        """
        if self.stream and not self.is_playing and hasattr(self, "samples_remaining"):
            logger.info("Audio resumed")
            self.is_playing = True  # Indicate that playing is resumed
            self.samples = self.samples_remaining  # Restore samples before resuming

            # Reinitialize the stream with the new callback
            loop = asyncio.get_event_loop()

            def audio_callback(outdata, frames, time, status):
                if len(self.samples) == 0 or not self.is_playing:
                    outdata[:] = np.zeros_like(outdata)
                    raise sd.CallbackStop()
                else:
                    chunksize = min(len(self.samples), frames)
                    # Prepare the audio chunk to be played
                    outdata[:chunksize] = self.samples[:chunksize].reshape(-1, 1)[
                        :chunksize
                    ]
                    self.samples = self.samples[chunksize:]

            # Restart the stream with new callback settings
            await loop.run_in_executor(None, self.stream.start)

    def save(self, filename="output.wav"):
        """
        Save current audio samples to a file.

        Args:
            filename (str): The name of the file to save the samples to.
                Defaults to "output.wav".
        """
        if len(self.samples) == 0:
            logger.info("No samples available to save.")
            return

        # Ensure that samples are formatted correctly for saving
        samples_to_save = np.array(self.samples).reshape(-1, 1)

        with sf.SoundFile(
            filename, mode="w", samplerate=self.sample_rate, channels=1
        ) as f:
            logger.info(f"Writing audio to {filename}...")
            f.write(samples_to_save)
