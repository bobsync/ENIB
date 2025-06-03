# Module Whiteboard

## Fonctionnement
C'est un bus de donnes qui fonctionne comme un broker de messages
Il s'occupe de recevoir les messages des modules et de les redistribuer aux modules abonnés aux topics

Pour s'abonner à un topic, un module va envoyer un message "Subcribe:"
Par exemple pour s'abonner au topic VISUAL_FEATURES_PERCEPTION :
Subscribe:VISUAL_FEATURES_PERCEPTION
Ensuite le module recevra les messages de ce topic
Pour envoyer un message sur un topic, il suffit d'envoyer par exemple sur le topic USER_FULL_SENTENCE_PERCEPTION :
USER_FULL_SENTENCE_PERCEPTION:C'est super.

## Autres informations
Le module est en C++ et on utilise Visual Studio pour modifier le code

## Config

## Prérequis logiciel
Visual Studio

## Prérequis matériel

## Améliorations possibles