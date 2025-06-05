import torch
import sounddevice as sd

# Download Silero TTS model if not already present
device = torch.device('cpu')
model, example_text = torch.hub.load(
    repo_or_dir='snakers4/silero-models',
    model='silero_tts',
    language='en',
    speaker='v3_en'
)

def tts_play(text):
    # Generate audio
    audio = model.apply_tts(text=text, speaker='en_0', sample_rate=48000)
    # Play audio
    sd.play(audio, 48000)
    sd.wait()

if __name__ == "__main__":
    user_text = input("Enter text to speak: ")
    tts_play(user_text)