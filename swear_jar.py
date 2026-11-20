import json, queue, subprocess, sys, threading, time, os
import sounddevice as sd
from vosk import Model, KaldiRecognizer

PROFANITY = {"fuck","shit","ass","bitch","cunt","dick","piss","bastard","crap","damn","dickhead","douche","douchebag","fucker","fucking","motherfucker","motherfucking","bitchass","kite","nigga"
            ,"what the fuck","what the heck","incel"}
MODEL = "vosk-model-small-en-us-0.15"

def log(msg):
    print(msg, flush=True)

def scream():
    log("\n💢💢💢 HEY QUIT FUCKING SWEARING! 💢💢💢\n")
    threading.Thread(target=lambda: subprocess.run(["say","-v","Daniel","-r","200","hey quit fucking swearing"]), daemon=True).start()

def check(text):
    words = {w.strip(".,!?\"'()[]") for w in text.lower().split()}
    if words & PROFANITY:
        scream()

def main():
    log("🚫 Swear Jar — Console Edition")
    log("Loading model…")
    if not os.path.isdir(MODEL):
        log("Downloading model (~50MB)…")
        import urllib.request, zipfile, io
        url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
        with urllib.request.urlopen(url, timeout=90) as r:
            data = r.read()
        zipfile.ZipFile(io.BytesIO(data)).extractall(".")
        log("Model downloaded!")
    model = Model(MODEL)
    rec = KaldiRecognizer(model, 16000)
    q = queue.Queue()
    def callback(indata, frames, ti, status):
        if status: log(f"Audio status: {status}")
        q.put(bytes(indata))
    log("🎙 Listening… Say a test word (try 'what the fuck'). Press Ctrl+C to stop.\n")
    with sd.RawInputStream(samplerate=16000, blocksize=800, dtype="int16", channels=1, callback=callback):
        while True:
            try: data = q.get(timeout=1)
            except queue.Empty: continue
            if rec.AcceptWaveform(data):
                text = json.loads(rec.Result()).get("text","").strip()
                if text:
                    log(f"👉 Heard: {text}")
                    check(text)
            else:
                partial = json.loads(rec.PartialResult()).get("partial","").strip()
                if partial:
                    log(f"… {partial}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("\nStopped.")
        sys.exit(0)
