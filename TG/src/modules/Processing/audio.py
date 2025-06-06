import os
import requests
from TG.src.modules.Converters.audio_convert import convert_audio
from TG.src.modules.Converters.STT import STT
from TG.src.modules.Converters.TTS import tts_play
from TG.src.sub_proccess import *


def receive_audio(msg, bot):
    file_info = bot.get_file(msg.audio.file_id if msg.content_type == 'audio' else msg.voice.file_id)
    file_path = file_info.file_path
    # bot.send_message(msg.chat.id, f'{file_info}|||| {file_path}')

    url = f'https://api.telegram.org/file/bot{bot.token}/{file_path}'

    download_dir = os.path.join("TG", "Data", "Downloads")
    os.makedirs(download_dir, exist_ok=True)

    file_id = msg.audio.file_id if msg.content_type == 'audio' else msg.voice.file_id
    if msg.content_type == 'audio' and hasattr(msg.audio, 'file_name') and msg.audio.file_name:
        ext = os.path.splitext(msg.audio.file_name)[1]
    elif msg.content_type == 'voice':
        ext = '.oga'
    else:
        ext = ''

    download_path = os.path.join(download_dir, f"{file_id}{ext}")
    response = requests.get(url)

    with open(download_path, "wb") as f:
        f.write(response.content)

    # Perform conversion to wav format and removes old file

    out_file = os.path.join(download_dir, f"{file_id}.wav")
    file_name = convert_audio(download_path, out_file, 'wav')
    name = file_name.split(sep='/')
    print(name)
    os.remove(download_path)

    # This code runs only after file is created (it is ensured)

    # Models website https://alphacephei.com/vosk/models

    big_model = os.path.join("TG", "Data", "Models", "vosk-model-ru-0.42")
    sml_model = os.path.join("TG", "Data", "Models", "vosk-model-small-ru-0.22")

    stt = STT(modelpath=sml_model)
    speech = stt.recognize_file(out_file)
    process_audio(speech, msg, bot, file_name)


'''
    Audio will be post processed, which will 
    make it possible to call certain commands
    using voice messages and audio files so
    that all users may have the best experience
'''


def process_audio(audio, msg, bot, name):
    if audio == 'старт' or 'начать' or 'привет':
        start_func(msg, bot)
        tts_play('Привет', bot, name=name)
