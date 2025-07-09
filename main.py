#!/usr/bin/env python3
# ──────────────────  assistant_vocal.py  ──────────────────
import os
import json
import queue
import random
import subprocess
from pathlib import Path
import sounddevice as sd
import vosk
import time

# ──────────────── Configuration générale ────────────────
random.seed()                              # graine aléatoire
ROOT          = Path("/home/psoc/chatbot")
MODEL_PATH    = ROOT / "vosk" / "vosk-model-small-fr-0.22"
MUSIC_DIR     = ROOT / "sounds" / "musics"
SOUND_DIR     = ROOT / "sounds" / "random"
DATA_JSON     = ROOT / "data.json"
FAREWELL_MP3  = ROOT / "sounds" / "Au_revoir.mp3"
MAUVAIS_MP3   = ROOT / "sounds" / "Tes_mauvais.mp3"
INIT_FILE = ROOT / ".initialized"
SAMPLE_RATE   = 16_000
INACTIVITY_TIMEOUT = 90  # Durée max d'inactivité avant retour en veille

# ──────────────── États globaux ────────────────
assistant_active = False     # réveille / endort l'assistant
en_ecoute        = True      # pause / play
music_proc       = None
sound_proc       = None
has_bac          = False
has_answered_bac = False

# ──────────────── Utilitaires ────────────────
def speak(text: str) -> None:
    """Synthèse vocale simple basée sur pico2wave + aplay."""
    print(f"[TTS] {text}")
    os.system(f'pico2wave -l=fr-FR -w=/tmp/tts.wav "{text}" && aplay /tmp/tts.wav && rm /tmp/tts.wav')

def play_mp3(path: Path, proc_attr: str) -> None:
    """Lance un mp3 via mpg123 ; arrête l’ancien si besoin."""
    global music_proc, sound_proc
    # arrêter le process existant
    proc = globals()[proc_attr]
    if proc and proc.poll() is None:
        proc.terminate()
    # lancer le nouveau
    globals()[proc_attr] = subprocess.Popen(["mpg123", str(path)])

def random_file(directory: Path) -> Path | None:
    files = [p for p in directory.glob("*.mp3")]
    return random.choice(files) if files else None

def is_audio_playing() -> bool:
    """Retourne True si un son ou une musique est en cours de lecture."""
    return (music_proc and music_proc.poll() is None) or (sound_proc and sound_proc.poll() is None)

# ──────────────── Préparation Vosk ────────────────
if not MODEL_PATH.exists():
    raise SystemExit(f"Modèle Vosk manquant : {MODEL_PATH}")

model    = vosk.Model(str(MODEL_PATH))
rec      = vosk.KaldiRecognizer(model, SAMPLE_RATE)
audio_q  = queue.Queue()

def audio_callback(indata, frames, time, status):
    if status: print(status)
    audio_q.put(bytes(indata))

# ──────────────── Chargement données ────────────────
with DATA_JSON.open(encoding="utf-8") as f:
    definitions: dict[str, list[str]] = json.load(f)

# ──────────────── Exception ────────────────
class AssistantReset(Exception):
    """Exception levée pour réinitialiser l'assistant sans quitter."""
    pass

# ──────────────── Reset ────────────────
def reset_state():
    global assistant_active, en_ecoute, has_bac, has_answered_bac
    global music_proc, sound_proc

    assistant_active = False
    en_ecoute = True
    has_bac = False
    has_answered_bac = False

    for proc in (music_proc, sound_proc):
        if proc and proc.poll() is None:
            proc.terminate()

    music_proc = sound_proc = None

