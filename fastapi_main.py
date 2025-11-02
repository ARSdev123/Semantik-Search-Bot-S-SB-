import os # Pour les opérations sur les fichiers et dossiers
import datetime #Pour la gestion des dates
import shutil # Pour la gestion des fichiers

# Gestion des imports avec gestion d'erreurs
MODULES_MANQUANTS = []

try:
    from fastapi import FastAPI, UploadFile, File, Depends, Security # Ajout de Depends et Security pour la sécurité par clé d'API
    from fastapi import HTTPException  # Ajout pour gestion d'erreurs HTTP
    from fastapi.security import APIKeyHeader # Pour la sécurité par clé d'API
    from starlette.status import HTTP_403_FORBIDDEN # Pour les codes de statut HTTP

#en cas d'import manquant, on ajoute à la liste des modules manquants
except ImportError:
    MODULES_MANQUANTS.append("fastapi")
    FastAPI = None
    HTTPException = None

try:
    import uvicorn # Pour lancer le serveur FastAPI
#et en cas d'import manquant, on ajoute à la liste des modules manquants
except ImportError:
    MODULES_MANQUANTS.append("uvicorn")
    uvicorn = None

try:
    #Pydantic est une bibliothèque utilisée par FastAPI pour la validation des données
    from pydantic import BaseModel # Pour la validation des [modèles de requêtes/réponses]
except ImportError:
    MODULES_MANQUANTS.append("pydantic")
    BaseModel = None

try:
    from chatbotcol import Chatbot # Importation de la classe Chatbot depuis le module chatbotcol
except ImportError:
    MODULES_MANQUANTS.append("chatbotcol")
    Chatbot = None

try:
    # Middleware CORS pour autoriser les requêtes cross-origin (utile pour le développement front-end)
    from fastapi.middleware.cors import CORSMiddleware # Pour gérer les CORS
except ImportError:
    MODULES_MANQUANTS.append("fastapi-cors")
    CORSMiddleware = None


# Vérification des modules critiques au démarrage
if MODULES_MANQUANTS:
    #dans le cas où des modules sont manquants, on affiche un message d'erreur
    print(f"Attention: Modules manquants détectés dans l'API: {', '.join(MODULES_MANQUANTS)}")
    print("L'API ne pourra pas démarrer correctement.")

# Création de l'application FastAPI
if FastAPI is None:
    print("Erreur: FastAPI non disponible")
    app = None
else:
    app = FastAPI()

    # --- Sécurité par Clé d'API ---
    # Définir le header pour la clé d'API
    api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

    # Dépendance pour vérifier la clé d'API
    #utilisation d'une fonction asynchrone pour la vérification de la clé d'API,la raison est que FastAPI supporte nativement les dépendances asynchrones
    async def get_api_key(api_key_header: str = Security(api_key_header)):
        """Dépendance pour vérifier la clé d'API fournie dans l'en-tête X-API-Key."""
        if api_key_header is None or api_key_header != config.API_KEY:
            # Si la clé est manquante ou invalide, lever une exception HTTP 403
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, detail="Clé d'API manquante ou invalide"
            )
    # --------------------------------


    # Autoriser CORS au développement
    if CORSMiddleware is not None:
        app.add_middleware(
            CORSMiddleware,  # permet d'autoriser les requêtes cross-origin
            allow_origins=["*"],  # en production, mettre l'URL de mon site
            allow_credentials=True,  # permet d'envoyer des cookies
            allow_methods=["*"],  # permet d'envoyer des requêtes en GET, POST, PUT, DELETE
            allow_headers=["*"],  # permet d'envoyer des headers (comme la clé d'API)
        )
    else:
        print("CORS middleware non disponible")

# Création de l'instance du bot au démarrage de l'API
if Chatbot is None:
    print("Erreur: Chatbot non disponible")
    bot = None
else:
    #instanciation du chatbot
    bot = Chatbot()

