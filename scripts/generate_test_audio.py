import numpy as np
from scipy.io.wavfile import write

sample_rate = 16000
duration = 3  # seconds
t = np.linspace(0, duration, int(sample_rate * duration))
audio = (np.sin(2 * np.pi * 440 * t) * 32767).astype(np.int16)
write("/Users/ricksegrest/code/2026/karaoke-create/shared_data/uploads/real_test_file.wav", sample_rate, audio)
print("Generated real_test_file.wav")
