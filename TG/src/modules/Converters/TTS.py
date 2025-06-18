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
    #audio = model.apply_tts(text=text, speaker='kseniya', sample_rate=48000)
    audio = model.apply_tts(
        text=text,
        speaker='en_0',  # en_1 is a female voice
        sample_rate=48000
    )
    # Save as wav file
    wav_path = os.path.join(save_path, filename)
    sf.write(wav_path, audio, 48000)
    oga_file = convert_audio(wav_path, output_format='oga')

    return oga_file