# Endpoint de test
@app.get("/", summary="Endpoint de test de l'API")
def lire_racine():
    """Vérifie que l'API est en ligne et retourne un message de bienvenue."""
    if app is None:
        return {"error": "API non disponible"}

    return {"message": "Bienvenue sur l'API du ColepsBot!"}


# Modèle pour recevoir les questions de l'utilisateur
if BaseModel is not None:
    class QuestionRequest(BaseModel):
        question: str # La question posée par l'utilisateur est une chaîne de caractères
        class Config:
            schema_extra = {
                "example": {"question": "Qu'est ce qu'une hypothese legale ?"}
            }
else:
    QuestionRequest = None

# Endpoint pour répondre
@app.post("/recherche", summary="Pose une question au chatbot", dependencies=[Depends(get_api_key)])
def repondre_a_question(question: QuestionRequest):
    """
    Cet endpoint reçoit une question de l'utilisateur, la traite avec le chatbot
    et retourne la réponse trouvée, le score de confiance et d'autres métadonnées.
    """
    if app is None:
        return {"error": "API non disponible"}

    if bot is None:
        return {"error": "Chatbot non disponible"}

    if QuestionRequest is None:
        return {"error": "Modèle de données non disponible"}
    # Traiter la question avec le bot
    try:
        reponse = bot.repondre(question.question)
        return {"recherche": reponse}
    except Exception as e:
        #en cas d'erreur, on retourne un message d'erreur
        return {"error": f"Erreur lors du traitement de la question: {e}"}
   

# Importation de la configuration centralisée pour les chemins et paramètres
import config #config.py , qui contient les paramètres globaux

# Le dossier de données est maintenant défini de manière centralisée dans config.py
DATA_DIR = config.DATA_DIR

# Endpoint pour la liste des documents disponibles
@app.get("/documents", summary="Liste les documents disponibles pour le chatbot", dependencies=[Depends(get_api_key)])
def lister_documents():
    """
    Retourne la liste de tous les documents (.txt, .pdf, .docx) actuellement chargés 
    dans le chatbot, avec leur nom, taille et date de modification.
    """
    if app is None:
        # On garde le retour JSON ici car HTTPException dépend de FastAPI
        return {"error": "API non disponible"}

    fichiers = [] # Liste pour stocker les informations des fichiers
    try:
        if not os.path.exists(DATA_DIR):
            # Utilisation de HTTPException pour signaler l'erreur
            raise HTTPException(status_code=404, detail=f"Dossier {DATA_DIR} non trouvé")
        # Parcours des fichiers dans le dossier de données et pour chaque fichier, on vérifie l'extension et on récupère les infos
        for f in os.listdir(DATA_DIR):
            #si le fichier a une extension valide,
            if f.lower().endswith(('.txt', '.pdf', '.docx')):
                chemin = os.path.join(DATA_DIR, f)
                try:
                    #on recuperer les infos du fichier
                    fichiers.append({
                        "nom": f,
                        "taille_ko": round(os.path.getsize(chemin) / 1024, 2),
                        "date_modification": datetime.datetime.fromtimestamp(os.path.getmtime(chemin)).isoformat()
                    })
                except OSError as e:
                    # En cas d'erreur d'accès au fichier, on l'ignore et on continue
                    print(f"Erreur lors de l'accès au fichier {f}: {e}")
                    continue
        # Retourne la liste des fichiers et le nombre total 
        return {"documents": fichiers, "nombre": len(fichiers)}
    except HTTPException:
        raise
    except Exception as e:
        # Remonte l'erreur via HTTPException
        raise HTTPException(status_code=500, detail=str(e))
    