# ──────────────── Quiz ────────────────
def run_quiz():
    questions = definitions.get("quiz", [])
    feedbacks = definitions.get("resultats_quiz", {})

    if len(questions) < 3:
        speak("Désolé, il n'y a pas assez de questions dans le quiz.")
        return

    selected = random.sample(questions, 3)
    score = 0

    for i, q in enumerate(selected, 1):
        speak(f"Question {i} : {q['question']}")
        last_active_time = time.time()

        while True:
            # Vérifie le timeout d'inactivité
            if time.time() - last_active_time > INACTIVITY_TIMEOUT:
                speak("Tu es trop silencieux. On arrête le quiz.")
                raise AssistantReset

            try:
                data = audio_q.get(timeout=1.0)  # attend max 1 seconde
            except queue.Empty:
                continue  # aucune donnée, on continue à attendre

            if rec.AcceptWaveform(data):
                text = json.loads(rec.Result()).get("text", "").lower()
                if not text:
                    continue

                last_active_time = time.time()  # mise à jour uniquement si texte non vide
                print(f"Réponse : {text}")

                if "au revoir" in text or "aurevoir" in text:
                    speak("À bientôt.")
                    play_mp3(FAREWELL_MP3, "sound_proc")
                    raise AssistantReset

                if "armageddon" in text:
                    speak("Arrêt du programme.")
                    if INIT_FILE.exists():
                        INIT_FILE.unlink()
                    raise SystemExit

                if q["réponse"].lower() in text:
                    speak("Bonne réponse !")
                    score += 1
                else:
                    speak(f"Mauvaise réponse. La bonne réponse était {q['réponse']}.")
                break

    feedback = feedbacks.get(str(score), "Merci d'avoir joué !")
    speak(f"Tu as obtenu {score} point{'s' if score > 1 else ''}. {feedback}")

    if score == 0 and has_bac:
        play_mp3(MAUVAIS_MP3, "sound_proc")

