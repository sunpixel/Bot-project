# Telegram Bot Project

This repository contains a modular Telegram bot built with Python. The bot supports audio message processing, speech-to-text, text-to-speech, and interactive chat features. It is designed for extensibility and easy integration with machine learning models.

## Features

- **Audio Message Handling:**  
  Converts incoming audio and voice messages to text, processes commands, and can reply with generated voice messages.

- **Speech Recognition & Synthesis:**  
  Uses Vosk for speech-to-text and Silero TTS for text-to-speech in Russian.

- **Interactive Keyboard:**  
  Provides reply and inline keyboards for user interaction.

- **Photo Handling:**  
  Responds to photo messages with inline buttons for editing or deleting.

- **ML Integration:**  
  Includes modules for embedding-based and hybrid ML question answering.

## Project Structure

```
TG/
  src/
    main.py                # Main bot logic and handlers
    sub_proccess.py        # Audio processing and utility functions
    modules/
      Processing/
        audio.py           # Audio download, conversion, and STT
        ML_Embeded.py      # Embedding-based QA
        ML_Hybrid.py       # Hybrid ML QA
      Converters/
        audio_convert.py   # Audio format conversion
        STT.py             # Speech-to-text (Vosk)
        TTS.py             # Text-to-speech (Silero)
  Data/
    Downloads/             # Temporary audio downloads
    Uploads/               # Generated audio uploads
    Models/                # ML and STT/TTS models
    ML/
      QA_Base_en.json      # Example QA data
```

## Requirements

- Python 3.13+
- [pyTelegramBotAPI (telebot)](https://github.com/eternnoir/pyTelegramBotAPI)
- [Vosk](https://alphacephei.com/vosk/)
- [Silero TTS](https://github.com/snakers4/silero-models)
- [SentenceTransformers](https://www.sbert.net/)
- [faiss](https://github.com/facebookresearch/faiss)
- [transformers](https://github.com/huggingface/transformers)
- ffmpeg (for audio conversion)

## Setup

1. **Clone the repository**
2. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```
3. **Download and place models:**
   - Vosk models in `TG/Data/Models/`
   - Silero TTS and ML models as described in the respective modules
4. **Configure your Telegram bot token** in `main.py`
5. **Run the bot:**
   ```
   python TG/src/main.py
   ```

## Usage

- Send audio or voice messages to the bot for processing.
- Use `/start` to initialize the bot and display the main menu.
- Interact with reply and inline keyboards for navigation and actions.

## Notes

- Audio files are temporarily stored and cleaned up after processing.
- The bot does not retain chat history for privacy reasons.
- For ML QA, update `QA_Base_en.json` with your own data.

## License

MIT License

```
MIT License

Copyright (c) 2025 SunPixel

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

**Developed by SunPixel.**  
For questions or support, open an issue or contact via Telegram.