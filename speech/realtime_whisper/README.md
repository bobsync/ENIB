# Module de speech perception

## Fonctionnement
Ce que dit l'utilisateur est transcrit en texte, le module attend 0.5 seconde (temps configurable)
que la personne ait fini de parler puis envoie les phrases de l'utilisateur sur le topic "USER_FULL_SENTENCE_PERCEPTION"
Exemple : 
USER_FULL_SENTENCE_PERCEPTION:Salut Audrey.

Reçois sur le topic AGENT_PLAYER_STATUS pour savoir si l'agent est en train de parler,
si l'agent est en train de parler le micro est coupé et le module arrête de transcrire l'audio.
Messages de statuts de l'agent que le module reçoit : 
AGENT_PLAYER_STATUS:Audrey:speech on
AGENT_PLAYER_STATUS:Audrey:speech off

Le module utilise la librairie RealtimeSTT : https://github.com/KoljaB/RealtimeSTT, RealtimeSTT utilise la librairie faster-whisper : https://github.com/SYSTRAN/faster-whisper
Le modèle qui est utilisé transcrit de la parole en français : "whisper-small-cv11-french" dans le dossier modèle, il est possible de le changer.

## Autres informations
La librairie RealtimeSTT n'est pas importée depuis l'environnement python, elle est dans le fichier audio_recorder.py, j'ai fait ça, car j'ai modifié le code de la librairie dans audio_recorder.py:
J'ai ajouté la possibilité de changer en temps réel la valeur de post_speech_silence_duration


## Config 
le fichier config.json contient
{
    #nom du périphérique audio ou il y a le micro, le micro plus directionnel est branché sur le canal audio n°7 de la focusrite
    #Lancer le script print_audio_sources.py affiche le nom de toutes les entres audio disponibles
    #Si le nom n'est pas trouvé, c'est le périphérique d'index 0 qui est utilisé
    "input_device_name": "Analogue 7 + 8",
    #le délai que la librairie attend avant de considérer que la personne a fini de parler, après ce délai l'audio et transcrit et le résultat est envoyé au module
    "post_speech_silence_duration": 0.5
}


## Prérequis logiciel
Python 3.10
librairie RealtimeSTT
Suivre les instructions pour qu'elle tourne sur le GPU : https://github.com/KoljaB/RealtimeSTT?tab=readme-ov-file#gpu-support-with-cuda-recommended

## Prérequis matériel
Pour que le micro de l'ACA soit utilisé (le micro plus directionnel), il faut que la table de mixage (la focusrite) soit branchée en USB au PC.

## Changer le modèle
Dans realtime_whisper.py, il y a : self.model_path = "models/whisper-small-cv11-french"
Il est possible de télécharger d'autres modèles sur HiggingFace, soit ils sont déjà compatibles avec faster-whisper, 
soit ils sont compatibles qu’avec Whisper et il faut les convertir : https://github.com/SYSTRAN/faster-whisper?tab=readme-ov-file#model-conversion


## Améliorations possibles
Dans realtime_whisper.py il y a plusieurs paramètres de la librairie de transcription qui peuvent surement être meilleur, notamment la sensibilité de détection,
voir : https://github.com/KoljaB/RealtimeSTT?tab=readme-ov-file#configuration 

## Ajouts possibles
Il est possible de faire un autre module qui envoie les phrases de l'utilisateur à un intervalle régulier même si elles ne se sont pas finies. 
Avec le paramètre "enable_realtime_transcription=True", voir : https://github.com/KoljaB/RealtimeSTT?tab=readme-ov-file#configuration 