# ──────────────── Boucle principale ────────────────
def listen_and_respond():
    global assistant_active, en_ecoute, has_bac, has_answered_bac
    global music_proc


    if not INIT_FILE.exists():
        speak("Assistant initialisé avec succès.")
        INIT_FILE.touch()

    print("Assistant prêt. Dites « bonjour » pour le réveiller (ou « armageddon » pour quitter).")

    with sd.RawInputStream(samplerate=SAMPLE_RATE,
                           blocksize=8000,
                           dtype='int16',
                           channels=1,
                           callback=audio_callback):

        # Boucle de réveil
        while not assistant_active:
            data = audio_q.get()
            if not rec.AcceptWaveform(data):
                continue
            text = json.loads(rec.Result()).get("text", "").lower()
            if not text:
                continue
            print(f"> {text}")

            if "armageddon" in text:
                speak("Arrêt du programme.")
                if INIT_FILE.exists():
                    INIT_FILE.unlink()
                return

            if "au revoir" in text or "aurevoir" in text:
                speak("À bientôt.")
                play_mp3(FAREWELL_MP3, "sound_proc")
                return

            if "bonjour" in text:
                speak(random.choice(definitions["bonjour"]))
                assistant_active = True

        # Pose obligatoire de la question du bac
        while not has_answered_bac:
            speak("As-tu ton baccalauréat ? Réponds par oui ou non.")

            # Boucle d'écoute jusqu’à une phrase complète
            while True:
                data = audio_q.get()
                if not rec.AcceptWaveform(data):
                    continue
                bac_text = json.loads(rec.Result()).get("text", "").lower()
                if not bac_text:
                    continue
                print(f"> {bac_text}")

                if "oui" in bac_text:
                    has_bac = True
                    has_answered_bac = True
                    speak("Très bien, commençons.")
                    break
                elif "non" in bac_text:
                    has_bac = False
                    has_answered_bac = True
                    speak("Pas de souci, tu peux quand même jouer.")
                    break
                elif "armageddon" in bac_text:
                    speak("Arrêt du programme.")
                    if INIT_FILE.exists():
                        INIT_FILE.unlink()
                    raise SystemExit
                elif "au revoir" in bac_text or "aurevoir" in bac_text:
                    speak("À bientôt.")
                    play_mp3(FAREWELL_MP3, "sound_proc")
                    raise AssistantReset
                else:
                    speak("Je n'ai pas compris.")
                    # Repose la question dans la boucle externe
                    break


        # Boucle principale
        last_active_time = time.time()
        while True:
            # Met à jour le timer si une musique ou un son vient de se terminer
            for proc_name in ("music_proc", "sound_proc"):
                proc = globals()[proc_name]
                if proc and proc.poll() is not None:  # processus terminé
                    globals()[proc_name] = None       # nettoyage
                    last_active_time = time.time()    # mise à jour du timer

            # Réinitialise si aucune activité pendant 90 secondes
            if not is_audio_playing() and time.time() - last_active_time > INACTIVITY_TIMEOUT:
                speak("Aucune activité détectée. Je retourne en veille.")
                raise AssistantReset


            data = audio_q.get()
            if not rec.AcceptWaveform(data):
                continue

            text = json.loads(rec.Result()).get("text", "").lower()
            if not text:
                continue

            print(f"> {text}")

            # ---------- Priorité : armageddon ou chut pendant la musique ----------
            if music_proc and music_proc.poll() is None:
                if "armageddon" in text:
                    proc = music_proc
                    if proc and proc.poll() is None:
                        proc.terminate()
                        music_proc = None
                        
                    speak("Arrêt du programme.")
                    if INIT_FILE.exists():
                        INIT_FILE.unlink()
                    break

                if "chut" in text:
                    proc = music_proc
                    if proc and proc.poll() is None:
                        proc.terminate()
                        music_proc = None
                    continue

                # Toute autre commande est ignorée pendant la musique
                continue

            # ---------- Activité vocale normale ----------
            last_active_time = time.time()



            # ---------- commandes système ----------
            if "armageddon" in text:
                speak("Arrêt du programme.\n")
                if INIT_FILE.exists():
                    INIT_FILE.unlink()
                break

            if "pause" in text and assistant_active:
                en_ecoute = False
                speak("Mise en pause.")
                continue

            if "play" in text and assistant_active and not en_ecoute:
                en_ecoute = True
                speak("Reprise.")
                continue

            if "chut" in text:
                for proc_name in ("music_proc", "sound_proc"):
                    proc = globals()[proc_name]
                    if proc and proc.poll() is None:
                        proc.terminate()
                        globals()[proc_name] = None
                continue
            # ----------------------------------------

            if not en_ecoute:
                continue  # en pause, on ignore le reste

            # ---------- actions audio ----------
            if "chanson" in text or "musique" in text:
                if path := random_file(MUSIC_DIR):
                    play_mp3(path, "music_proc")
                    last_active_time = time.time()
                else:
                    speak("Aucune musique trouvée.")
                continue

            if "son" in text:
                if path := random_file(SOUND_DIR):
                    play_mp3(path, "sound_proc")
                    last_active_time = time.time()
                else:
                    speak("Aucun son trouvé.")
                continue
            # -------------------------------------

            if "questions réponses" in text or "quiz" in text:
                run_quiz()
                last_active_time = time.time()
                continue

            if "au revoir" in text or "aurevoir" in text:
                play_mp3(FAREWELL_MP3, "sound_proc")
                speak("À bientôt.")
                raise AssistantReset

            # ---------- réponses aux mots‑clés ----------
            words = text.split()
            bigrams = {" ".join(words[i:i+2]) for i in range(len(words)-1)}

            for key, replies in definitions.items():
                if key == "bonjour":  # déjà géré
                    continue
                if key in text or key in bigrams:
                    speak(random.choice(replies))
                    break
            # --------------------------------------------

if __name__ == "__main__":
    try:
        while True:
            try:
                listen_and_respond()          # boucle interne
            except AssistantReset:
                reset_state()                 # remet tout à zéro
                print("\n--- Assistant réinitialisé ---")
                continue                      # repart du début
            break                              # on sort si listen_and_respond termine normalement
    except KeyboardInterrupt:
        play_mp3(FAREWELL_MP3, "sound_proc")
        if INIT_FILE.exists():
            INIT_FILE.unlink()
        print("\nFin du programme.")
