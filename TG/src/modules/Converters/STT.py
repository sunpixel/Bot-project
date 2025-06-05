import vosk
import json
import wave

class STT:
    def __init__(self, modelpath: str = "model", samplerate: int = 16000):
        self.model = vosk.Model(modelpath)
        self.samplerate = samplerate

    def recognize_file(self, filepath: str):
        try:
            with wave.open(filepath, "rb") as wf:
                if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != self.samplerate:
                    print(f"❌ Audio must be mono, 16-bit PCM at {self.samplerate} Hz.")
                    return ""

                rec = vosk.KaldiRecognizer(self.model, self.samplerate)
                results = []

                while True:
                    data = wf.readframes(4000)
                    if len(data) == 0:
                        break
                    if rec.AcceptWaveform(data):
                        res = json.loads(rec.Result())
                        results.append(res.get("text", ""))

                res = json.loads(rec.FinalResult())
                results.append(res.get("text", ""))

                transcript = " ".join(results).strip()
                print("✅ Recognized text:")
                print(transcript)
                return transcript

        except Exception as e:
            print(f"STT error: {e}")
            return ""
