# -*- coding: utf-8 -*-
"""
Created on Mon Jun 17 14:43:53 2024

@author: Maxime
"""
import re

def maybe_update_agent_interaction(user_text, agent_interaction):
    user_text = user_text.lower()
    new_agent_interaction = agent_interaction
    agent_response = ""
    
    stop_word = "arrêt"
    resume_word = "reprend"
    interact_word = "(dialogue|interaction)"
    stop_response = "Ok j'arrête"
    resume_response = "Ok je reprends"
    
    if agent_interaction:
        if re.search(stop_word, user_text) and re.search(interact_word, user_text):
            new_agent_interaction = False
            agent_response = stop_response
            
    else:
        if re.search(resume_word, user_text) and re.search(interact_word, user_text):
            new_agent_interaction = True
            agent_response = resume_response
    
    return new_agent_interaction, agent_response


def filter_bmls(bmls):
    pattern = r'^<.*?>$'  # Regex pattern to match "< />"
    filtered_bmls = [s for s in bmls if re.match(pattern, s)]
    return filtered_bmls

def extract_bmls_from_agent_response(text):
    # Define the regex pattern to find elements surrounded by asterisks
    pattern = r'\*(.*?)\*'
    # Find all matches
    bmls = re.findall(pattern, text)
    # Replace the matches in the text with an empty string
    agent_speech_text = re.sub(pattern, '', text)
    filtered_bmls = filter_bmls(bmls)
    return agent_speech_text, filtered_bmls
