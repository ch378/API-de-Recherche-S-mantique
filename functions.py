# functions.py

import os
import uuid
from typing import Dict, List, Any

import numpy as np
import redis
from sentence_transformers import SentenceTransformer

from redis.commands.search.field import TextField, VectorField
from redis.commands.search.index_definition import IndexDefinition, IndexType
from redis.commands.search.query import Query

from constraints import (
    REDIS_URL,
    MODELS_DIR,
    SUPPORTED_MODELS,
    DISTANCE_METRIC,
)

redis_client = None
loaded_models: Dict[str, SentenceTransformer] = {}


def connect_redis():
    """
    Connexion à Redis Stack.
    Redis Stack doit être lancé sur localhost:6379.
    """
    global redis_client

    try:
        redis_client = redis.from_url(
            REDIS_URL,
            decode_responses=False
        )

        redis_client.ping()
        print("✅ Connexion Redis Stack réussie")

    except Exception as e:
        raise RuntimeError(
            "Impossible de se connecter à Redis. "
            "Vérifie que Redis Stack est lancé sur le port 6379. "
            f"Détail : {e}"
        )


def load_models():
    """
    Charge les modèles SentenceTransformers.

    Logique :
    - Si le modèle existe déjà dans models/, on le charge localement.
    - Sinon, on le télécharge depuis HuggingFace puis on le sauvegarde dans models/.
    """
    os.makedirs(MODELS_DIR, exist_ok=True)

    for model_name, config in SUPPORTED_MODELS.items():
        local_path = os.path.join(MODELS_DIR, config["local_name"])

        try:
            print(f"🔄 Chargement du modèle : {model_name}")

            if os.path.exists(local_path):
                model = SentenceTransformer(local_path)
                print(f"✅ Modèle chargé localement : {local_path}")
            else:
                model = SentenceTransformer(model_name)
                model.save(local_path)
                print(f"✅ Modèle téléchargé et sauvegardé : {local_path}")

            loaded_models[model_name] = model

        except Exception as e:
            raise RuntimeError(
                f"Erreur pendant le chargement du modèle {model_name} : {e}"
            )


def create_hnsw_indexes():
    """
    Crée automatiquement un index HNSW séparé pour chaque modèle.

    Important :
    - all-MiniLM-L6-v2 produit des vecteurs de dimension 384
    - all-mpnet-base-v2 produit des vecteurs de dimension 768

    Donc chaque modèle doit avoir son propre index Redis.
    """
    if redis_client is None:
        raise RuntimeError("Redis n'est pas connecté")

    for model_name, config in SUPPORTED_MODELS.items():
        index_name = config["index_name"]
        prefix = config["prefix"]
        dimension = config["dimension"]

        try:
            redis_client.ft(index_name).info()
            print(f"ℹ️ Index déjà existant : {index_name}")

        except Exception:
            schema = [
                TextField("text"),
                TextField("model_name"),
                VectorField(
                    "embedding",
                    "HNSW",
                    {
                        "TYPE": "FLOAT32",
                        "DIM": dimension,
                        "DISTANCE_METRIC": DISTANCE_METRIC,
                        "INITIAL_CAP": 1000,
                        "M": 16,
                        "EF_CONSTRUCTION": 200,
                    },
                ),
            ]

            definition = IndexDefinition(
                prefix=[prefix],
                index_type=IndexType.HASH,
            )

            try:
                redis_client.ft(index_name).create_index(
                    fields=schema,
                    definition=definition,
                )

                print(f"✅ Index HNSW créé : {index_name}")

            except Exception as e:
                raise RuntimeError(
                    f"Erreur pendant la création de l'index {index_name} : {e}"
                )


def initialize_system():
    """
    Fonction appelée au démarrage de FastAPI.

    Étapes :
    1. Connexion à Redis Stack
    2. Chargement ou téléchargement des modèles
    3. Création automatique des index HNSW
    """
    connect_redis()
    load_models()
    create_hnsw_indexes()


