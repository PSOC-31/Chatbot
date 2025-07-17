# chatbot-PS

Ce projet est un assistant vocal interactif développé en Python. Il utilise la reconnaissance vocale hors-ligne et la synthèse vocale pour interagir avec l'utilisateur. Il est capable de :

- Reconnaître des commandes vocales en français
- Répondre oralement via synthèse vocale (Coqui TTS)
- Lire des musiques ou sons aléatoires
- Poser un mini quiz vocal
- Réagir différemment selon l'âge supposé de l'utilisateur (test du bac)

---

## Installation (Raspberry Pi 3)

### 1. Cloner le projet

```bash
git clone https://github.com/PSOC-31/Chatbot.git
cd chatbot
```

### 2. Dépendances système

```bash
sudo apt update
sudo apt install -y mpg123 libttspico-utils python3-pip python3-sounddevice
```

### 3. Installer les dépendances Python

```bash
pip3 install vosk
```

### 4. Télécharger le modèle Vosk FR

```bash
mkdir -p vosk
cd vosk
wget https://alphacephei.com/vosk/models/vosk-model-small-fr-0.22.zip
unzip vosk-model-small-fr-0.22.zip
rm vosk-model-small-fr-0.22.zip
cd ..
```

### 5. Ajouter des sons et musiques

- Place tes musiques (.mp3) dans sounds/musics/
- Place tes sons aléatoires (.mp3) dans sounds/random/
- Place tes fichiers de réaction dans sounds/ (ex. Au_revoir.mp3, Tes_mauvais.mp3)

### 6. Ajouter les définitions (questions/réponses)

Édite data.json avec des blocs de type :

```json
{
  "bonjour": ["Salut, je suis prêt !"],
  "quiz": [
    {"question": "Quelle est la capitale de la France ?", "réponse": "Paris"}
  ],
  "resultats_quiz": {
    "0": "Aïe, tu peux faire mieux !",
    "1": "Pas mal.",
    "2": "Bravo !",
    "3": "Excellent !"
  }
}
```

---

## Lancer l’assistant

Depuis le répertoire /chatbot

```bash
chmod +x main.py
./main.py
```

---

## Structure du projet

```
chatbot/
├── main.py                # Script principal
├── data.json              # Questions, réponses, quiz...
├── vosk/                  # Modèle de reconnaissance vocale (ex: vosk-model-small-fr-0.22)
├── sounds/
│   ├── musics/            # Musiques aléatoires
│   └── random/            # Sons aléatoires
├── .initialized           # Fichier de contrôle interne
```

---

## Commandes vocales disponibles

- **"Bonjour"** : Réveille l’assistant
- **"Au revoir"** : Le remet en veille
- **"Armageddon"** : Ferme complètement le programme
- **"Quiz"** ou **"questions réponses"** : Lance un quiz vocal
- **"Chanson"** ou **"musique"** : Joue un fichier aléatoire
- **"Son"** : Joue un son court aléatoire
- **"Chut"** : Coupe le son en cours
