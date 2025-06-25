import os.path

import torch
import soundfile as sf
from TG.src.modules.Converters.audio_convert import convert_audio
from TG.src.config_manager import config

save_path = os.path.abspath(os.path.join(config.data_path, 'Uploads'))

device = torch.device('cuda')
model, example_text = torch.hub.load(
    repo_or_dir='snakers4/silero-models',
    model='silero_tts',
    language='en',
    speaker='v3_en'
)

def tts_make(text, filename="output.wav"):

    print('Entered TTS')
    base_name = os.path.splitext(filename)[0]
    wav_path = os.path.join(save_path, base_name + ".wav")
    oga_path = os.path.join(save_path, base_name + ".oga")

    audio = model.apply_tts(
        text=text,
        speaker='en_0',  # en_1 is a female voice
        sample_rate=48000
    )
    sf.write(wav_path, audio, 48000)

    # Convert wav to oga, ensure output path is used
    convert_audio(wav_path, oga_path, output_format='oga')

    # Ensure oga_path is a valid file path and exists
    if os.path.isfile(oga_path):
        return oga_path
    else:
        print(f"TTS: Output file not found or invalid: {oga_path}")
        return None