# Implémentation de la Recherche Vectorielle (Sémantique)

Ce document détaille le plan de migration du système de recherche actuel, basé sur les mots-clés (TF-IDF), vers un système de recherche sémantique avancé utilisant `sentence-transformers` et `FAISS`.

## 1. Pourquoi la Recherche Vectorielle ?

La recherche vectorielle est une technologie de pointe qui offre des avantages majeurs par rapport à une recherche par mots-clés classique :

- **Compréhension du Sens** : Au lieu de simplement chercher des mots identiques, la recherche sémantique comprend le *sens* de la question. Par exemple, la question "*Comment faire pour prendre des vacances ?*" pourra trouver une réponse dans un document qui parle de "*procédure de demande de congés*", même si les mots sont différents.
- **Pertinence Accrue** : Les résultats sont bien plus pertinents car ils sont basés sur la similarité contextuelle et sémantique, et non sur le simple partage de mots-clés.
- **Robustesse aux Variations** : Le système est moins sensible aux fautes de frappe, aux synonymes et aux différentes manières de formuler une même question.

## 2. Technologies Proposées

- **`sentence-transformers`** : Une bibliothèque Python qui permet de calculer des "embeddings" de phrases, c'est-à-dire des représentations vectorielles (une liste de nombres) qui capturent leur sens sémantique. Nous utiliserons le modèle `all-MiniLM-L6-v2`, qui offre un excellent équilibre entre performance et légèreté.
- **`faiss-cpu`** : (Facebook AI Similarity Search) Une bibliothèque développée par Facebook pour effectuer des recherches de similarité ultra-rapides parmi des millions de vecteurs. La version CPU est plus simple à installer.

## 3. Plan d'Implémentation

### Étape 1 : Installation des Dépendances

Il faudra ajouter les nouvelles bibliothèques au projet :

```bash
pip install sentence-transformers faiss-cpu
```

### Étape 2 : Création d'un Module de Recherche Vectorielle (`vector_store.py`)

Pour garder le code propre, nous allons encapsuler toute la logique de recherche dans un nouveau fichier. Ce module aura une classe `VectorStore` responsable de :
1.  Charger le modèle `sentence-transformers`.
2.  Créer et gérer un index FAISS.
3.  Convertir des morceaux de texte en vecteurs et les ajouter à l'index.
4.  Prendre une question, la convertir en vecteur, et trouver les textes les plus similaires dans l'index.

```python
# vector_store.py
import faiss
from sentence_transformers import SentenceTransformer
import numpy as np
import os

class VectorStore:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        self.index = faiss.IndexFlatL2(self.dimension)
        self.chunks = []

    def add_documents(self, text_chunks):
        """Convertit les chunks de texte en vecteurs et les ajoute à l'index FAISS."""
        embeddings = self.model.encode(text_chunks, convert_to_tensor=False)
        self.index.add(np.array(embeddings))
        self.chunks.extend(text_chunks)
        print(f"{len(text_chunks)} chunks ajoutés à l'index.")

    def search(self, query, k=3):
        """Recherche les k chunks les plus similaires à la question."""
        if self.index.ntotal == 0:
            return []
        query_embedding = self.model.encode([query])
        distances, indices = self.index.search(np.array(query_embedding), k)
        # Retourne les chunks correspondants aux indices trouvés
        return [self.chunks[i] for i in indices[0] if i < len(self.chunks)]

    def save_index(self, index_path, chunks_path):
        """Sauvegarde l'index FAISS et les chunks de texte."""
        faiss.write_index(self.index, index_path)
        with open(chunks_path, 'w', encoding='utf-8') as f:
            for chunk in self.chunks:
                f.write(chunk + '\n')

    def load_index(self, index_path, chunks_path):
        """Charge un index FAISS et les chunks de texte depuis le disque."""
        if os.path.exists(index_path) and os.path.exists(chunks_path):
            self.index = faiss.read_index(index_path)
            with open(chunks_path, 'r', encoding='utf-8') as f:
                self.chunks = [line.strip() for line in f.readlines()]
            print("Index et chunks chargés depuis le disque.")
```

### Étape 3 : Intégration dans le Chatbot (`chatbotcol.py`)

Nous allons modifier `chatbotcol.py` pour qu'il utilise notre nouveau `VectorStore`.

- **Remplacer TF-IDF** : L'initialisation et l'utilisation de `TfidfVectorizer` seront complètement supprimées.
- **Initialiser le VectorStore** : Au démarrage, le chatbot créera une instance de `VectorStore` et chargera l'index s'il existe.
- **Mettre à jour la recherche** : La méthode `_repondre_docs` appellera `vector_store.search()` au lieu de `extraire_passage_tfidf()`.

**Exemple de modification dans `_repondre_docs` :**

**AVANT :**
```python
def _repondre_docs(self, message_original, message_nettoye):
    # ...
    passage_pertinent = self.extraire_passage_tfidf(self.document_content, message_original)
    # ...
```

**APRÈS :**
```python
def _repondre_docs(self, message_original, message_nettoye):
    # self.vector_store est initialisé dans le __init__ du chatbot
    passages_similaires = self.vector_store.search(message_original, k=1)
    if passages_similaires:
        return passages_similaires[0] # On retourne le plus pertinent
    return None
```

### Étape 4 : Persistance de l'Index

Pour éviter de devoir ré-indexer tous les documents à chaque redémarrage du chatbot, nous utiliserons les méthodes `save_index` et `load_index`.

- Au démarrage du chatbot, on essaiera de charger un index existant.
- Lorsque de nouveaux documents sont ajoutés via l'API (`/upload`), on les ajoutera à l'index en mémoire.
- On pourrait ajouter une commande ou un mécanisme pour sauvegarder l'index périodiquement ou à l'extinction du programme.

```
