# Guide simple pour tester des endpoints et saisir la clé API (Postman)

1. Préparer l'Environment  
    - Créer un Environment (ex: `dev`).  
    - Ajouter les variables : `baseUrl` (ex: https://api.example.com), `apiKey` (laisser vide pour coller la clé).

2. Saisir la clé API  
    - Ouvrir l'Environment → `apiKey` → coller la valeur fournie par l'API.  
    - Sauvegarder l'Environment et le sélectionner.

3. Créer une Collection  
    - Créer une collection nommée (ex: `API - v1`) et y ajouter les requêtes.

4. Créer les requêtes (exemples d'URL)  
    - GET liste : `GET {{baseUrl}}/items`  
    - GET item : `GET {{baseUrl}}/items/{{itemId}}`  
    - POST : `POST {{baseUrl}}/items` (Body JSON)  
    - PUT / DELETE : `PUT/DELETE {{baseUrl}}/items/{{itemId}}`

5. Ajouter la clé API aux requêtes  
    - Méthode recommandée : onglet Headers → ajouter  
      - Key: `x-api-key`  
      - Value: `{{apiKey}}`  
    - Si l'API attend un Bearer : onglet Authorization → Type `Bearer Token` → Token = `{{apiKey}}`

6. Exécuter et vérifier  
    - Envoyer la requête (Send).  
    - Vérifier le statut HTTP et la réponse.

7. Tests rapides (onglet Tests)  
    - Statut 200 :
```javascript
pm.test("Status code is 200", () => pm.response.to.have.status(200));
```
    - Content-Type JSON :
```javascript
pm.test("Content-Type is JSON", () => pm.response.to.have.header("Content-Type", /application\/json/));
```

8. Automatisation basique  
    - Utiliser Collection Runner pour exécuter plusieurs requêtes ou jeux de données CSV/JSON.

Fin. Si besoin, je peux générer une collection Postman exportable avec ces requêtes.
