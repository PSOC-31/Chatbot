# chatbot-PS

Ce projet est un assistant vocal interactif développé en Python. Il utilise la reconnaissance vocale hors-ligne et la synthèse vocale pour interagir avec l'utilisateur. Il est capable de :

- Reconnaître des commandes vocales en français
- Répondre oralement via synthèse vocale (Coqui TTS)
- Lire des musiques ou sons aléatoires
- Poser un mini quiz vocal
- Réagir différemment selon l'âge supposé de l'utilisateur (test du bac)

---

## Installation (Raspberry Pi 3 avec environnement virtuel)

### 1. Dépendances système

```bash
sudo apt update
sudo apt install -y mpg123 python3-pip python3-venv python3-dev libasound2-dev build-essential
```

### 2. Cloner le projet

```bash
git clone https://github.com/PSOC-31/Chatbot.git
cd chatbot
```

### 3. Créer et activer un environnement virtuel

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Installer Rust (requis pour certaines dépendances de TTS)

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
```

### 5. Installer les dépendances Python dans l’environnement

```bash
pip install --upgrade pip
pip install vosk sounddevice TTS
```

---

## Lancer l’assistant

Activez l’environnement virtuel si ce n’est pas déjà fait :

```bash
source venv/bin/activate
```

Puis lancez le script (depuis le répertoire /chatbot) :

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
└── venv/                  # Environnement virtuel Python
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

---

## Reconnaissance vocale avec VOSK

Téléchargez le modèle français VOSK ici :  
https://alphacephei.com/vosk/models  
Puis décompressez-le dans `vosk/` (par exemple `vosk/vosk-model-small-fr-0.22`).

---

## Synthèse vocale : Coqui TTS

Le projet utilise la librairie [`TTS`](https://github.com/coqui-ai/TTS) pour parler en français. Le modèle est automatiquement téléchargé au premier lancement.
