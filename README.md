# chatbot-PS

Ce projet est un assistant vocal interactif développé en Python. Il est capable de reconnaître des commandes vocales en français, de répondre par synthèse vocale, de jouer des musiques/sons, et de lancer un mini quiz vocal.


## Fonctionnalités principales

- Réveil/dormir avec les mots-clés `bonjour` / `au revoir`
- Synthèse vocale avec `pico2wave`
- Reconnaissance vocale locale avec [VOSK](https://alphacephei.com/vosk/)
- Lecture de musiques ou sons aléatoires
- Quiz vocal avec questions/réponses orales
- Réaction spécifique si l'utilisateur a le baccalauréat (gag sonore)


## Lancer l'assistant

Assurez-vous que les dépendances sont installées (voir ci-dessous), puis exécutez :

```bash
python3 assistant_vocal.py
