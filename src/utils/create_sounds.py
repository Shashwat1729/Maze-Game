import wave
import struct
import math
import os
from constants import SOUNDS_DIR

def create_sine_wave(frequency, duration, volume=0.5, sample_rate=44100):
    n_samples = int(sample_rate * duration)
    wave_data = []
    for i in range(n_samples):
        t = float(i) / sample_rate
        wave_data.append(volume * math.sin(2 * math.pi * frequency * t))
    return wave_data

def save_wave_file(filename, wave_data, sample_rate=44100):
    with wave.open(filename, 'w') as wave_file:
        n_channels = 1
        sample_width = 2
        wave_file.setparams((n_channels, sample_width, sample_rate, len(wave_data), 'NONE', 'not compressed'))
        
        # Convert to 16-bit integers
        scaled = [int(sample * 32767) for sample in wave_data]
        wave_file.writeframes(struct.pack('h' * len(scaled), *scaled))

def create_coin_sound():
    # High-pitched short beep
    wave_data = create_sine_wave(880, 0.1)  # A5 note
    save_wave_file(os.path.join(SOUNDS_DIR, 'coin.wav'), wave_data)

def create_powerup_sound():
    # Rising pitch
    wave_data = []
    for freq in range(440, 880, 20):  # A4 to A5
        wave_data.extend(create_sine_wave(freq, 0.02))
    save_wave_file(os.path.join(SOUNDS_DIR, 'powerup.wav'), wave_data)

def create_level_complete_sound():
    # Triumphant jingle
    wave_data = []
    for freq in [440, 554, 659, 880]:  # A4, C#5, E5, A5
        wave_data.extend(create_sine_wave(freq, 0.15))
    save_wave_file(os.path.join(SOUNDS_DIR, 'level_complete.wav'), wave_data)

def create_game_over_sound():
    # Descending notes
    wave_data = []
    for freq in [440, 392, 349, 294]:  # A4, G4, F4, D4
        wave_data.extend(create_sine_wave(freq, 0.2))
    save_wave_file(os.path.join(SOUNDS_DIR, 'game_over.wav'), wave_data)

def create_background_music():
    # Simple background loop
    wave_data = []
    base_freq = 220  # A3
    for _ in range(4):
        for freq in [base_freq, base_freq*1.5, base_freq*1.25, base_freq]:
            wave_data.extend(create_sine_wave(freq, 0.5, volume=0.3))
    save_wave_file(os.path.join(SOUNDS_DIR, 'background.wav'), wave_data)

if __name__ == '__main__':
    os.makedirs(SOUNDS_DIR, exist_ok=True)
    create_coin_sound()
    create_powerup_sound()
    create_level_complete_sound()
    create_game_over_sound()
    create_background_music() 