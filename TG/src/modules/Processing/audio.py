import os
from TG.src.modules.Converters.audio_convert import convert_audio
from TG.src.modules.Converters.STT import STT
from TG.src.modules.Converters.TTS import tts_make
from TG.src.config_manager import config

async def receive_audio(update, context):
    # Determine if it's audio or voice
    if update.message.audio:
        file = update.message.audio
        ext = os.path.splitext(file.file_name)[1] if file.file_name else ''
        file_id = file.file_id
    elif update.message.voice:
        file = update.message.voice
        ext = '.oga'
        file_id = file.file_id
    else:
        return None, None

    # Download file from Telegram
    download_dir = os.path.abspath(os.path.join(config.data_path, 'Downloads'))
    os.makedirs(download_dir, exist_ok=True)
    download_path = os.path.join(download_dir, f"{file_id}{ext}")

    telegram_file = await context.bot.get_file(file_id)
    await telegram_file.download_to_drive(download_path)

    # Convert to wav
    out_file = os.path.join(download_dir, f"{file_id}.wav")
    print(f"Downloading {file_id} to {out_file}")
    convert_audio(download_path, out_file, 'wav')

    # Speech-to-text
    sml_model = os.path.abspath(os.path.join(config.data_path, "Models", "vosk-model-small-ru-0.22"))
    stt = STT(modelpath=sml_model)
    speech = stt.recognize_file(out_file)

    return speech, f'{file_id}.wav'

async def check_audio(text, update, context, name):
    # Simple voice command recognition
    if text in ['старт', 'начать', 'привет']:
        return tts_make('Привет', filename=name)
    else:
        return None