# Endpoint pour uploader un document
@app.post("/upload", summary="Uploade un nouveau document pour le chatbot", dependencies=[Depends(get_api_key)])
async def uploader_document(file: UploadFile = File(...)):
    """
    Permet d'envoyer un nouveau document (.txt, .pdf, .docx) qui sera ajouté 
    à la base de connaissances du chatbot. Le fichier est sauvegardé dans le 
    dossier de données et son contenu est immédiatement chargé dans le bot.
    """
    if app is None:
        return {"error": "API non disponible"}

    if not file.filename.lower().endswith(('.txt', '.pdf', '.docx')):
        # Utilisation de HTTPException pour signaler l'erreur de format
        raise HTTPException(
            status_code=400,
            detail="Format de fichier non supporté. Seuls les fichiers .txt, .pdf, .docx sont autorisés."
        )

    chemin_sauvegarde = os.path.join(DATA_DIR, file.filename)

    try:
        # Créer le dossier s'il n'existe pas
        os.makedirs(DATA_DIR, exist_ok=True)

        with open(chemin_sauvegarde, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer) # Sauvegarde du fichier uploadé

        # Chargement optimisé du nouveau document dans le bot (si disponible)
        if bot is not None:
            try:
                # Déterminer l'action en fonction de l'extension du fichier
                file_ext = os.path.splitext(file.filename)[1].lower()
                if file_ext == '.txt':
                    bot.lire_fichier_txt(chemin_sauvegarde)
                elif file_ext == '.pdf':
                    bot.lire_fichier_pdf(chemin_sauvegarde)
                elif file_ext == '.docx':
                    bot.lire_fichier_word(chemin_sauvegarde)
                
                print(f"Fichier '{file.filename}' chargé dynamiquement dans le bot.")

            except Exception as e:
                # Si le chargement dans le bot échoue, lever une exception.
                # Le fichier est sauvegardé, mais le client doit savoir que le bot n'a pas pu le traiter.
                raise HTTPException(status_code=500, detail=f"Le fichier a été uploadé, mais une erreur est survenue lors de son traitement par le bot: {e}")

        return {"message": f"Fichier '{file.filename}' uploadé et traité avec succès."}

    except Exception as e:
        # Remonte l'erreur via HTTPException
        raise HTTPException(status_code=500, detail=str(e))
    

# Endpoint pour les informations système
@app.get("/system-info", summary="Récupère les prérequis système")
def get_system_info():
    """
    Retourne les configurations minimales et recommandées pour le serveur 
    et les clients (web et bureau), mises à jour pour inclure la recherche sémantique.
    """
    return {
        "server_requirements": {
            "minimum": {
                "cpu_cores": 2,
                "ram_gb": 4,
                "storage_gb": 20,
                "python_version": "3.8+",
                "additional_software": ["FastAPI", "Uvicorn", "Pydantic"]
            },
            "recommended": {
                "cpu_cores": 4,
                "ram_gb": 8,
                "storage_gb": 50,
                "python_version": "3.9+",
                "additional_software": ["FastAPI", "Uvicorn", "Pydantic", "ChatbotLib"]
            }
        },
        "client_requirements": {
            "web_client": {
                "browser": ["Latest Chrome", "Latest Firefox", "Latest Edge", "Latest Safari"],
                "internet_connection": "Stable broadband connection",
                "screen_resolution": "1024x768 minimum"
               
            },
            "desktop_client": {
                "os": ["Windows 10+", "macOS 10.15+", "Linux (Ubuntu 20.04+)"],
                "cpu_cores": 2,
                "ram_gb": 4,
                "storage_gb": 50
               
            }
        }
    }


# Lancer uvicorn depuis ce script si exécuté directement
if __name__ == "__main__":
    if uvicorn is None:
        print("Erreur: Uvicorn non disponible. Impossible de démarrer le serveur.")
        exit(1)

    if app is None:
        print("Erreur: Application FastAPI non disponible. Impossible de démarrer le serveur.")
        exit(1)

    print("Démarrage du serveur FastAPI...")
    # Lancer le serveur Uvicorn avec rechargement automatique
    uvicorn.run("fastapi_main:app", host="127.0.0.1", port=8000, reload=True)

