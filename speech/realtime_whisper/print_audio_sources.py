# -*- coding: utf-8 -*-
"""
Created on Tue Apr 30 17:40:48 2024

@author: enib
"""

import pyaudio

p = pyaudio.PyAudio()
info = p.get_host_api_info_by_index(0)
numdevices = info.get('deviceCount')

for i in range(0, numdevices):
    if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
        print("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))
        

def get_index_audio_device(name):
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    for i in range(0, numdevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            device_name =  p.get_device_info_by_host_api_device_index(0, i).get('name')
            if name in device_name:
                return i
            
    return 0


print(get_index_audio_device("Analogue 7 + 8"))

    