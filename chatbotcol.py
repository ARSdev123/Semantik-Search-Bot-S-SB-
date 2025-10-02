import json
import os
from datetime import datetime
#from collections import Counter
#from difflib import SequenceMatcher
from sklearn.feature_extraction.text import TfidfVectorizer
import random
import difflib
import unicodedata
import fitz
import re
import spacy

class Chatbot:
   
    """
    Classe principale du Chatbot.
    Gère la logique de conversation, la gestion des connaissances et l'apprentissage.
    """
    def __init__(self):
        """
        Initialise le chatbot.
        - Charge les données de base (intentions, base de connaissances).
        - Initialise les variables d'état.
        """
        #self.nom_user = ""
        # Charge les données depuis les fichiers JSON
        self.intents, self.knowledge_base = self._load_data('data.json', is_base=True)
        # Variable pour garder en mémoire la question en attente d'une réponse pour l'apprentissage
        self.question_en_attente = None
        #pour receuillir le taux de popularité d'une question
        self.statistiques_questions=self._load_stats()
        # Pour stocker le contenu des documents chargés
        self.document_content = ""
        # Charger SpaCy une seule fois
        self.nlp = spacy.load("fr_core_news_sm")
    
        #TF-IDF
        self.vectorizer=None
        self.doc_matrix=None
        self.doc_chunks=[]

        # --- Chargement automatique de fichiers Word et PDF au démarrage ---
        self.charger_documents("data")


        self.fichiers_word = [f for f in os.listdir("data") if f.lower().endswith('.docx')]
        self.fichiers_pdf = [f for f in os.listdir("data") if f.lower().endswith('.pdf')]
        self.fichiers_txt = [f for f in os.listdir("data") if f.lower().endswith('.txt')]  
      
    
    def _load_data(self, fichier, is_base=False):
        """
        Charge les données depuis un fichier JSON.
        Crée le fichier s'il n'existe pas.
        """
        # Crée le fichier s'il n'existe pas (utile pour le premier lancement)
        if not os.path.exists(fichier):
            with open(fichier, "w", encoding="utf-8") as f:
                # Initialise avec un objet vide ou une structure de base
                json.dump({} if not is_base else {"intents": [], "knowledge_base": {}}, f)

        # Charge les données du fichier
        with open(fichier, "r", encoding="utf-8") as f:
            data = json.load(f)
           
        if is_base:
            # Pour le fichier de base, on nettoie les clés de la base de connaissances
            knowledge_base = {
                self.nettoyer_message(k): v for k, v in data["knowledge_base"].items()
            }
            return data["intents"], knowledge_base
        else:
            # Pour le fichier d'apprentissage, on nettoie toutes les clés
            return {self.nettoyer_message(k): v for k, v in data.items()}
        

    # GESTION DES STATISTIQUES DES QUESTIONS FREQUEMENT POSEES
    def _load_stats(self):
          if not os.path.exists("stats.json"):
            with open("stats.json", "w", encoding="utf-8") as f:
               json.dump({}, f)
          with open("stats.json", "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_stats(self):
          with open("stats.json", "w", encoding="utf-8") as f:
           json.dump(self.statistiques_questions, f, ensure_ascii=False, indent=4)

    def _increment_stat(self,question):
        if question in self.statistiques_questions:
            self.statistiques_questions[question] +=1
        else:
            self.statistiques_questions[question] =1
        self._save_stats()


    #PARTIE LIEE AU TRAITEMENT LINGUISTIQUE DES DOCUMENTS CHARGéS
    def lematise_phrase(self,phrase):
        """
        Transformer une phrase en une version lematisée
        """ 
         #chargement du modele spacy pour la lemmatisation en francais
        doc= self.nlp(phrase)
        lemmes = [token.lemma_.lower() for token in doc if not token.is_punct and not token.is_space]
        return "".join(lemmes)
        
    #nettoyage linguistique
    def nettoyer_message(self, text):
        """
        Nettoie une chaîne de caractères pour la rendre comparable :
        - Met en minuscules.
        - Supprime les espaces au début et à la fin.
        - Supprime les accents.
        """
        text = text.lower()
        text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', ' ', text)  # Supprime les espaces
        return text.strip()


    def decouper_chunks(self, text, taille_fenetre):
        phrases=re.split(r'(?<=[.!?])\s+', text)
        chunks=[]
        for i in range (0,len(phrases), taille_fenetre ):
            chunk=' '.join(phrases[i:i+taille_fenetre])
            if chunk.strip():
               chunks.append(chunk)
        return chunks

    def extraire_passage_tfidf(self, texte, question):
        """
        Extrait le passage le plus pertinent du texte en utilisant l'analyse vectorielle TF-IDF.
        1. Découpe le texte en chunks (fenêtres de 3 phrases).
        2. Vectorise les chunks et la question avec TfidfVectorizer.
        3. Calcule la similarité entre chaque chunk et la question.
        4. Retourne les 3 chunks les plus pertinents.
       """
        if not self.doc_chunks:
            return "Aucun diocument chargé"
        q_vect= self.vectorizer.transform([question])
        scores = (self.doc_matrix @ q_vect.T).toarray().ravel()
        self.idx_score= scores.argmax()
        if scores[self.idx_score]<=0.1:
            return "Aucun passage pertinent trouvé."
        return self.doc_chunks[self.idx_score]

    def ajouter_contenu(self, contenu):
        """Ajoute le contenu d'un document au stockage du chatbot."""
        try:
           self.document_content += "\n" + contenu
           # Réinitialise le vectoriseur et la matrice TF-IDF
           chunks= self.decouper_chunks(contenu,3)
           self.doc_chunks.extend(chunks)

           #recalcule la matrice tf-idf à chaque ajout de contenu
           self.vectorizer = TfidfVectorizer(ngram_range=(1, 2))
           self.doc_matrix = self.vectorizer.fit_transform(self.doc_chunks)
        
           print(f"Contenu ajouté ({len(contenu)} caractères)")
        except Exception as e :
           print (f"ajouter_contenu ne fonctione pas: erreur{e} trouvé")


    #---FONCTION PERMETTANT DE LIRE UN FICHIER TXT---
    def lire_fichier_txt(self, chemin):
        """Lit un fichier texte et ajoute son contenu aux documents du chatbot."""
        try:
           with open(chemin, "r", encoding="utf-8") as f:
             contenu = f.read()
             self.ajouter_contenu(contenu)
             return f"Contenu du fichier texte chargé ({len(contenu)} caractères)."
        except FileNotFoundError:
            return f"Le fichier {chemin} n'existe pas."
        except Exception as e:
            return f"Une erreur est survenue lors de la lecture du fichier {chemin}: {e}"
        
    #FONCTION PERMETTANT DE LIRE UN DOCUMENT WORD
    def lire_fichier_word(self, chemin):
        """Lit un fichier Word et ajoute son contenu aux documents du chatbot."""
        try:
            import docx
            doc = docx.Document(chemin)
            contenu = "\n".join([para.text for para in doc.paragraphs])
            self.ajouter_contenu(contenu)
            return f"Contenu du fichier Word chargé ({len(contenu)} caractères)."
        except FileNotFoundError:
            return f"Le fichier {chemin} n'existe pas."
        except Exception as e:
            return f"Une erreur est survenue lors de la lecture du fichier {chemin}: {e}" 
        
    #---FONCTION PERMETTANT DE LIRE UN DOCUMENT PDF---
    def lire_fichier_pdf(self, chemin):
        """Lit un fichier PDF et ajoute son contenu aux documents du chatbot."""
        try:
            doc = fitz.open(chemin)
            contenu = ""
            for page in doc:
                contenu += page.get_text()
            doc.close()
            self.ajouter_contenu(contenu)
            return f"Contenu du fichier PDF chargé ({len(contenu)} caractères)."
        except FileNotFoundError:
            return f"Le fichier {chemin} n'existe pas."
        except Exception as e:
            return f"Une erreur est survenue lors de la lecture du fichier {chemin}: {e}"

    #fonction d'extraction des titres dans les documents pdf
    def _extraire_titres_pdf(self, chemin_pdf, ):
        """
        Extrait les titres d'un document PDF en utilisant la taille de la police comme critère.
        Considère qu'un titre est une ligne avec une taille de police supérieure à un certain seuil.
        """
        titres = []
        try:
            doc = fitz.open(chemin_pdf)
            for page in doc:
                blocks = page.get_text("dict")["blocks"]
                for b in blocks:
                    if b['type'] == 0:  # Texte
                        for line in b["lines"]:
                            for span in line["spans"]:
                                if span["size"] > 12:  # Seuil de taille pour considérer comme titre
                                    titres.append(span["text"])
            doc.close()
            return dict.fromkeys(titres)
        except Exception as e:
            print(f"Erreur lors de l'extraction des titres : {e}")
            return titres
        

    def extraire_titres_word(self, chemin_word):
        try:
            import docx
            doc=docx.Document(chemin_word)
            titres=[]

            for para in doc.paragraphs:
                style= para.style.name.lower()
                tit=["titre","title","heading"]
                if tit in style or style in ["heading 1", "heading 2"]:
                    text=para.text.strip()
                    if text and text not in titres:
                        titres.append(text)
            return titres
        except Exception as e:
           print(f"Erreur lecture Word : {e}")
           return []

    def extraire_titres(self, chemin_fichier):
        """
        Extrait les titres d'un document (PDF ou Word).
        Utilise les styles (Word) ou la taille de police (PDF).
        """
        _, extension = os.path.splitext(chemin_fichier.lower())
    
        if extension == ".pdf":
           return self._extraire_titres_pdf(chemin_fichier)
        elif extension in [".doc", ".docx"]:
           return self._extraire_titres_word(chemin_fichier)
        else:
           return []


    #fonction permettant d'extraire le contenu de la premiere page du doc pdf
    def extraire_premiere_page(self, chemin_pdf):
        """
        Extrait le texte de la première page d'un document PDF.
        """
        try:
            doc = fitz.open(chemin_pdf)
            if len(doc) > 0:
                page_1 = doc[0]
                contenu = page_1.get_text()
                doc.close()
                return contenu
            else:
                doc.close()
                return "Document PDF vide."
        except Exception as e:
            print(f"Erreur lors de l'extraction de la première page : {e}")
            return ""
        
        
    #fonction de nettoyage de texte
    def nettoyer_texte(self, texte):
        """
        Nettoie le texte en supprimant les caractères spéciaux et les espaces superflus.
        """
        # Supprimer les caractères spéciaux
        texte = re.sub(r'[^\w\s]', '', texte)
        # Supprimer les espaces multiples
        texte = re.sub(r'\s+', ' ', texte)
        # Supprimer les espaces au début et à la fin
        return texte.strip()
    
    #fonction de chargement des documents dans le bot
    def charger_documents(self, dossier="data"):
        """
        Charge tous les documents (txt, pdf, docx) d'un dossier donné dans le chatbot.
        """
        try:
            self.docs=[]
            for fichier in os.listdir(dossier):
                chemin = os.path.join(dossier, fichier)
                if fichier.lower().endswith('.txt'):
                    resultat = self.lire_fichier_txt(chemin)
                    print(resultat)
                    self.docs.append(fichier)
                elif fichier.lower().endswith('.pdf'):
                     resultat = self.lire_fichier_pdf(chemin)
                     print(resultat)
                     self.docs.append(fichier)
                elif fichier.lower().endswith('.docx'):
                     resultat = self.lire_fichier_word(chemin)
                     print(resultat)
                     self.docs.append(fichier)
        except Exception as e:
            print(f"Erreur lors du chargement des documents : {e}")
        #recalculer la matrice tf-idf
        if self.docs:
            self.doc_matrix = self.vectorizer.fit_transform(self.doc_chunks)
            print(f"Documents chargés : {', '.join(self.docs)}")
        
      
    #FONCTIONS QUI S'OCCUPENT DE LA GENERATION DES REPONSES AUX QUESTIONS DE L'UTILISATEUR
    
    def _repondre_intentions(self, message_nettoye):
        """
        Gère les réponses basées sur les intentions de base (salutations, remerciements, etc.).
        """
        if any(mot in message_nettoye for mot in self.intents['saluer']):
            return random.choice(["Bonjour ! Que puis-je faire pour vous?", "Salut, comment puis-je vous aider?", "Bonjour, en quoi puis-je vous être utile?"])
        
        elif any(mot in message_nettoye for mot in self.intents['comment_cv']):
            return random.choice(["Je vais bien, merci. Et vous?", "Je suis toujours en forme pour vous aider.", "Tout va bien, prêt à vous assister."])
        
        elif any(mot in message_nettoye for mot in self.intents['heure']):
            return f"Il est {datetime.now().strftime('%d/%m/%Y, %H:%M:%S')}"
        
        elif any(mot in message_nettoye for mot in self.intents['remercier']):
            return random.choice(["Avec plaisir!", "Il n'y a pas de quoi.", "C'est un plaisir de vous aider."])
        
        elif any(mot in message_nettoye for mot in self.intents['aurevoir']):
            return random.choice(["À bientôt !", "Au revoir, à très vite."])
        
        elif "qu'est ce que tu sais faire?" in message_nettoye or "tu sais faire quoi?" in message_nettoye:
            return "Je suis un assistant virtuel capable de vous aider à trouver des informations dans les documents que vous chargez. Vous pouvez me poser des questions et je chercherai les réponses dans ces documents."
        
        elif "je vais bien merci" in message_nettoye or "ça va bien" in message_nettoye or "ca va" in message_nettoye:
            return random.choice(["Je suis heureux de l'apprendre.", "Parfait! En quoi puis-je vous aider?"])
        
        return None
    

    def _repondre_faq_exacte(self, message_nettoye):
        """
        Gère les réponses basées sur une correspondance exacte dans la base de connaissances.
        """
        if message_nettoye in self.knowledge_base:
            self._increment_stat(message_nettoye)
            return self.knowledge_base[message_nettoye]
        return None
    

    def _repondre_faq_approximative(self, message_nettoye):
        all_known_questions = list(self.knowledge_base.keys()) 
        correspondance = difflib.get_close_matches(message_nettoye, all_known_questions, n=1, cutoff=0.60)
        if correspondance:
            question_proche = correspondance[0]
            self._increment_stat(question_proche)
            return self.knowledge_base.get(question_proche, None)
        return None
           

    def _repondre_docs(self, message_original, message_nettoye):
        """
        Gère les réponses basées sur le contenu des documents chargés.
        Utilise TF-IDF pour trouver des passages pertinents.
        """
        if not self.doc_chunks:
            return None
        
        #--------RECHERCHE TF-IDF-------
        passage_pertinent = self.extraire_passage_tfidf( self.document_content, message_original)
        if passage_pertinent and passage_pertinent not in ["Aucun passage retrouvé.", "Aucun passage pertinent trouvé."]:
            return passage_pertinent
        
        # ----si la question est vague on suggere les titres-----
        if self.est_question_vague(message_nettoye):
            titres=[]
            for fichier in self.fichiers_word +self.fichiers_pdf:
                if os.path.exists(fichier):
                    titres.extend(self.extraire_titres(fichier))
            titres_uniques= list(dict.fromkeys(titres))
            if titres_uniques:
                return "veillez orienter vos recherches en fonction des points suivants:\n- "+"\n-".join(titres_uniques)
        return None
    

    #----FONCTION D'ORIENTATION DES REPONSES 
    def repondre(self,message: str) -> dict:
        """
        Génère une réponse à un message de l'utilisateur.
        Cette méthode délègue maintenant le travail à plusieurs sous-méthodes spécialisées.
        """
        #-----pretraitement du message-------
        message_lematise= self.lematise_phrase(message)
        message_nettoye=self.nettoyer_message(message_lematise)

        reponse = None
        score = 0.0


        # --- ÉTAPE 1 : APPRENTISSAGE DU PRÉNOM (simplifié) ---
        if "je m'appelle" in message_nettoye or "mon nom est" in message_nettoye :
            mots = message.split()
            for i, mot in enumerate(mots):
                if mot in ["m'appelle", "m'appelles"] and i + 1 < len(mots):
                    self.nom_user = mots[i + 1].capitalize()
                    return f"Enchanté, {self.nom_user}. Que puis-je faire pour vous?"
            return "Je n'ai pas compris votre prénom."
        
        # Le bot n'est plus obligé de demander le prénom pour répondre


        #---------intentions de base--------
        if reponse is None:
           reponse = self._repondre_intentions(message_nettoye)
           if reponse:
              score = 1.0
        
        #------selon la knowledge_base-----
        if reponse is None:
           reponse = self._repondre_faq_exacte(message_nettoye)
           if reponse:
               score = 0.9
        
        #----recherche approximative-----
        if reponse is None:
           reponse = self._repondre_faq_approximative(message_nettoye)
           if reponse:
               score = 0.8

        #-----recherche dans les documents-----
        if reponse is None:
           reponse = self._repondre_docs(message, message_nettoye)
           if reponse:
               score = 0.7
        
        #si rien n'est trouvé
        if reponse is None:
           score = 0.0
           reponse = "Je suis désolé, je n'ai pas trouvé de réponse à votre question. Pouvez-vous reformuler ou poser une autre question?"
        
        #----Construction du resultat final-----
        resultat = {
            "question": message,
            "reponse": reponse,
            "score(/1)": round(score, 2),
            "horodatage": datetime.now().isoformat()
        }

        # Sauvegarde de l'interaction dans l'historique
        self.sauvegarder_interactions(resultat)

        return resultat
    
    def sauvegarder_interactions(self, interaction:dict):
        """
        Sauvegarde chaque interaction (question-réponse) dans un fichier JSON.
        """
        historique_fichier = "historique.json"
        historique = []
        if os.path.exists(historique_fichier):
            with open(historique_fichier, "r", encoding="utf-8") as f:
                try:
                    historique = json.load(f)
                except json.JSONDecodeError:
                    historique = []
        historique.append(interaction)
        with open(historique_fichier, "w", encoding="utf-8") as f:
            json.dump(historique, f, ensure_ascii=False, indent=4)