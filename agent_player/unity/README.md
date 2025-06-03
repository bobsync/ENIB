# Modulo Unity

## Funzionamento
È un modulo di tipo agent player, che visualizza l'agente e ne permette l'animazione.
Il software 3D utilizzato è Unity. L'agente è posizionato in una scena 3D che somiglia alla stanza in cui si trova lo schermo.
L'agente viene visualizzato sullo schermo.

Questo modulo riceve messaggi di tipo (topic) BML_COMMAND e AGENT_PLAYER_COMMAND.

AGENT_PLAYER_COMMAND permette di modificare la scena 3D o il funzionamento di Unity.
Esempio per spostare la telecamera in Unity:
AGENT_PLAYER_COMMAND:move_object:Camera:0.269,1.307,1.14
La telecamera dovrebbe spostarsi per seguire la posizioine della testa dell'utente, in modo che l'agente diriga il suo sguardo verso di lui quando richiesto. Questa cosa è visibile in reltà virtuale (3D) ma non su uno schermo 2D.


BML_COMMAND permette di controllare le azioni dell'agente virtuale.
Esempio per far parlare l'agente:
BML_COMMAND:
<bml xmlns="http://www.bml-initiative.org/bml/bml-1.0" xmlns:ext="http://www.bml-initiative.org/bml/coreextensions-1.0" id="14" characterId="Audrey" composition="MERGE">
    <speech id="0" start="0">
        <description priority="0" type="application/ssml+xml">
            <speak>
                Hi! I'm happy to listen to you. My name is Audrey, I am an embodied conversational agent, and I’m glad to see you here.  
				What would you like to talk about?
            </speak>
        </description>
    </speech>
</bml>


version française

# Module Unity

## Fonctionnement
C'est un module de type agent player, c'est un module qui va afficher l'agent et permettre son animation
C'est le logiciel 3D Unity qui est utilisé, l'agent est placé dans une scène 3D qui ressemble à la pièce ou l'écran se trouve
L'agent est affiché sur l'écran

Ce module reçoit des messages de type (topic) BML_COMMAND et AGENT_PLAYER_COMMAND
AGENT_PLAYER_COMMAND permet de modifier la scène 3D ou le fonctionnement de Unity
Exemple pour bouger la caméra dans Unity : 
AGENT_PLAYER_COMMAND:move_object:Camera:0.269,1.307,1.14

BML_COMMAND permet de contrôler ce que fait l'agent virtuel
Exemple pour faire parler l'agent :
BML_COMMAND:
<bml xmlns="http://www.bml-initiative.org/bml/bml-1.0" xmlns:ext="http://www.bml-initiative.org/bml/coreextensions-1.0" id="14" characterId="Audrey" composition="MERGE">
    <speech id="0" start="0">
        <description priority="0" type="application/ssml+xml">
            <speak>
                Salut ! C'est avec plaisir que je puis me mettre à ton écoute. Je m'appelle Audrey, 
                je suis un agent conversationnel animé et je suis ravi de te voir ici. Qu'est-ce que tu veux discuter ?
            </speak>
        </description>
    </speech>
</bml>

## Autres informations
Pour que la perspective soit bonne pour la personne qui regarde l'écran, le frustum de vision de la caméra est positionné
au niveau de l'écran, en réalité il est positionné devant l'écran, mais avec la même perspective pour permettre a l'agent de faire
des gestes vers l'avant et qu'ils soient visibles.
liens utiles pour comprendre le frustum de camera :
https://docs.unity3d.com/Manual/ObliqueFrustum.html
https://docs.unity3d.com/Manual/PhysicalCameras.html
https://discussions.unity.com/t/what-do-the-values-in-the-matrix4x4-for-camera-projectionmatrix-do/188320


Quand la position cible de la caméra est changée via une commande AGENT_PLAYER_COMMAND, la caméra est déplacée vers cette position
avec un certain pourcentage pour que l'animation soit plus fluide.

Le point de coordonnées (0,0,0) est positionné au niveau du milieu bas de l'écran.

## Config

## Prérequis logiciel

## Prérequis matériel
Pour afficher l'agent sur la télévision, il faut brancher l'écran avec le câble HDMI

## Améliorations possibles
Avoir une commande qui fait que Unity consomme moins d'énergie 
une commande qui ressemble à : AGENT_PLAYER_COMMAND:low_power:on
et qui diminue la fréquence de rafraîchissement de Unity.
Voir ce lien : https://bronsonzgeb.com/index.php/2021/10/16/low-power-mode-in-unity/
Faire en sorte que le module se connecte a l'IP de du fichier Ip_whiteboard.txt, et non l'ip du pc
