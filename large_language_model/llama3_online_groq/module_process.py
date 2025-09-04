# -*- coding: utf-8 -*-
"""
Created on Wed May 15 12:09:23 2024

@author: Maxime
"""

import os
import sys
import json
import time
from groq import Groq

MODULE_FULL_NAME = 'LARGE_LANGUAGE_MODEL/LLAMA3_ONLINE_GROQ'

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


# Config file
config_file_path = 'config.json'
default_config = {}
        
if not os.path.exists(config_file_path):
    # Creation of the default configuration file
    with open(config_file_path, 'w') as config_file:
        json.dump(default_config, config_file, indent=4)

# Reading of the current configuration
with open(config_file_path, 'r') as config_file:
    config = json.load(config_file)
    

# Setup UDP_Client
udp_client = UDPClient(ip_whiteboard)
subscribes = ['LLM_QUERY', 'COMMON']
results_topic = 'LLM_RESPONSE'

for subscribe in subscribes:
    udp_client.send(f'Subscribe:{subscribe}')
    
    
# Setup llm
llm_model = "llama3-8b-8192" #llama3-8b-8192, llama3-70b-8192, mixtral-8x7b-32768, gemma-7b-it
groq_client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

# make sure the API works
test_prompt = [{'role': 'system','content': 'réponds oui'}, {'role': 'user','content': 'oui'}]
chat_completion = groq_client.chat.completions.create(
    messages=test_prompt,
    model=llm_model
)

udp_client.send(f'COMMON:MODULE_SUCCESSFULLY_ACTIVATED:{MODULE_FULL_NAME}')
print("Ready to receive queries")

# Main loop
while True:
    received_messages = udp_client.get_received_messages()  
    if 'COMMON' in received_messages:
        message = received_messages['COMMON']
        if 'REQUEST_MODULE_DEACTIVATION' in message:
            request_module_full_name = message.split(':')[1]
            if MODULE_FULL_NAME == request_module_full_name:
                break #the main loop is exited and the module is closed
    
    if 'LLM_QUERY' in received_messages:
        llm_query = received_messages['LLM_QUERY']
        print(f'{llm_query=}')
        llm_query = json.loads(llm_query)
        
        t0 = time.time()
        chat_completion = groq_client.chat.completions.create(
            messages=llm_query,
            model=llm_model
        )
        llm_response = chat_completion.choices[0].message.content
        print(f'{llm_response=}')
        print(f"Response latency : {time.time()-t0}")
        
        udp_client.send(f'{results_topic}:{llm_response}')

    if (message := received_messages.get("COMMON")):
        if "BROADCAST_REQUEST_SHUTDOWN" in message:
            print("[INFO] Ricevuto broadcast di chiusura. Uscita...")
            udp_client.send(f"COMMON:MODULE_SUCCESSFULLY_DEACTIVATED:{MODULE_FULL_NAME}")
            udp_client.close()
            exit()
    
    time.sleep(0.01)
    
udp_client.send(f'COMMON:MODULE_SUCCESSFULLY_DEACTIVATED:{MODULE_FULL_NAME}')
udp_client.close()  
    
            
