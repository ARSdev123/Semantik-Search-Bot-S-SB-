import json  # lib de gestion des fichiers json
import os  #lib de gestion des modifications systeme
from datetime import datetime # gestion des dates
import random # lib de gestion des choix aléatoires
import difflib # lib de gestion des similarités de chaînes
import unicodedata # lib de gestion des caractères unicode
import re # lib de gestion des expressions régulières
import config # Importation de la configuration centralisée contenue dans le fichier config.py

# Gestion des imports avec gestion d'erreurs
MODULES_MANQUANTS = []
#ici, chacune des bibliothèques externes utilisées est importée dans un bloc try-except
#pour capturer les erreurs d'importation et enregistrer les modules manquants.
try:
    import docx # bibliothèque pour la manipulation des fichiers Word
except ImportError:
    MODULES_MANQUANTS.append("python-docx")
    docx = None

try:# Utilisation des conceptes de Machine Learning pour le traitement du langage naturel
    from sklearn.feature_extraction.text import TfidfVectorizer # bibliothèque pour le traitement du langage naturel et l'extraction de caractéristiques TF-IDF(Term Frequency-Inverse Document Frequency)
except ImportError:
    MODULES_MANQUANTS.append("scikit-learn")
    TfidfVectorizer = None

try:
    import fitz # bibliothèque PyMuPDF pour la manipulation des fichiers PDF
except ImportError:
    MODULES_MANQUANTS.append("PyMuPDF")
    fitz = None

try:
    import spacy # bibliothèque pour le traitement avancé du langage naturel
except ImportError:
    MODULES_MANQUANTS.append("spacy")
    spacy = None
#un message d'avertissement est affiché si des modules sont manquants, le message comportant la liste des modules non disponibles.
if MODULES_MANQUANTS:
    print(f"Attention: Modules manquants détectés: {', '.join(MODULES_MANQUANTS)}")

