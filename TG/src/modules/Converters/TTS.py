import os.path

import torch
import sounddevice as sd
import soundfile as sf
from TG.src.modules.Converters.audio_convert import convert_audio

save_path = os.path.join('TG', 'Data', 'Uploads')

device = torch.device('cuda')
model, example_text = torch.hub.load(
    repo_or_dir='snakers4/silero-models',
    model='silero_tts',
    language='ru',
    speaker='ru_v3'
)

def tts_make(text, filename="output.wav"):
    audio = model.apply_tts(text=text, speaker='kseniya', sample_rate=48000)
    # Save as wav file
    wav_path = os.path.join(save_path, filename)
    sf.write(wav_path, audio, 48000)
    oga_file = convert_audio(wav_path, output_format='oga')

    return oga_file