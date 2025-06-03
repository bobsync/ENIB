# -*- coding: utf-8 -*-
"""
Created on Wed May 15 15:53:11 2024

@author: Maxime
"""

import os
import sys

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
    

# Setup UDP Client
udp_client = UDPClient(ip_whiteboard)