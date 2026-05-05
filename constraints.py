

REDIS_URL = "redis://localhost:6379"
MODELS_DIR = "models"

DEFAULT_TOP_K = 3
DISTANCE_METRIC = "COSINE"

SUPPORTED_MODELS = {
    "sentence-transformers/all-MiniLM-L6-v2": {
        "local_name": "all-MiniLM-L6-v2",
        "dimension": 384,
        "index_name": "idx_minilm",
        "prefix": "minilm:",
    },
    "sentence-transformers/all-mpnet-base-v2": {
        "local_name": "all-mpnet-base-v2",
        "dimension": 768,
        "index_name": "idx_mpnet",
        "prefix": "mpnet:",
    },
}