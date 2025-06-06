import os
import subprocess
from fileinput import filename
from pathlib import Path

def convert_audio(input_file, output_file=None, output_format='wav'):
    try:
        allowed_output_formats = {'wav', 'mp3', 'oga'}
        output_format = output_format.lower()

        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")

        if output_format not in allowed_output_formats:
            raise ValueError(f"Unsupported output format: {output_format}. Allowed: {', '.join(allowed_output_formats)}")

        # Set output file name
        input_path = str(Path(input_file))
        if output_file is None:
            output_path, ext = input_path.split('.')
            output_file = output_path + f'.{output_format}'
        else:
            output_file = str(Path(output_file).with_suffix(f'.{output_format}'))

        original_output = output_file
        while os.path.exists(output_file):
            base, ext = os.path.splitext(original_output)
            output_file = f"{base}{ext}"


        # Build ffmpeg command
        ffmpeg_command = ['ffmpeg', '-y', '-i', input_file]

        if output_format == 'wav':
            ffmpeg_command += ['-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1']
        elif output_format == 'mp3':
            ffmpeg_command += ['-codec:a', 'libmp3lame', '-qscale:a', '2']
        elif output_format == 'oga':
            ffmpeg_command += ['-c:a', 'libopus']

        ffmpeg_command.append(output_file)

        # Run conversion
        subprocess.run(ffmpeg_command, check=True)

        print(f"✅ Created new {output_format.upper()} file: {output_file}")
        return output_file

    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {str(e)}")
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg conversion failed: {e}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

    return None
