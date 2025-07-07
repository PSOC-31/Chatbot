# chatbot-PS

Ce projet est un assistant vocal interactif développé en Python. Il est capable de reconnaître des commandes vocales en français, de répondre par synthèse vocale, de jouer des musiques/sons, et de lancer un mini quiz vocal.


## Fonctionnalités principales

- Réveil/dormir avec les mots-clés `bonjour` / `au revoir`
- Synthèse vocale avec `pico2wave`
- Reconnaissance vocale locale avec [VOSK](https://alphacephei.com/vosk/)
- Lecture de musiques ou sons aléatoires
- Quiz vocal avec questions/réponses orales
- Réaction spécifique (gag sonore) si l'utilisateur est jeune ou non (test du baccalauréat) pour ne pas l'affecter mentalement


## Lancer l'assistant

Assurez-vous que les dépendances sont installées (voir ci-dessous), puis exécutez la commande bash


## Dépendances

sudo apt install mpg123 libttspico-utils
pip install vosk sounddevice


```bash
python3 main.py
