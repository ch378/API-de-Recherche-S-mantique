# Devoir 7 — API de Recherche Sémantique

## 1. Présentation du projet

Ce projet consiste à créer une API REST de recherche sémantique avec **FastAPI**, **SentenceTransformers** et **Redis Stack**.

L’objectif est de permettre à un utilisateur de :

1. Envoyer une liste de phrases textuelles.
2. Transformer ces phrases en vecteurs numériques appelés **embeddings**.
3. Stocker ces embeddings dans une base vectorielle Redis Stack.
4. Envoyer une phrase de recherche.
5. Retrouver les phrases les plus proches en sens grâce à une recherche vectorielle HNSW.

Contrairement à une recherche classique par mots-clés, cette API cherche les phrases selon leur **similarité sémantique**, c’est-à-dire leur sens.

Exemple :

```text
Phrase stockée :
"Le chat dort sur le canapé"

Requête :
"Un félin se repose"

Résultat attendu :
"Le chat dort sur le canapé"
```

Même si les mots ne sont pas exactement identiques, le sens est proche.

---

## 2. Stack technique utilisée

Le projet utilise les technologies suivantes :

```text
FastAPI              → Création de l’API REST
SentenceTransformers → Encodage des phrases en embeddings
Redis Stack          → Base de données vectorielle
RedisInsight         → Visualisation de la base Redis
Docker               → Lancement de Redis Stack
Uvicorn              → Serveur ASGI pour exécuter FastAPI
Python               → Langage principal du projet
```

---

## 3. Architecture du projet

```text
rech_Sémantique/
│
├── main.py
├── routes.py
├── functions.py
├── constraints.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── models/
│   ├── all-MiniLM-L6-v2/
│   └── all-mpnet-base-v2/
│
└── venv/
```

---

## 4. Rôle de chaque fichier

### `main.py`

C’est le point d’entrée de l’application FastAPI.

Il permet de :

```text
- créer l’application FastAPI
- lancer l’initialisation automatique au démarrage
- connecter l’application à Redis Stack
- charger les modèles SentenceTransformers
- créer les index HNSW
- inclure les routes de l’API
```

### `routes.py`

Ce fichier contient les endpoints de l’API :

```text
GET  /models/
POST /encode/
POST /search/
```

Il gère aussi les erreurs HTTP avec les bons codes de statut.

### `functions.py`

Ce fichier contient la logique principale du projet :

```text
- se connecter à Redis Stack
- charger les modèles
- télécharger les modèles si nécessaire
- créer les index HNSW
- encoder les textes
- stocker les embeddings dans Redis
- rechercher les phrases similaires
```

### `constraints.py`

Ce fichier contient la configuration du projet :

```text
- URL Redis
- noms des modèles
- dimensions des embeddings
- noms des index Redis
- préfixes des clés Redis
- nombre de résultats par défaut
- type de distance utilisé
```

### `models/`

Ce dossier contient les modèles téléchargés localement.

Au premier lancement, les modèles sont téléchargés depuis HuggingFace puis sauvegardés dans ce dossier.

Après téléchargement, la structure devient :

```text
models/
├── all-MiniLM-L6-v2/
└── all-mpnet-base-v2/
```

### `requirements.txt`

Ce fichier contient les bibliothèques Python nécessaires au projet.

---

## 5. Modèles utilisés

Le projet supporte deux modèles SentenceTransformers :

```text
sentence-transformers/all-MiniLM-L6-v2
sentence-transformers/all-mpnet-base-v2
```

### `sentence-transformers/all-MiniLM-L6-v2`

Ce modèle produit des embeddings de dimension :

```text
384
```

Avantages :

```text
- léger
- rapide
- adapté aux tests
- consomme moins de mémoire
```

### `sentence-transformers/all-mpnet-base-v2`

Ce modèle produit des embeddings de dimension :

```text
768
```

Avantages :

```text
- plus puissant
- souvent plus précis
- meilleure qualité de représentation sémantique
```

Inconvénient :

```text
- plus lourd
- plus lent que MiniLM
```

---

## 6. Pourquoi deux index Redis séparés ?

Chaque modèle produit des vecteurs de taille différente :

```text
all-MiniLM-L6-v2  → vecteur de 384 dimensions
all-mpnet-base-v2 → vecteur de 768 dimensions
```

