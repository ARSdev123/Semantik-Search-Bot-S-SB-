Rapport des Modifications et Implémentations - Projet Chatbot

============================================================

Ce document résume l'ensemble des changements apportés au projet au cours de notre session.


### 1. Analyse Initiale et Amélioration de l'API

- **Analyse du Projet** : Examen de la structure du code, identification des composants clés (`chatbotcol.py`, `gui.py`, `fastapi_main.py`) et formulation d'un premier avis et de pistes d'amélioration.
- **Documentation Interactive de l'API** : Modification du fichier `fastapi_main.py` pour enrichir la documentation auto-générée par FastAPI. 
    - Ajout de `summary` et de `docstrings` descriptives à tous les endpoints (`/`, `/recherche`, `/documents`, `/upload`).
    - Ajout d'un exemple de requête au modèle Pydantic `QuestionRequest`.


### 2. Implémentation de la Sécurité de l'API

- **Ajout d'une Clé d'API** : Une clé d'API a été ajoutée au fichier `config.py` pour centraliser sa gestion.
- **Protection des Endpoints** : Le fichier `fastapi_main.py` a été modifié pour implémenter un système de sécurité.
    - Une fonction de dépendance (`get_api_key`) a été créée pour vérifier la présence et la validité d'une clé d'API dans l'en-tête de requête `X-API-Key`.
    - Les endpoints `/recherche`, `/documents`, et `/upload` sont désormais protégés et nécessitent une clé d'API valide pour fonctionner.


### 3. Planification d'Évolutions Futures

- **Intégration d'une Base de Données** : Création d'un document `DATABASE_INTEGRATION.md` détaillant la méthode et les avantages de remplacer le stockage par fichiers JSON par une base de données (SQLite avec SQLAlchemy).
- **Recherche Vectorielle** : Création d'un document `VECTOR_SEARCH_IMPLEMENTATION.md` pour planifier le remplacement de la recherche par mots-clés (TF-IDF) par une recherche sémantique.


### 4. Remplacement de TF-IDF par la Recherche Vectorielle

- **Installation des Dépendances** : Ajout des bibliothèques `sentence-transformers` et `faiss-cpu` au projet.
- **Création du Module `vector_store.py`** : Un nouveau module a été créé pour encapsuler la logique de recherche sémantique. La classe `VectorStore` gère :
    - Le chargement du modèle de langage `all-MiniLM-L6-v2`.
    - La création d'un index de recherche FAISS.
    - L'ajout de documents à l'index.
    - La recherche de similarité.
    - La sauvegarde et le chargement de l'index sur le disque.
- **Mise à Jour du Chatbot (`chatbotcol.py`)** : Le fichier principal du chatbot a été profondément remanié.
    - Suppression complète de l'ancienne logique basée sur `TfidfVectorizer`.
    - Intégration du `VectorStore` pour gérer la recherche dans les documents.
    - Mise en place du chargement de l'index au démarrage et de sa sauvegarde lors de l'ajout de nouveaux documents.


### 5. Test et Débogage de la Recherche Vectorielle

- **Création d'un Fichier de Test** : Ajout du fichier `tech_leaders.txt` dans le dossier `/data` avec du contenu sur Sam Altman et Jensen Huang pour permettre des tests concrets.
- **Diagnostic et Correction** : Constat que le bot retournait des réponses trop longues (le document entier).
    - **Cause identifiée** : La taille des "chunks" (morceaux de texte) était trop grande (20 phrases), ce qui faisait que les petits documents n'étaient pas découpés.
    - **Correction** : La valeur de `CHUNK_SIZE` dans `config.py` a été réduite de 20 à 2.
    - **Finalisation** : Suppression des anciens fichiers d'index (`faiss_index.bin`, `faiss_chunks.txt`) pour forcer la ré-indexation des documents avec la nouvelle configuration.

============================================================
