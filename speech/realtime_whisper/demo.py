from audio_recorder import AudioToTextRecorder
import sys
import time

current_text = ""


def on_transcription_update(text: str):
    """Realtime partial updates"""
    _print_live(text)


def on_transcription_stabilized(text: str):
    """Stabilized segments"""
    _print_live(text, finalize=True)


def _print_live(text: str, finalize: bool = False):
    global current_text
    sys.stdout.write(
        "\r" + text + " " * max(0, len(current_text) - len(text))
    )
    sys.stdout.flush()
    current_text = text
    if finalize:
        sys.stdout.write("\n")
        sys.stdout.flush()
        current_text = ""


def main():
    model_path = "speech/realtime_whisper/models/whisper-small-int8"

    recorder = AudioToTextRecorder(
        model=model_path,
        compute_type="int8",
        language="en",
        beam_size=3,
        enable_realtime_transcription=True,
        realtime_model_type=model_path,
        realtime_processing_pause=0.2,
        post_speech_silence_duration=0.3,
        on_realtime_transcription_update=on_transcription_update,
        on_realtime_transcription_stabilized=on_transcription_stabilized,
        spinner=False,
    )

    print("🎙️ Speak into the microphone (Ctrl+C to stop)...")

    try:
        while True:
            time.sleep(0.1)  # let callbacks run in background
    except KeyboardInterrupt:
        print("\n🛑 Stopping transcription...")
    finally:
        recorder.shutdown()


if __name__ == "__main__":
    main()
