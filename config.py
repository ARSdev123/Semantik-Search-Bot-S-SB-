# config.py
"""
Fichier de configuration centralisé pour l'application Chatbot.

Ce fichier regroupe tous les chemins de fichiers, noms de dossiers et autres 
paramètres constants utilisés à travers l'application. Le but est de faciliter 
la maintenance et d'éviter les valeurs codées en dur dans le reste du code.
"""

import os

# --- Chemins de base ---

# Récupère le chemin absolu du dossier racine du projet.
# os.path.dirname(__file__) donne le chemin du dossier où se trouve config.py.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# --- Dossiers de données ---

# Dossier contenant les documents (PDF, DOCX, TXT) que le bot peut lire.
DATA_DIR = os.path.join(BASE_DIR, 'data')


# --- Fichiers de la base de connaissances et logs ---

# Fichier JSON contenant la base de connaissances principale (intentions, FAQ).
KNOWLEDGE_BASE_FILE = os.path.join(BASE_DIR, 'data.json')

# Fichier JSON pour stocker les statistiques d'utilisation des questions.
STATS_FILE = os.path.join(BASE_DIR, 'stats.json')

# Fichier JSON pour enregistrer l'historique de toutes les interactions avec le bot.
HISTORY_FILE = os.path.join(BASE_DIR, 'historique.json')


# --- Paramètres du modèle de Chatbot ---

# Seuil de similarité pour la recherche de questions approximatives (entre 0.0 et 1.0).
# Utilisé par difflib.get_close_matches.
SIMILARITY_CUTOFF = 0.60

# Taille des "chunks" (morceaux de texte) pour l'analyse TF-IDF. 
# Exprimé en nombre de phrases.
CHUNK_SIZE = 5

# --- Configuration de l'API ---

# Clé d'API secrète pour protéger les endpoints de l'API.
# Remplacez cette valeur par une clé forte et unique en production.
API_KEY = "YOUR_API_KEY"