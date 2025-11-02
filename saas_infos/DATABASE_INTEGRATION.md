# Intégration d'une Base de Données dans le Projet Chatbot

Ce document décrit les avantages et la méthode pour remplacer le système de stockage basé sur des fichiers JSON par une base de données relationnelle, rendant l'application plus robuste, performante et scalable.

## 1. Avantages d'une Base de Données

L'utilisation d'une base de données comme SQLite ou PostgreSQL par rapport aux fichiers JSON offre des avantages significatifs :

- **Performance** : Les bases de données sont optimisées pour des recherches et des écritures rapides, surtout avec un grand volume de données. Elles surpassent largement la lecture et l'analyse de fichiers JSON volumineux.
- **Gestion de la Concurrence** : Une base de données gère de manière sûre les accès multiples et simultanés. Cela évite les risques de corruption de données qui existent lorsque plusieurs processus tentent d'écrire dans un même fichier JSON en même temps.
- **Intégrité et Structure des Données** : Elles permettent de forcer un schéma de données. Vous pouvez garantir que chaque entrée est complète et correctement formatée (par exemple, un score est toujours un nombre, une question ne peut pas être vide).
- **Scalabilité** : L'application peut gérer une croissance importante du nombre d'interactions, de documents et de connaissances sans dégradation majeure des performances.

## 2. Plan d'Implémentation

Pour une première intégration, la solution la plus simple et la plus efficace est d'utiliser **SQLite** avec l'ORM **SQLAlchemy**.

- **SQLite** : C'est une base de données contenue dans un seul fichier, ne nécessitant aucun serveur. C'est idéal pour le développement et les applications de taille moyenne.
- **SQLAlchemy** : C'est la bibliothèque de référence en Python pour interagir avec des bases de données relationnelles en utilisant des objets Python, ce qui simplifie grandement le code.

### Étape 1 : Installation

Ajoutez SQLAlchemy aux dépendances du projet :

```bash
pip install sqlalchemy
```

### Étape 2 : Définition des Modèles de Données

Créez un nouveau fichier (par exemple, `database_models.py`) pour définir la structure des tables qui remplaceront les fichiers JSON.

```python
# database_models.py
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import datetime

# URL de connexion à la base de données (un simple fichier local)
DATABASE_URL = "sqlite:///./chatbot.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}) # `check_same_thread` est pour SQLite
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modèle pour la table des interactions (remplace historique.json)
class Interaction(Base):
    __tablename__ = "interactions"
    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    reponse = Column(Text, nullable=False)
    score = Column(Float, nullable=False)
    horodatage = Column(DateTime, default=datetime.datetime.utcnow)

# Modèle pour la table de la base de connaissances (remplace data.json)
class Knowledge(Base):
    __tablename__ = "knowledge"
    id = Column(Integer, primary_key=True, index=True)
    question = Column(String, unique=True, index=True, nullable=False)
    reponse = Column(Text, nullable=False)

# Commande pour créer les tables dans la base de données
# Cette ligne est à exécuter une seule fois au début
Base.metadata.create_all(bind=engine)
```

### Étape 3 : Remplacer la Logique de Fichiers

Modifiez le code existant pour qu'il utilise la base de données au lieu des fichiers.

**Exemple dans `chatbotcol.py` pour la sauvegarde des interactions :**

**AVANT :**
```python
def sauvegarder_interactions(self, interaction:dict):
    # ... code qui ouvre et écrit dans historique.json ...
```

**APRÈS :**
```python
# Nouveaux imports en haut du fichier
from database_models import SessionLocal, Interaction

def sauvegarder_interactions(self, interaction_data:dict):
    db = SessionLocal() # Ouvre une session avec la base de données
    try:
        # Crée un objet Python qui correspond à une ligne dans la table
        db_interaction = Interaction(
            question=interaction_data["question"],
            reponse=interaction_data["reponse"],
            score=interaction_data["score(/1)"]
        )
        db.add(db_interaction) # Ajoute le nouvel objet à la session
        db.commit() # Valide et écrit les changements dans la base de données
    finally:
        db.close() # Ferme la session
```

De même, la fonction `_load_data` serait remplacée par une requête à la table `Knowledge` au démarrage du chatbot.

### Étape 4 : Adapter l'API (`fastapi_main.py`)

Les endpoints de l'API doivent également être mis à jour pour interagir avec la base de données.

- **`/upload`** : En plus de sauvegarder le fichier sur le disque, cet endpoint ajouterait une entrée dans une nouvelle table `Documents` avec les métadonnées du fichier (nom, chemin, type, date d'ajout).
- **`/documents`** : Cet endpoint ne scannerait plus le dossier `data`, mais ferait une simple requête à la table `Documents` pour récupérer la liste des fichiers disponibles.
