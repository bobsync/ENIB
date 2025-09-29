# -*- coding: utf-8 -*-
"""
Realtime Whisper con log della latenza essenziale
"""

import customtkinter
import os
import sys
import threading
import time
import pyaudio

from audio_recorder import AudioToTextRecorder

### ------------------ CONFIG ------------------ ###
MODULE_FULL_NAME = 'SPEECH/REALTIME_WHISPER'

### ------------------ UDP Setup ------------------ ###
def get_modules_folder_dir():
    current_dir = os.path.abspath(os.path.dirname(__file__))
    while not os.path.exists(os.path.join(current_dir, 'Modules')):
        current_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
        if current_dir == os.path.abspath(os.sep):
            sys.exit("Le dossier 'Modules' n'a pas été trovato.")
    return os.path.join(current_dir, 'Modules')

modules_folder_dir = get_modules_folder_dir()
sys.path.append(modules_folder_dir)

from UDPClient import UDPClient

ip_whiteboard_file = os.path.join(modules_folder_dir, 'IP_whiteboard.txt')
with open(ip_whiteboard_file, 'r') as txt_file:
    ip_whiteboard = txt_file.read().strip()

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

### ------------------ AUDIO ------------------ ###
def get_index_audio_device(name):
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    for i in range(info.get('deviceCount')):
        if p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels') > 0:
            device_name = p.get_device_info_by_host_api_device_index(0, i).get('name')
            if name in device_name:
                return i
    return 0  # Default device

class SpeechToText:
    def __init__(self, udp_client, config):
        self.model_path = "models/whisper_small_en_ct_float32"
        self.results_topic = "USER_FULL_SENTENCE_PERCEPTION"
        self.udp_client = udp_client
        self.input_device_index = get_index_audio_device(config["input_device_name"])
        self.user_full_sentence = None
        self.last_partial_sent = ""
        self.last_wait_start_ts = 0.0

        self.recorder = AudioToTextRecorder(
            model=self.model_path,
            spinner=False,
            language="en",
            input_device_index=self.input_device_index,
            silero_sensitivity=0.5,
            webrtc_sensitivity=2,
            post_speech_silence_duration=config["post_speech_silence_duration"],
            min_gap_between_recordings=0.2,
            on_vad_detect_start=self.on_user_stop_speaking,
            on_vad_detect_stop=self.on_user_start_speaking,
            enable_realtime_transcription=True,
            on_realtime_transcription_update=self.on_partial_text,
        )

        self.thread = threading.Thread(target=self._listen_for_text, daemon=True)
        self.thread.start()

    # ---- Eventi ----
    def on_user_start_speaking(self):
        self.udp_client.send("USER_STATUS:START_SPEAKING")

    def on_user_stop_speaking(self):
        self.udp_client.send("USER_STATUS:STOP_SPEAKING")

    def on_partial_text(self, text):
        if text != self.last_partial_sent:
            self.last_partial_sent = text
            ts = time.time()
            self.udp_client.send(f"{self.results_topic}_PARTIAL:{text}")

    # ---- Frasi complete ----
    def _listen_for_text(self):
        while True:
            self.last_wait_start_ts = time.time()
            self.recorder.text(on_transcription_finished=self.process_full_sentence)
            time.sleep(0.01)

    def process_full_sentence(self, sentence):
        ts_received = time.time()
        latency_ms = (ts_received - self.last_wait_start_ts) * 1000.0
        sentence = sentence.strip()
        if sentence:
            print(f"[LATENCY: {latency_ms:.1f} ms] FULL SENTENCE: {sentence}")
            self.user_full_sentence = sentence
        else:
            self.user_full_sentence = None

    # ---- Update per GUI ----
    def update(self):
        if self.user_full_sentence:
            s = self.user_full_sentence
            self.udp_client.send(f"{self.results_topic}:{s}")
            self.user_full_sentence = None
            return s
        return None

    def close(self):
        self.recorder.shutdown()

### ------------------ UI ------------------ ###
class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.config = {
            "input_device_name": "Analogue 7 + 8",
            "post_speech_silence_duration": 1.2
        }

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.subscribes = ["AGENT_PLAYER_STATUS", "COMMON"]
        self.udp_client = UDPClient(ip_whiteboard)
        self.stt = SpeechToText(self.udp_client, self.config)

        for subscribe in self.subscribes:
            self.udp_client.send(f"Subscribe:{subscribe}")

        self.title("Realtime Whisper IHM")
        self.geometry("300x200")

        # slider
        self.slider = customtkinter.CTkSlider(
            self, from_=0.1, to=3, number_of_steps=29,
            width=200, height=20,
            command=self.set_post_speech_silence_duration
        )
        self.slider.place(relx=0.5, rely=0.4, anchor=customtkinter.CENTER)
        self.slider.set(self.config['post_speech_silence_duration'])

        self.label = customtkinter.CTkLabel(self, text="")
        self.label.place(relx=0.5, rely=0.2, anchor=customtkinter.CENTER)
        self.label.configure(text=f"post_speech_silence_duration: {round(self.slider.get(), 1)}")

        self.textbox = customtkinter.CTkTextbox(self, width=300, height=100)
        self.textbox.place(relx=0.5, rely=0.7, anchor=customtkinter.CENTER)

        self.udp_client.send(f'COMMON:MODULE_SUCCESSFULLY_ACTIVATED:{MODULE_FULL_NAME}')

        self.after(20, self.update)

    def on_closing(self):
        self.stt.close()
        self.udp_client.send(f'COMMON:MODULE_SUCCESSFULLY_DEACTIVATED:{MODULE_FULL_NAME}')
        self.udp_client.close()
        self.destroy()

    def set_post_speech_silence_duration(self, value):
        value = round(value, 1)
        self.label.configure(text=f"post_speech_silence_duration: {value}")
        self.stt.recorder.set_post_speech_silence_duration(value)

    def update(self):
        received_messages = self.udp_client.get_received_messages()

        if 'COMMON' in received_messages:
            message = received_messages['COMMON']
            if 'REQUEST_MODULE_DEACTIVATION' in message:
                request_module_full_name = message.split(':')[1]
                if MODULE_FULL_NAME == request_module_full_name:
                    self.on_closing()
                    return

        if "AGENT_PLAYER_STATUS" in received_messages:
            message = received_messages['AGENT_PLAYER_STATUS']
            if "speech off" in message:
                self.stt.recorder.set_microphone(True)
            elif "speech on" in message:
                self.stt.recorder.set_microphone(False)

        user_full_sentence = self.stt.update()
        if user_full_sentence:
            self.textbox.delete("0.0", "end")
            self.textbox.insert("0.0", user_full_sentence)

        self.after(20, self.update)

### ------------------ MAIN ------------------ ###
if __name__ == "__main__":
    print(f"[{time.time():.3f}] Application starting...")
    app = App()
    app.mainloop()
    print(f"[{time.time():.3f}] Application exited cleanly.")
