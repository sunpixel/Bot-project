import os
import subprocess
from pathlib import Path

def convert_oga_to_wav(input_file, output_file=None):
    try:
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")

        if output_file is None:
            input_path = Path(input_file)
            output_file = input_path.with_suffix('.wav').name

        counter = 1
        original_output = output_file
        while os.path.exists(output_file):
            base, ext = os.path.splitext(original_output)
            output_file = f"{base}_{counter}{ext}"
            counter += 1

        subprocess.run([
            'ffmpeg', '-i', input_file,
            '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1',
            output_file
        ], check=True)

        print(f"✅ Created new WAV file: {output_file}")
        return output_file

    except FileNotFoundError as e:
        print(f"Error: {str(e)}")
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg conversion failed: {e}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

    return None
