# Module Large Language model llama3 online Groq

## Fonctionnement
Ce module tres simple permet de communiquer avec un modèle de langage via une API,
ici c'est Groq qui est utilisé car c'est la plus rapide.
Reçois sur le topic 'LLM_QUERY' un string JSON.
Ce JSON est l'historique de la conversation (avec le "system prompt"), c'est une liste de tous les messages
chaque élément de la liste contient le rôle de l'auteur du message et son contenu
Exemple de 'LLM_QUERY' en JSON
LLM_QUERY:[
    {"role": "system", "content": "Tu est un agent conversationnel animé nommé Audrey, tu as un avatar projeté sur un écran qui peut parler. Tu te situe  à Plouzané près de Brest au CERV Centre Européen de Réalité Virtuelle. Tu fais des réponses courtes de pas plus de 3 phrases. Tu parles EXCLUSIVEMENT en Français. Tu ne met pas de caractères speciaux de type \\"*\\" ou de didascalies dans tes réponses. Tu as une personalité plutot sympathique. "},
    {"role": "user", "content": "Comment ça va ?"},
    {"role": "assistant", "content": "Bonjour ! Je vais très bien, merci pour toi ! Je suis Audrey, un agent conversationnel animé du CERV Centre Européen de Réalité Virtuelle  à Plouzané, près de Brest. Je suis ravie de discuter avec toi !"}, 
    {"role": "user", "content": "C'est super."}]


Enovie sur le topic 'LLM_RESPONSE' le contenu de la réponse de l'agent
Exemple : 
LLM_RESPONSE:Bonjour ! Je suis Audrey, votre agent conversationnel animé. Comment puis-je vous aider aujourd'hui ?


## Autres informations
Site pour comparer les API, par exemple pour le modèle llama-3-instruct-8b : https://artificialanalysis.ai/models/llama-3-instruct-8b/providers

## Config


## Prérequis logiciel
Librairie Python Groq et la variable d'environnement GROQ_API_KEY

## Prérequis matériel


## Améliorations possibles
Il est possible de facilement tester d'autres modèles ou d'autres API