def get_models_metadata() -> List[Dict[str, Any]]:
    """
    Retourne les informations des modèles disponibles.
    Utilisé par GET /models/
    """
    return [
        {
            "name": model_name,
            "dimension": config["dimension"],
            "index_name": config["index_name"],
            "prefix": config["prefix"],
            "loaded_in_memory": model_name in loaded_models,
        }
        for model_name, config in SUPPORTED_MODELS.items()
    ]


def validate_model(model_name: str):
    """
    Vérifie que le modèle demandé est supporté et chargé.
    """
    if model_name not in SUPPORTED_MODELS:
        raise ValueError("Modèle non supporté")

    if model_name not in loaded_models:
        raise ValueError("Modèle non chargé en mémoire")


def encode_and_store_texts(model_name: str, texts: List[str]) -> Dict[str, Any]:
    """
    Encode une liste de textes avec le modèle choisi
    puis stocke les textes et leurs embeddings dans Redis.
    """
    validate_model(model_name)

    if not texts:
        raise ValueError("La liste des textes ne doit pas être vide")

    cleaned_texts = [
        text.strip()
        for text in texts
        if text and text.strip()
    ]

    if not cleaned_texts:
        raise ValueError("La liste des textes ne contient aucun texte valide")

    model = loaded_models[model_name]
    config = SUPPORTED_MODELS[model_name]
    prefix = config["prefix"]

    try:
        embeddings = model.encode(
            cleaned_texts,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        stored_keys = []

        for text, embedding in zip(cleaned_texts, embeddings):
            doc_id = str(uuid.uuid4())
            redis_key = f"{prefix}{doc_id}"

            embedding_bytes = np.asarray(
                embedding,
                dtype=np.float32
            ).tobytes()

            redis_client.hset(
                redis_key,
                mapping={
                    "text": text,
                    "model_name": model_name,
                    "embedding": embedding_bytes,
                },
            )

            stored_keys.append(redis_key)

        return {
            "message": "Textes encodés et stockés avec succès",
            "model_name": model_name,
            "count": len(stored_keys),
            "redis_keys": stored_keys,
        }

    except Exception as e:
        raise RuntimeError(
            f"Erreur pendant l'encodage ou le stockage : {e}"
        )


def search_similar_texts(
    model_name: str,
    query_text: str,
    top_k: int
) -> Dict[str, Any]:
    """
    Recherche les textes les plus similaires à une requête.

    Étapes :
    1. Encoder la requête
    2. Chercher dans l'index Redis correspondant au modèle
    3. Retourner les textes les plus proches
    """
    validate_model(model_name)

    if not query_text or not query_text.strip():
        raise ValueError("La requête ne doit pas être vide")

    if top_k <= 0:
        raise ValueError("top_k doit être supérieur à 0")

    model = loaded_models[model_name]
    config = SUPPORTED_MODELS[model_name]
    index_name = config["index_name"]

    try:
        query_embedding = model.encode(
            [query_text],
            convert_to_numpy=True,
            normalize_embeddings=True
        )[0]

        query_vector = np.asarray(
            query_embedding,
            dtype=np.float32
        ).tobytes()

        redis_query = (
            Query(f"*=>[KNN {top_k} @embedding $vector AS score]")
            .sort_by("score")
            .return_fields("text", "model_name", "score")
            .dialect(2)
        )

        results = redis_client.ft(index_name).search(
            redis_query,
            query_params={
                "vector": query_vector
            },
        )

        response_results = []

        for doc in results.docs:
            text_value = doc.text
            model_value = doc.model_name

            if isinstance(text_value, bytes):
                text_value = text_value.decode("utf-8")

            if isinstance(model_value, bytes):
                model_value = model_value.decode("utf-8")

            response_results.append(
                {
                    "text": text_value,
                    "model_name": model_value,
                    "score": float(doc.score),
                }
            )

        return {
            "query": query_text,
            "model_name": model_name,
            "top_k": top_k,
            "results_count": len(response_results),
            "results": response_results,
        }

    except Exception as e:
        raise RuntimeError(
            f"Erreur pendant la recherche sémantique : {e}"
        )