Redis ne peut pas comparer un vecteur de 384 dimensions avec un vecteur de 768 dimensions.

Donc chaque modèle possède son propre index HNSW :

```text
idx_minilm → pour all-MiniLM-L6-v2
idx_mpnet  → pour all-mpnet-base-v2
```

Les documents sont aussi stockés avec des préfixes différents :

```text
minilm:xxxx → documents encodés avec MiniLM
mpnet:xxxx  → documents encodés avec MPNet
```

---

## 7. Redis Stack et HNSW

Redis Stack est utilisé comme base de données vectorielle.

Il permet de :

```text
- stocker des embeddings
- créer des index vectoriels
- rechercher les vecteurs les plus proches
```

L’algorithme utilisé pour la recherche est :

```text
HNSW : Hierarchical Navigable Small World
```

HNSW permet de rechercher rapidement les vecteurs les plus proches sans comparer tous les vecteurs un par un.

---

## 8. Installation du projet

### Étape 1 : créer le dossier du projet

```powershell
mkdir rech_Sémantique
cd rech_Sémantique
```

### Étape 2 : créer un environnement virtuel

```powershell
py -m venv venv
```

### Étape 3 : activer l’environnement virtuel

Avec PowerShell :

```powershell
.\venv\Scripts\Activate.ps1
```

Si PowerShell bloque l’activation :

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

Puis réessayer :

```powershell
.\venv\Scripts\Activate.ps1
```

Quand le venv est activé, on doit voir :

```text
(venv)
```

au début de la ligne du terminal.

### Étape 4 : installer les dépendances

```powershell
python -m pip install --upgrade pip
```

Puis :

```powershell
python -m pip install -r requirements.txt
```

Ou installation manuelle :

```powershell
python -m pip install fastapi "uvicorn[standard]" redis sentence-transformers numpy pydantic
```

---

## 9. Contenu du fichier `requirements.txt`

```txt
fastapi
uvicorn[standard]
redis
sentence-transformers
numpy
pydantic
```

---

## 10. Lancer Redis Stack

Le projet nécessite **Redis Stack**, pas Redis classique.

### Lancer Redis Stack avec Docker

```powershell
docker run -d --name redis-stack -p 6379:6379 -p 8001:8001 redis/redis-stack:latest
```

### Si le conteneur existe déjà

```powershell
docker start redis-stack
```

### Vérifier que Redis Stack fonctionne

```powershell
docker ps
```

On doit voir un conteneur nommé :

```text
redis-stack
```

---

## 11. Ouvrir RedisInsight

RedisInsight permet de visualiser la base Redis.

Ouvrir dans le navigateur :

```text
http://localhost:8001
```

Connexion :

```text
Host: localhost
Port: 6379
```

Après avoir utilisé l’endpoint `/encode/`, on peut voir des clés comme :

```text
minilm:xxxxxxxx
mpnet:xxxxxxxx
```

---

## 12. Télécharger les modèles avant le lancement

Les modèles peuvent être téléchargés automatiquement au démarrage de l’API.

Mais il est aussi possible de les télécharger avant avec le fichier :

```text
download_models.py
```

Commande :

```powershell
python download_models.py
```

Après téléchargement, on obtient :

```text
models/
├── all-MiniLM-L6-v2/
└── all-mpnet-base-v2/
```

---

## 13. Lancer l’API

Dans le terminal avec le venv activé :

```powershell
python -m uvicorn main:app --reload
```

Si tout fonctionne, on voit :

```text
Uvicorn running on http://127.0.0.1:8000
Application startup complete
```

---

## 14. Documentation Swagger

FastAPI génère automatiquement une documentation interactive.

Ouvrir dans le navigateur :

```text
http://127.0.0.1:8000/docs
```

---

## 15. Endpoints de l’API

### `GET /`

Endpoint d’accueil.

URL :

```text
http://127.0.0.1:8000/
```

Réponse attendue :

```json
{
  "message": "Bienvenue dans l'API de Recherche Sémantique",
  "documentation": "/docs",
  "endpoints": {
    "models": "GET /models/",
    "encode": "POST /encode/",
    "search": "POST /search/"
  }
}
```

---

### `GET /models/`

Cet endpoint retourne la liste des modèles disponibles.

URL :

```text
http://127.0.0.1:8000/models/
```

Méthode :

```text
GET
```

Réponse attendue :

