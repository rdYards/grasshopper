import asyncio
import sounddevice as sd
import numpy as np
import soundfile as sf

class AudioStream:
    def __init__(self):
        self.stream = None
        self.is_playing = False
        self.samples = []
        self.sample_rate = 0

    async def play(self, samples, sample_rate):
        if self.is_playing or self.stream is not None:
            print("Audio is already playing")
            return

        loop = asyncio.get_event_loop()

        def audio_callback(outdata, frames, time, status):
            if len(self.samples) == 0 or not self.is_playing:
                outdata[:] = np.zeros_like(outdata)
                raise sd.CallbackStop()
            else:
                chunksize = min(len(self.samples), frames)
                outdata[:chunksize] = self.samples[:chunksize].reshape(-1, 1)[:chunksize]
                self.samples = self.samples[chunksize:]

        self.is_playing = True
        self.samples = samples.copy()  # Create a copy to avoid modifying the original array
        self.sample_rate = sample_rate

        self.stream = sd.OutputStream(callback=audio_callback, channels=1, samplerate=sample_rate)
        await loop.run_in_executor(None, self.stream.start)

    def stop(self):
        if self.stream and self.is_playing:
            print("Audio stopped")
            self.is_playing = False
            if self.stream is not None:
                self.stream.stop()
                self.stream.close()
                self.stream = None

    def pause(self):
        if self.stream and self.is_playing:
            print("Audio paused")
            self.is_playing = False
            self.samples_remaining = self.samples.copy()  # Save the remaining samples before pausing
            if self.stream is not None:
                self.stream.stop()

    async def resume(self):
        if self.stream and not self.is_playing and hasattr(self, 'samples_remaining'):
            print("Audio resumed")
            self.is_playing = True
            self.samples = self.samples_remaining  # Restore samples before resuming

            # Reinitialize the stream with the new callback
            loop = asyncio.get_event_loop()
            def audio_callback(outdata, frames, time, status):
                if len(self.samples) == 0 or not self.is_playing:
                    outdata[:] = np.zeros_like(outdata)
                    raise sd.CallbackStop()
                else:
                    chunksize = min(len(self.samples), frames)
                    outdata[:chunksize] = self.samples[:chunksize].reshape(-1, 1)[:chunksize]
                    self.samples = self.samples[chunksize:]

            # Restart the stream
            await loop.run_in_executor(None, self.stream.start)
            
    def save(self, filename="output.wav"):
        if len(self.samples) == 0:
            print("No samples available to save.")
            return
    
        # Ensure that samples are formatted correctly (numpy array with shape [-1, 1])
        samples_to_save = np.array(self.samples).reshape(-1, 1)
    
        with sf.SoundFile(filename, mode='w', samplerate=self.sample_rate, channels=1) as f:
            print(f"Writing audio to {filename}...")
            f.write(samples_to_save)