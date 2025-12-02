import pvporcupine
import pyaudio
import struct
import sys
import os
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE = os.path.join(BASE_DIR, 'config', '.env')

PICOVOICE_ACCESS_KEY = "TVUJ_PICOVOICE_ACCESS_KEY_TADY"
WAKE_WORD_MODEL_PATH = os.path.join(BASE_DIR, 'models', 'porcupine', 'Hey_Chronos_raspberry-pi.ppn')
OUTPUT_FILENAME = os.path.join(BASE_DIR, 'audio', 'user_query.wav')

CHANNELS = 1
SAMPLE_RATE = pvporcupine.Porcupine.sample_rate
FRAME_LENGTH = pvporcupine.Porcupine.frame_length


# --- Phase 1: Initialization ---

def init_engines():
    """Initializations Porcupine for the Wake-Word and PyAudio for the microphone."""
    porcupine = None
    pa = None

    try:
        if not os.path.exists(WAKE_WORD_MODEL_PATH):
            print(f"Error: Model for Wake-Word wasnt found on the path: {WAKE_WORD_MODEL_PATH}")
            sys.exit(1)

        porcupine = pvporcupine.Porcupine(
            access_key=PICOVOICE_ACCESS_KEY,
            keyword_paths=[WAKE_WORD_MODEL_PATH]
        )
        print("Porcupine engine initializated and ready for listening.")

        pa = pyaudio.PyAudio()
        audio_stream = pa.open(
            rate=SAMPLE_RATE,
            channels=CHANNELS,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=FRAME_LENGTH
        )
        print("Audio stream from microphone OPEN.")
        return porcupine, pa, audio_stream

    except Exception as e:
        print(f"Critical error in initialization: {e}")
        if porcupine: porcupine.delete()
        if pa: pa.terminate()
        sys.exit(1)


# --- Phase 2: Active recording of question ---

def record_query(pa, audio_stream):
    RECORDING_TIMEOUT_SECONDS = 5

    print(">> Active listening... Speak. (max 5 seconds)")
    frames = []

    for i in range(0, int(SAMPLE_RATE / FRAME_LENGTH * RECORDING_TIMEOUT_SECONDS)):
        try:
            data = audio_stream.read(FRAME_LENGTH)
            frames.append(data)
        except IOError:
            pass

    print(f">> Nahrávání dokončeno. Soubor uložen do {OUTPUT_FILENAME}")

    return OUTPUT_FILENAME


# --- Fáze 3: Spuštění AI Jádra ---

def handle_ai_core(audio_file_path):
    print("\n--- Spouštím AI Jádro ---")

    transcribed_text = f"Simulovaný text od Leoparda z {time.time()}"

    print(f"Přepsaný dotaz: '{transcribed_text}'")

    response_text = "Simulovaná odpověď od Ollamy. Tohle je testovací zpráva, která ověří, že Orca funguje."

    print(f"Chronos replies: '{response_text}'")

    print("--- AI core done ---\n")


def main_loop():
    """Main cycle, which listens on Wake-Word."""
    porcupine, pa, audio_stream = init_engines()

    print("\n[CHRONOS IS ONLINE] Listening on 'Hey Chronos'...")

    try:
        while True:
            pcm_chunk = audio_stream.read(FRAME_LENGTH, exception_on_overflow=False)
            pcm_data = struct.unpack_from("h" * FRAME_LENGTH, pcm_chunk)

            keyword_index = porcupine.process(pcm_data)

            if keyword_index >= 0:
                print("====================================")
                print(">> DETECTED: HEY CHRONOS! <<")
                print("====================================")

                recorded_file = record_query(pa, audio_stream)

                handle_ai_core(recorded_file)

                print("[CHRONOS IS ONLINE] Continues in listening of Wake-Word...")

    except KeyboardInterrupt:
        print("\n\nTurning off Chronos. Bye!")

    finally:
        if porcupine: porcupine.delete()
        if audio_stream: audio_stream.close()
        if pa: pa.terminate()


if __name__ == "__main__":
    main_loop()