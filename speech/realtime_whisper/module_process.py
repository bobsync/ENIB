# -*- coding: utf-8 -*-
"""
Created on Wed May 15 12:09:23 2024

@author: Maxime
"""

import customtkinter
import json
from realtime_whisper import SpeechToText

import os
import sys

MODULE_FULL_NAME = 'SPEECH/REALTIME_WHISPER'

### To import UDPCLient ###
def get_modules_folder_dir():
    current_dir = os.path.abspath(os.path.dirname(__file__))
    
    while not os.path.exists(os.path.join(current_dir, 'Modules')):
        current_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
        if current_dir == os.path.abspath(os.sep):
            print("Le dossier 'Modules' n'a pas été trouvé.")
            sys.exit(1)
    
    return os.path.join(current_dir, 'Modules')
    
modules_folder_dir = get_modules_folder_dir()
sys.path.append(modules_folder_dir)
from UDPClient import UDPClient

### To have the whiteboard ip ###
ip_witeboard_file = os.path.join(modules_folder_dir, 'IP_whiteboard.txt')
with open(ip_witeboard_file, 'r') as txt_file:
    ip_whiteboard = txt_file.read()


customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__() 
        self.config_file_path = "config.json"
        self.default_config = {
            "input_device_name": "Analogue 7 + 8",
            "post_speech_silence_duration" : 0.4
        }
        
        if not os.path.exists(self.config_file_path):
            # Creation of the default configuration file
            with open(self.config_file_path, 'w') as config_file:
                json.dump(self.default_config, config_file, indent=4)
        
        # Reading of the current configuration
        with open(self.config_file_path, 'r') as config_file:
            self.config = json.load(config_file)
            
        self.subscribes = ["AGENT_PLAYER_STATUS", "COMMON"]
        self.udp_client = UDPClient(ip_whiteboard)
        self.stt = SpeechToText(self.udp_client, self.config)
        for subscribe in self.subscribes:
            self.udp_client.send(f"Subscribe:{subscribe}")
        

        # configure window
        self.title("realtime_whisper_IHM.py")
        self.geometry(f"{300}x{200}")
        
        
        # slider to control post_speech_silence_duration
        self.slider = customtkinter.CTkSlider(self, from_=0.1, to=1, number_of_steps=9,
                                              width=200, height=20,
                                              command=self.set_post_speech_silence_duration)
        self.slider.place(relx=0.5, rely=0.4, anchor=customtkinter.CENTER)
        self.slider.set(self.config['post_speech_silence_duration'])
        
        self.label = customtkinter.CTkLabel(self, text="Slider_value", fg_color="transparent")
        self.label.place(relx=0.5, rely=0.2, anchor=customtkinter.CENTER)
        self.label.configure(text="set_post_speech_silence_duration : "+
                             str(round(self.slider.get(), 1)))
        
        # box to display the user sentences
        self.textbox = customtkinter.CTkTextbox(self, width=300, height=100)
        self.textbox.place(relx=0.5, rely=0.7, anchor=customtkinter.CENTER)

        self.udp_client.send(f'COMMON:MODULE_SUCCESSFULLY_ACTIVATED:{MODULE_FULL_NAME}')
        
        self.after(20, self.update)
        
    def set_post_speech_silence_duration(self, value):
        value = round(value, 1)
        self.label.configure(text=f"set_post_speech_silence_duration : {value}")
        self.stt.set_post_speech_silence_duration(value) 
        
        
    def update(self):
        """ Function executed every 20ms that checks the received messages
        and updates the interface
        """
        received_messages = self.udp_client.get_received_messages()  
        if 'COMMON' in received_messages:
            message = received_messages['COMMON']
            if 'REQUEST_MODULE_DEACTIVATION' in message:
                request_module_full_name = message.split(':')[1]
                if MODULE_FULL_NAME == request_module_full_name:
                    self.destroy() # closes the module
            
        if "AGENT_PLAYER_STATUS" in received_messages:
            message = received_messages['AGENT_PLAYER_STATUS']
            if "speech off" in message:
                print("set microphone on")
                self.stt.recorder.set_microphone(True)
            elif "speech on" in message:
                print("set microphone off")
                self.stt.recorder.set_microphone(False)
                self.stt.clear_pending_sentences()  # <-- QUI

                
        user_full_sentence = self.stt.update()
        if user_full_sentence is not None:
            self.textbox.delete("0.0", "end")
            self.textbox.insert("0.0", user_full_sentence)

        self.after(20, self.update)


if __name__ == "__main__":
    app = App()
    app.mainloop()
    app.stt.close()
    app.udp_client.send(f'COMMON:MODULE_SUCCESSFULLY_DEACTIVATED:{MODULE_FULL_NAME}')
    app.udp_client.close()
    