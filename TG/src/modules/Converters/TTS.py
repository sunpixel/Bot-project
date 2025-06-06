import torch
import torchaudio
import sounddevice as sd
import os
from pathlib import Path

# from TG.src.modules.Converters.audio_convert import convert_audio  # Uncomment if needed

# Set device automatically
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Load Silero TTS model
model = None
example_text = None


def load_model():
    global model, example_text
    model, example_text = torch.hub.load(
        repo_or_dir='snakers4/silero-models',
        model='silero_tts',
        language='ru',
        speaker='ru_v3'
    )
    model.to(device)


# Directory to save audio files
save_path = Path("TG") / "Data" / "Uploads"
save_path.mkdir(parents=True, exist_ok=True)


def tts_play(text, filename_prefix="tts_output", play_audio=False):
    """Generate TTS audio and save as WAV file.

    Args:
        text: Text to convert to speech
        filename_prefix: String prefix for the output file
        play_audio: Whether to play the audio immediately
        bot: (Optional) Telegram bot instance
        chat_id: (Optional) Chat ID for unique filenames
    """
    # Ensure model is loaded
    if model is None:
        load_model()

    # Generate unique filename

    filename = save_path / f"{filename_prefix}_{unique_id}.wav"

    try:
        # Generate audio
        sample_rate = 48000
        audio = model.apply_tts(
            text=text,
            speaker='kseniya',
            sample_rate=sample_rate,
            put_accent=True,
            put_yo=True
        )

        # Convert to proper tensor format
        tensor_audio = audio.detach().clone().unsqueeze(0) if torch.is_tensor(audio) \
            else torch.tensor(audio).unsqueeze(0)

        # Save audio file
        torchaudio.save(
            str(filename),
            tensor_audio,
            sample_rate,
            format='wav'
        )
        print(f"Audio saved to {filename}")

        # Play audio if requested
        if play_audio:
            audio_data = audio.numpy() if torch.is_tensor(audio) else audio
            sd.play(audio_data, sample_rate)
            sd.wait()

        return filename