```json
{
  "models": [
    {
      "name": "sentence-transformers/all-MiniLM-L6-v2",
      "dimension": 384,
      "index_name": "idx_minilm",
      "prefix": "minilm:",
      "loaded_in_memory": true
    },
    {
      "name": "sentence-transformers/all-mpnet-base-v2",
      "dimension": 768,
      "index_name": "idx_mpnet",
      "prefix": "mpnet:",
      "loaded_in_memory": true
    }
  ]
}
```

---

### `POST /encode/`

Cet endpoint reçoit une liste de textes et un nom de modèle.

Il encode les textes en embeddings et les stocke dans Redis.

URL :

```text
http://127.0.0.1:8000/encode/
```

Méthode :

```text
POST
```

Body JSON :

```json
{
  "model_name": "sentence-transformers/all-MiniLM-L6-v2",
  "texts": [
    "Le chat dort sur le canapé",
    "Un félin se repose dans le salon",
    "La voiture roule vite",
    "Un étudiant apprend FastAPI",
    "Redis est une base de données rapide"
  ]
}
```

Réponse attendue :

```json
{
  "message": "Textes encodés et stockés avec succès",
  "model_name": "sentence-transformers/all-MiniLM-L6-v2",
  "count": 5,
  "redis_keys": [
    "minilm:xxxxxxxx",
    "minilm:xxxxxxxx",
    "minilm:xxxxxxxx"
  ]
}
```

---

### `POST /search/`

Cet endpoint reçoit une phrase de recherche, un modèle et un nombre de résultats.

Il encode la requête et cherche les textes les plus proches dans Redis.

URL :

```text
http://127.0.0.1:8000/search/
```

Méthode :

```text
POST
```

Body JSON :

```json
{
  "model_name": "sentence-transformers/all-MiniLM-L6-v2",
  "query": "un chat se repose",
  "top_k": 3
}
```

Réponse attendue :

```json
{
  "query": "un chat se repose",
  "model_name": "sentence-transformers/all-MiniLM-L6-v2",
  "top_k": 3,
  "results_count": 3,
  "results": [
    {
      "text": "Un félin se repose dans le salon",
      "model_name": "sentence-transformers/all-MiniLM-L6-v2",
      "score": 0.15
    },
    {
      "text": "Le chat dort sur le canapé",
      "model_name": "sentence-transformers/all-MiniLM-L6-v2",
      "score": 0.22
    }
  ]
}
```

Remarque :

```text
Avec la distance COSINE, plus le score est petit, plus le texte est similaire.
```

---

## 16. Tester avec Postman

### Tester `GET /models/`

Dans Postman :

```text
Method: GET
URL: http://127.0.0.1:8000/models/
```

Cliquer sur :

```text
Send
```

### Tester `POST /encode/`

Dans Postman :

```text
Method: POST
URL: http://127.0.0.1:8000/encode/
```

Aller dans :

```text
Body → raw → JSON
```

Coller :

```json
{
  "model_name": "sentence-transformers/all-MiniLM-L6-v2",
  "texts": [
    "Le chat dort sur le canapé",
    "Un félin se repose dans le salon",
    "La voiture roule vite",
    "Un étudiant apprend FastAPI",
    "Redis est une base de données rapide"
  ]
}
```

Cliquer sur :

```text
Send
```

### Tester `POST /search/`

Dans Postman :

```text
Method: POST
URL: http://127.0.0.1:8000/search/
```

Aller dans :

```text
Body → raw → JSON
```

Coller :

```json
{
  "model_name": "sentence-transformers/all-MiniLM-L6-v2",
  "query": "un chat se repose",
  "top_k": 3
}
```

Cliquer sur :

```text
Send
```

---

## 17. Ordre de test important

Il faut tester dans cet ordre :

```text
1. GET /models/
2. POST /encode/
3. POST /search/
```

Pourquoi ?

```text
/search/ cherche dans les textes déjà stockés.
Si /encode/ n’a pas encore été utilisé, Redis ne contient aucun texte.
```

---

## 18. Fonctionnement interne de la recherche

Quand on appelle `/encode/` :

```text
Texte
↓
SentenceTransformer
↓
Embedding vectoriel
↓
Redis Stack
↓
Index HNSW
```

Quand on appelle `/search/` :

```text
Requête utilisateur
↓
SentenceTransformer
↓
Embedding de la requête
↓
Recherche KNN dans Redis HNSW
↓
Résultats les plus similaires
```

