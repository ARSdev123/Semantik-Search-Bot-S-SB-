# Guide de Sécurisation de l'API FastAPI

Ce document résume les étapes essentielles pour renforcer la sécurité de l'API du projet Semantik-Search-Bot.

## 1. Contrôler l'Accès avec une Clé d'API (Authentification)

C'est la mesure la plus importante à mettre en place. Elle garantit que seules les applications autorisées peuvent utiliser votre API.

**Principe :** Le client (l'application web) doit envoyer une clé secrète dans les en-têtes HTTP de chaque requête (par exemple, `X-API-Key: VOTRE_CLE_SECRETE`). Le serveur vérifiera cette clé avant de traiter la demande.

**Comment faire :**
1.  **Définir une clé secrète :** Ne la codez pas en dur. Utilisez des variables d'environnement.
2.  **Créer une fonction de dépendance** dans `fastapi_main.py` qui vérifie la présence et la validité de la clé.
3.  **Protéger vos endpoints** en ajoutant cette dépendance à ceux qui nécessitent une protection (ex: `/recherche`, `/upload`).

## 2. Configurer CORS pour la Production

Votre configuration actuelle (`allow_origins=["*"]`) est dangereuse en production car elle autorise n'importe quel site web à appeler votre API.

**Principe :** Restreindre les origines autorisées à uniquement le domaine de votre application frontend.

**Comment faire :**
Modifiez la section `CORSMiddleware` dans `fastapi_main.py` pour spécifier les domaines autorisés :
```python
origins = [
    "http://votre-site-web.com",
    "https://votre-site-web.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

## 3. Validation et Limitation des Données d'Entrée

FastAPI et Pydantic valident déjà les types de données, mais vous pouvez ajouter des contraintes plus fines.

**Principe :** Définir des contraintes strictes sur les données que vous acceptez pour éviter des entrées malformées ou trop volumineuses.

**Comment faire :**
Dans votre modèle Pydantic (`QuestionRequest`), utilisez `Field` pour ajouter des contraintes :
```python
from pydantic import BaseModel, Field

class QuestionRequest(BaseModel):
    # La question doit faire entre 3 et 500 caractères
    question: str = Field(..., min_length=3, max_length=500)
```

## 4. Utiliser HTTPS (SSL/TLS)

En production, votre API doit être servie via HTTPS pour chiffrer les communications.

**Principe :** Un "reverse proxy" (comme Nginx ou Caddy) est placé devant votre serveur Uvicorn et gère le chiffrement SSL/TLS.

**Comment faire :**
- Lors du déploiement, configurez un reverse proxy.
- Utilisez un service comme Let's Encrypt pour obtenir un certificat SSL gratuit.
- Le code FastAPI n'a généralement pas besoin d'être modifié.

## 5. Limiter le Taux de Requêtes (Rate Limiting)

Cela protège votre API contre les attaques par déni de service (DoS) et les abus.

**Principe :** Limiter le nombre de requêtes qu'un utilisateur peut faire sur une période donnée (ex: 20 requêtes par minute).

**Comment faire :**
- Ajoutez la bibliothèque `slowapi` à votre projet (`pip install slowapi`).
- Intégrez-la à votre application FastAPI pour limiter les endpoints les plus coûteux comme `/recherche`.

## 6. Gestion des Secrets

Ne jamais coder en dur des informations sensibles (clés d'API, mots de passe) dans le code.

**Principe :** Stocker les secrets dans des variables d'environnement ou un service de gestion de secrets.

**Comment faire :**
- Créez un fichier `.env` (et ajoutez-le à `.gitignore`).
- Utilisez une bibliothèque comme `python-dotenv` pour charger ces variables au démarrage.
- Accédez-y dans le code avec `os.getenv("NOM_DE_LA_VARIABLE")`.
