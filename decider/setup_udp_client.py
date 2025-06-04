# -*- coding: utf-8 -*-
"""
Created on Wed May 15 15:53:11 2024

@author: Maxime
"""

import os
import sys

### Utilities to locate the root folder of the modules ###
def get_modules_folder_dir():
    """Return the directory containing the available modules configuration."""
    current_dir = os.path.abspath(os.path.dirname(__file__))

    while not os.path.exists(os.path.join(current_dir, 'available_modules.json')):
        parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
        if parent_dir == current_dir:
            print("Le fichier 'available_modules.json' n'a pas été trouvé.")
            sys.exit(1)
        current_dir = parent_dir

    return current_dir
    
modules_folder_dir = get_modules_folder_dir()
sys.path.append(modules_folder_dir)
from UDPClient import UDPClient

### Retrieve the whiteboard IP ###
ip_whiteboard_file = os.path.join(modules_folder_dir, 'IP_whiteboard.txt')
with open(ip_whiteboard_file, 'r') as txt_file:
    ip_whiteboard = txt_file.read()
    

# Setup UDP Client
udp_client = UDPClient(ip_whiteboard)