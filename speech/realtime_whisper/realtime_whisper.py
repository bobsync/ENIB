# -*- coding: utf-8 -*-
"""
Created on Fri May  3 17:27:25 2024

@author: Maxime
"""

from audio_recorder import AudioToTextRecorder

import threading
import pyaudio
import time

def get_index_audio_device(name):
    """ Get the index of an audio device using its name
    if the name is not found, it returns 0 as the index
    """
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    for i in range(0, numdevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            device_name =  p.get_device_info_by_host_api_device_index(0, i).get('name')
            if name in device_name:
                return i
    
    print(f"device named \"{name}\" not found, using device of index 0 instead")
    return 0

class SpeechToText():
    def __init__(self, udp_client, config):
        self.model_path = "models/whisper-small-int8"
        self.results_topic = "USER_FULL_SENTENCE_PERCEPTION"
        self.udp_client = udp_client

        self.input_device_index = get_index_audio_device(config["input_device_name"])
        self.recorder = AudioToTextRecorder(
            model=self.model_path,
            spinner=False,
            language="en",
            input_device_index=self.input_device_index,
            silero_sensitivity=0.5,
            webrtc_sensitivity=2,
            post_speech_silence_duration=config["post_speech_silence_duration"],
            min_gap_between_recordings=0.2,

            # funzionano al contrario, non so perché
            on_vad_detect_start=self.on_user_stop_speaking, 
            on_vad_detect_stop=self.on_user_start_speaking,
            enable_realtime_transcription=True,
            on_realtime_transcription_update=self.on_partial_text
        )

        self.user_full_sentence = None
        self.receive_text_thread = threading.Thread(target=self.receive_full_sentence)
        self.receive_text_thread.daemon = True
        self.receive_text_thread.start()

    # 🔹 Evento: l’utente ha iniziato a parlare
    def on_user_start_speaking(self):
        self.udp_client.send("USER_STATUS:START_SPEAKING")
        print("[DEBUG] Utente ha iniziato a parlare")

    # 🔹 Evento: l’utente ha smesso di parlare
    def on_user_stop_speaking(self):
        self.udp_client.send("USER_STATUS:STOP_SPEAKING")
        print("[DEBUG] Utente ha smesso di parlare")

    # 🔹 Testo parziale in tempo reale
    def on_partial_text(self, text):
        self.udp_client.send(f"USER_PARTIAL:{text}")
        print("[PARZIALE]", text)
        
    def set_post_speech_silence_duration(self, value):
        self.recorder.set_post_speech_silence_duration(value)
        
    def receive_full_sentence(self):
        while True:
            self.recorder.text(self.process_full_sentence)
            time.sleep(0.01)

    def process_full_sentence(self, user_full_sentence):
        user_full_sentence = user_full_sentence.strip()
        if user_full_sentence:
            self.user_full_sentence = user_full_sentence
        else:
            self.user_full_sentence = None  
        
    def update(self):
        """ Is called by the interface update function and sends the new user sentences 
        to others modules
        """
        if self.user_full_sentence is not None:
            user_full_sentence = self.user_full_sentence
            self.udp_client.send(f"{self.results_topic}:{user_full_sentence}")
            self.user_full_sentence = None
            
            return user_full_sentence
        
        return None
            
        
    def close(self):
        self.recorder.shutdown()