# Classe principale du chatbot(celle ci gere la logique de traitement des questions et des réponses)
class Chatbot:
    def __init__(self):
        #--- Chargement des données de la base de connaissances ---
        self.intents, self.knowledge_base = self._load_data(config.KNOWLEDGE_BASE_FILE, is_base=True)
        #
        self.question_en_attente = None
        #objet pour le chargement et le stockage des statistiques
        self.statistiques_questions = self._load_stats()
        #objet pour stocker le contenu des documents chargés
        self.document_content = ""
        # --- Initialisation de SpaCy ---
        if spacy is not None:
            try:
                self.nlp = spacy.load("fr_core_news_sm")
            except OSError:
                print("Modèle SpaCy non trouvé.")
                self.nlp = None
        else:
            self.nlp = None

        # --- Logique TF-IDF ---

        # objet pour le vectoriseur TF-IDF
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2)) if TfidfVectorizer else None
        # matrice des documents
        self.doc_matrix = None
        # liste des chunks de documents
        self.doc_chunks = []

        # ---------------------

        """
        ici nous avons la premiere partie de la logique qui traites les questions de la base de connaissances
        et des documents. La méthode _load_data charge les intentions et la base de connaissances à partir d'un fichier JSON
        spécifié dans config.KNOWLEDGE_BASE_FILE. Les statistiques des questions sont également chargées à partir d'un fichier de statistiques.
        
        """
        # Charger les documents depuis le dossier de données a partir de config.py
        self.charger_documents(config.DATA_DIR)
    # Méthodes internes pour le chargement des données et la gestion des réponses
    def _load_data(self, fichier, is_base=False):
        if not os.path.exists(fichier):#on verifie si le fichier existe
            with open(fichier, "w", encoding="utf-8") as f:
                json.dump({} if not is_base else {"intents": {}, "knowledge_base": {}}, f) #si le fichier n'existe pas, on le crée avec une structure vide appropriée
        with open(fichier, "r", encoding="utf-8") as f:
            data = json.load(f)
        if is_base: #si c'est la base de connaissances, on charge les intentions et la base de connaissances
            intents = {intent: [self.nettoyer_message(phrase) for phrase in phrases] for intent, phrases in data.get("intents", {}).items()}
            #dans la base de connaissances, chaque clé est nettoyée avant d'être stockée
            knowledge_base = {self.nettoyer_message(k): v for k, v in data.get("knowledge_base", {}).items()}
            return intents, knowledge_base 
        else:
            return {self.nettoyer_message(k): v for k, v in data.items()}
    # Méthodes pour la gestion des statistiques
    def _load_stats(self):
        if not os.path.exists(config.STATS_FILE): #si le fichier de statistiques n'existe pas, on le crée avec une structure vide
            with open(config.STATS_FILE, "w", encoding="utf-8") as f:
                json.dump({}, f)
        with open(config.STATS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    #cette methode sauvegarde les statistiques mises à jour dans le fichier de statistiques
    def _save_stats(self):
        with open(config.STATS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.statistiques_questions, f, ensure_ascii=False, indent=4)
    #celle ci s'occupe de l'incrémentation du compteur pour une question donnée
    def _increment_stat(self, question):
        self.statistiques_questions[question] = self.statistiques_questions.get(question, 0) + 1
        self._save_stats()

    """
    Ici, nous sommes dans la deuxième partie de la logique du chatbot.
    celle ci concerne le traitement des messages, la gestion des documents, et la génération des réponses.
    On trouve des méthodes pour nettoyer les messages, découper les documents en chunks,
    extraire des passages pertinents à l'aide de TF-IDF, et répondre aux questions en utilisant différentes stratégies.
    """
    # Méthodes pour le traitement du texte
    def nettoyer_message(self, text):
        text = text.lower() # le texte est converti en minuscules
        text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn') #normalisation unicode pour enlever les accents
        text = re.sub(r'[^\w\s]', '', text) #suppression de la ponctuation
        text = re.sub(r'\s+', ' ', text) #remplacement des espaces multiples par un seul espace
        return text.strip() #separation des espaces en début et fin de chaîne
    

    # Méthodes pour le traitement des documents
    #ici, le texte est découpé en chunks basés sur des phrases
    #chaque chunk comprend un certain nombre de phrases défini par taille_fenetre
    def decouper_chunks(self, text, taille_fenetre=config.CHUNK_SIZE):
        #les phrases sont extraites en utilisant une expression régulière qui divise le texte aux points, points d'exclamation et points d'interrogation suivis d'espaces
        phrases = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        #pour chaque segment de phrases, un chunk est créé en joignant les phrases ensemble
        for i in range(0, len(phrases), taille_fenetre):
            chunk = ' '.join(phrases[i:i+taille_fenetre])
            if chunk.strip():
                chunks.append(chunk)
        return chunks #on retourne la liste des chunks créés

    # Méthodes pour la recherche et la réponse(Methode Parent)
    #cette methode utilise TF-IDF pour extraire le passage le plus pertinent en fonction de la question posée
    def extraire_passage_tfidf(self, question):
        #si aucun chunk de document n'est disponible ou si le vectoriseur ou la matrice des documents n'est pas initialisé, on retourne None
        if not self.doc_chunks or self.vectorizer is None or self.doc_matrix is None:
            return None
        try:
            #la question est transformée en vecteur TF-IDF
            q_vect = self.vectorizer.transform([question])
            #les scores de similarité entre la question et chaque chunk de document sont calculés
            """
            explication du .torray et du .ravel:
            .torray 
                Cette méthode est utilisée pour convertir une matrice creuse (sparse matrix) en un tableau NumPy dense (dense array).
                Les matrices creuses sont souvent utilisées dans le traitement du langage naturel et l'apprentissage automatique
                car elles permettent de représenter efficacement des données avec beaucoup de zéros (comme les matrices
            .ravel
                Cette méthode est utilisée pour aplatir un tableau NumPy multidimensionnel en un tableau unidimensionnel.
                Cela signifie que toutes les dimensions du tableau sont "aplaties" en une seule dimension.
            -----------------------------
            En combinant les deux méthodes, on obtient un tableau unidimensionnel dense qui contient les scores de similarité entre la question et chaque chunk de document.
            """
            scores = (self.doc_matrix @ q_vect.T).toarray().ravel()
            idx_score = scores.argmax() #extraction du seil de pertinance
            if scores[idx_score] > 0.1: # Seuil de pertinence
                return self.doc_chunks[idx_score]
            return None
        except Exception as e:
            print(f"Erreur TF-IDF: {e}")
            return None
    #Methode d'ajout du contenu documentaire
    def ajouter_contenu(self, contenu):
        self.document_content += "\n" + contenu
        # Recréer les chunks et la matrice TF-IDF à chaque ajout de contenu
        chunks = self.decouper_chunks(self.document_content)
        self.doc_chunks = chunks
        if self.vectorizer and self.doc_chunks:
            self.doc_matrix = self.vectorizer.fit_transform(self.doc_chunks)
        print(f"({len(self.document_content)}caractères)")

    #Methode permettant la lecture des fichiers text au bot
    def lire_fichier_txt(self, chemin):
        try:
            with open(chemin, "r", encoding="utf-8") as f: contenu = f.read()
            self.ajouter_contenu(contenu)
            return f"Fichier texte '{os.path.basename(chemin)}' chargé."
        except Exception as e: return f"Erreur lecture {os.path.basename(chemin)}: {e}"
    #Methode permettant la lecture des fichiers word au bot
    def lire_fichier_word(self, chemin):
        # Ici on procede d'abord par la verification de l'existance du module docx
        #en cas d'absence, un message d'erreur est retourné
        if docx is None: return "Module python-docx non disponible."
        #sinon, on tente de lire le fichier word:
        try:
            doc = docx.Document(chemin)
            contenu = "\n".join([para.text for para in doc.paragraphs])
            self.ajouter_contenu(contenu)
            return f"Fichier Word '{os.path.basename(chemin)}' chargé."
        #en cas d'erreur lors de la lecture, un message d'erreur est retourné
        except Exception as e: return f"Erreur lecture {os.path.basename(chemin)}: {e}"

    #Methode permettant la lecture des fichiers pdf au bot
    def lire_fichier_pdf(self, chemin):
        #meme logique que pour les fichiers word
        #en cas d'abscence ,on renvioie un message d'erreur
        if fitz is None: return "Module PyMuPDF non disponible."
        #sinon, on tente de lire le fichier pdf
        try:
            with fitz.open(chemin) as doc:
                contenu = "".join(page.get_text() for page in doc)
            self.ajouter_contenu(contenu)
            return f"Fichier PDF '{os.path.basename(chemin)}' chargé."
        except Exception as e: return f"Erreur lecture {os.path.basename(chemin)}: {e}"


    """
    Ici, nous avons la troisième partie de la logique du chatbot.
    Celle ci concerne le chargement des documents au démarrage et la gestion des réponses aux questions
    Dans cette section, on trouve des méthodes pour charger les documents depuis un dossier spécifié,
    répondre aux intentions prédéfinies, gérer les réponses basées sur la base de connaissances,
    et générer des réponses en fonction du contenu des documents.
    """
    #Cette methode permet au bot de charger les documents au demarrage 
    #Elle charge les documents txt,pdf et docx(word) uniquement
    def charger_documents(self, dossier=config.DATA_DIR):
        if not os.path.exists(dossier): 
            return
        #on confirme l'existance et l'extension  de chacun des fichiers contenu dans le dossier *****
        for fichier in os.listdir(dossier):
            chemin = os.path.join(dossier, fichier)
            if not os.path.isfile(chemin): continue
            if fichier.lower().endswith('.txt'): print(self.lire_fichier_txt(chemin))
            elif fichier.lower().endswith('.pdf'): print(self.lire_fichier_pdf(chemin))
            elif fichier.lower().endswith('.docx'): print(self.lire_fichier_word(chemin))

    #Cette methode permet de repondre aux questions de l'utilisateur en fonction des "intensions"
    #ici, chaque intention constue une liste des questions valides a partir desquelles certaines reponses prévues a cet effet 
    #sont données de maniere aléatoire
    def _repondre_intentions(self, message_simple):
        #par exemple, pour chaque mot present dans les intentions de salutation et present dans le message de
        #l'utilisateur, on renvoie l'un des messages contenu dans la liste en random.
        if any(mot in message_simple for mot in self.intents['saluer']):
           return random.choice(["Bonjour ! Que puis-je faire pour vous?", 
                              "Salut, comment puis-je vous aider?", 
                              "Bonjour, en quoi puis-je vous être utile?"])
        #meme chose a ce niveau
        if any(mot in message_simple for mot in self.intents['comment_cv']):
            return random.choice(["Je vais bien, merci. Et vous?", 
                              "Je suis toujours en forme pour vous aider.", 
                              "Tout va bien, prêt à vous assister."])
        #et ici aussi
        if any(mot in message_simple for mot in self.intents['heure']):
            return f"Il est {datetime.now().strftime('%d/%m/%Y, %H:%M:%S')}"
        #
        if any(mot in message_simple for mot in self.intents['remercier']):
            return random.choice(["Avec plaisir!", "Il n'y a pas de quoi.", "C'est un plaisir de vous aider."])
        #
        if any(mot in message_simple for mot in self.intents['aurevoir']):
            return random.choice(["À bientôt !", "Au revoir, à très vite."])
          
        return None
    
    #ici, les reponses sont données de maniere exacte si le systeme clé-valeur est correcte à 100%
    def _repondre_faq_exacte(self, message_simple):
        return self.knowledge_base.get(message_simple)

    #Par contre, ici on prend en compte les  approximations dans les clés de l'utilisateur
    def _repondre_faq_approximative(self, message_simple):
        if not self.knowledge_base: return None
        #c'est ici qu'on crée une correspondance entre le message de l'user et les clés de la base de connaissance
        #en admettant un seuil de similarité
        correspondance = difflib.get_close_matches(message_simple, self.knowledge_base.keys(), n=1, cutoff=config.SIMILARITY_CUTOFF)
        #si lee seuil de correspondance est atteint, ou meme depassé on renvoi la reponse prevue à cet effet.
        if correspondance:
            return self.knowledge_base[correspondance[0]]
        return None

    #Methode pour retourné la reponse issue de l'extraction du contenu des documents
    def _repondre_docs(self, message_original):
        return self.extraire_passage_tfidf(message_original)

    #Methode principale de reponse aux questions
    def repondre(self, message: str) -> dict:
        message_simple = self.nettoyer_message(message)
        reponse = None
        score = 0.0

        # Ordre de priorité
        reponse = self._repondre_intentions(message_simple)
        if reponse: score = 1.0
        
        if reponse is None:
            reponse = self._repondre_faq_exacte(message_simple)
            if reponse: score = 0.9

        if reponse is None:
            reponse = self._repondre_faq_approximative(message_simple)
            if reponse: score = 0.8

        if reponse is None:
            reponse = self._repondre_docs(message)
            if reponse: score = 0.7

        if reponse is None:
            reponse = "Je suis désolé, je n'ai pas trouvé de réponse."
        
        resultat = {
            "question": message,
            "reponse": reponse,
            "score(/1)": round(score, 2),
            "horodatage": datetime.now().isoformat()
        }
        self.sauvegarder_interactions(resultat)
        return resultat

    #Methode de sauvegarde des interactions
    def sauvegarder_interactions(self, interaction: dict):
       """
       Sauvegarde chaque interaction (question-réponse) dans un fichier JSON.
       """
       historique_fichier = "historique.json"

       # Charger l'historique existant
       if os.path.exists(historique_fichier):
           try:
               with open(historique_fichier, "r", encoding="utf-8") as f:
                    historique = json.load(f)
           except (json.JSONDecodeError, IOError):
                    historique = []
       else:
        historique = []

       # Ajouter la nouvelle interaction
       historique.append(interaction)

       # Réécrire le fichier
       with open(historique_fichier, "w", encoding="utf-8") as f:
            json.dump(historique, f, ensure_ascii=False, indent=4)
       pass