---

## 19. Exemple de recherche sémantique

Textes stockés :

```text
Le chat dort sur le canapé
Un félin se repose dans le salon
La voiture roule vite
Un étudiant apprend FastAPI
Redis est une base de données rapide
```

Requête :

```text
un chat se repose
```

Résultats attendus :

```text
1. Un félin se repose dans le salon
2. Le chat dort sur le canapé
```

Même si les mots sont différents, le sens est proche.

---

## 20. Gestion des erreurs

Le projet gère plusieurs erreurs.

### Modèle non supporté

Si on envoie :

```json
{
  "model_name": "fake-model",
  "texts": ["Bonjour"]
}
```

Réponse :

```json
{
  "detail": "Modèle non supporté"
}
```

Code HTTP :

```text
400 Bad Request
```

### Liste de textes vide

Si on envoie :

```json
{
  "model_name": "sentence-transformers/all-MiniLM-L6-v2",
  "texts": []
}
```

Réponse :

```json
{
  "detail": "La liste des textes ne doit pas être vide"
}
```

Code HTTP :

```text
400 Bad Request
```

### Requête vide

Si on envoie :

```json
{
  "model_name": "sentence-transformers/all-MiniLM-L6-v2",
  "query": "",
  "top_k": 3
}
```

Réponse :

```json
{
  "detail": "La requête ne doit pas être vide"
}
```

Code HTTP :

```text
400 Bad Request
```

### Aucun résultat trouvé

Si aucun document n’a été stocké avant la recherche :

```json
{
  "detail": "Aucun document similaire trouvé pour ce modèle"
}
```

Code HTTP :

```text
404 Not Found
```

### Erreur Redis

Si Redis Stack n’est pas lancé :

```json
{
  "detail": "Impossible de se connecter à Redis..."
}
```

Code HTTP :

```text
500 Internal Server Error
```

---

## 21. Commandes utiles

### Activer le venv

```powershell
.\venv\Scripts\Activate.ps1
```

### Installer les dépendances

```powershell
python -m pip install -r requirements.txt
```

### Lancer Redis Stack

```powershell
docker start redis-stack
```

### Créer Redis Stack si nécessaire

```powershell
docker run -d --name redis-stack -p 6379:6379 -p 8001:8001 redis/redis-stack:latest
```

### Lancer FastAPI

```powershell
python -m uvicorn main:app --reload
```

### Tester l’import du projet

```powershell
python -c "import main; print('main OK')"
```

### Tester Redis import

```powershell
python -c "from redis.commands.search.index_definition import IndexDefinition, IndexType; print('Redis import OK')"
```

---

## 22. Problèmes fréquents et solutions

### Problème 1 : `No module named fastapi`

Solution :

```powershell
python -m pip install fastapi
```

Ou :

```powershell
python -m pip install -r requirements.txt
```

### Problème 2 : `No module named uvicorn`

Solution :

```powershell
python -m pip install "uvicorn[standard]"
```

### Problème 3 : `No module named redis.commands.search.indexDefinition`

Cause :

```text
Mauvais nom d’import.
```

Il faut utiliser :

```python
from redis.commands.search.index_definition import IndexDefinition, IndexType
```

et non :

```python
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
```

### Problème 4 : Redis ne se connecte pas

Solution :

```powershell
docker start redis-stack
```

ou :

```powershell
docker run -d --name redis-stack -p 6379:6379 -p 8001:8001 redis/redis-stack:latest
```

### Problème 5 : PowerShell bloque le venv

Solution :

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

Puis :

```powershell
.\venv\Scripts\Activate.ps1
```

---

## 23. Conclusion

Ce projet permet de construire un mini moteur de recherche sémantique.

Il utilise :

```text
FastAPI pour l’API
SentenceTransformers pour convertir les phrases en embeddings
Redis Stack pour stocker et rechercher les vecteurs
HNSW pour accélérer la recherche de similarité
```

Le point le plus important du projet est que chaque modèle possède son propre index Redis HNSW :

```text
idx_minilm pour all-MiniLM-L6-v2
idx_mpnet pour all-mpnet-base-v2
```

Cela permet d’éviter de mélanger des vecteurs de dimensions différentes et garantit une recherche correcte.#   A P I - d e - R e c h e r c h e - S - m a n t i q u e  
 