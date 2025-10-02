from fastapi import FastAPI,UploadFile, File
import uvicorn
from pydantic import BaseModel
from chatbotcol import Chatbot
from fastapi.middleware.cors import CORSMiddleware
import os
import datetime
import shutil

# Création de l'application FastAPI
app = FastAPI()

#Autoriser CORS au developpement
app.add_middleware(
    CORSMiddleware,#permet d'autoriser les requetes cross-origin
    allow_origins=["*"],#en production, mettre l'url de mon site
    allow_credentials=True,#permet d'envoyer des cookies
    allow_methods=["*"],#permet d'envoyer des requetes en GET, POST, PUT, DELETE
    allow_headers=["*"],#permet d'envoyer des headers
)

# Création de l'instance du bot au démarrage de l'API
bot = Chatbot()

# Endpoint de test
@app.get("/")
def lire_racine():
    return {"message": "Bienvenu sur l'API du ColepsBot!"}


# Modèle pour recevoir les questions de l'utilisateur
class QuestionRequest(BaseModel):
    question: str

# Endpoint pour répondre
@app.post("/recherche")
def repondre_a_question(question: QuestionRequest):
    reponse = bot.repondre(question.question)
    return {"recherche": reponse}
   

#creer le dossier contenant les fichiers mis a la disposition du bot
DATA_DIR=os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(DATA_DIR,exist_ok=True)

#  endpoint pour la liste des documents disponibles
@app.get("/documents")
def lister_documents():
    """
      Retourne la liste des documents disponibles avec infos détaillées
      (nom, taille en Ko, date de modification ISO8601)
    """
    fichiers = []
    try:
        for f in os.listdir(DATA_DIR):
            if f.lower().endswith(('.txt', '.pdf', '.docx')):
                chemin = os.path.join(DATA_DIR, f)
                fichiers.append({
                    "nom": f,
                    "taille_ko": round(os.path.getsize(chemin) / 1024, 2),
                    "date_modification": datetime.datetime.fromtimestamp(os.path.getmtime(chemin)).isoformat()
                })
        return {"documents": fichiers, "nombre": len(fichiers)}
    except Exception as e:
        return {"error": str(e), "documents": []} 
    
# Endpoint pour uploader un document
@app.post("/upload")
async def uploader_document(file: UploadFile = File(...)):
    """
    Endpoint pour uploader un document (txt, pdf, docx).
    Le fichier est sauvegardé dans le dossier DATA_DIR.
    """
    if not file.filename.lower().endswith(('.txt', '.pdf', '.docx')):
        return {"error": "Format de fichier non supporté. Seuls les fichiers .txt, .pdf, .docx sont autorisés."}
    
    chemin_sauvegarde = os.path.join(DATA_DIR, file.filename)
    
    try:
        with open(chemin_sauvegarde, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        #Chargement des documents dans le bot
        bot.charger_documents(DATA_DIR)
        return {"message": f"Fichier '{file.filename}' uploadé et chargé dans le bot avec succès."}
    
    except Exception as e:
        return {"error": str(e)}
    
       
# Lancer uvicorn depuis ce script si exécuté directement
if __name__ == "__main__":
    uvicorn.run("fastapi_main:app", host="127.0.0.1", port=8000, reload=True)
