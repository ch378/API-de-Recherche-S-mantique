

from typing import List

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from constraints import DEFAULT_TOP_K
from functions import (
    get_models_metadata,
    encode_and_store_texts,
    search_similar_texts,
)

router = APIRouter()


class EncodeRequest(BaseModel):
    model_name: str = Field(
        ...,
        examples=["sentence-transformers/all-MiniLM-L6-v2"],
    )
    texts: List[str] = Field(
        ...,
        examples=[
            [
                "Le chat dort sur le canapé",
                "Un félin se repose dans le salon",
                "La voiture roule vite",
            ]
        ],
    )


class SearchRequest(BaseModel):
    model_name: str = Field(
        ...,
        examples=["sentence-transformers/all-MiniLM-L6-v2"],
    )
    query: str = Field(
        ...,
        examples=["un chat se repose"],
    )
    top_k: int = Field(
        default=DEFAULT_TOP_K,
        ge=1,
        examples=[3],
    )


@router.get("/models/", status_code=status.HTTP_200_OK)
def get_models():
    try:
        return {
            "models": get_models_metadata()
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur serveur : {str(e)}",
        )


@router.post("/encode/", status_code=status.HTTP_201_CREATED)
def encode_texts(request: EncodeRequest):
    try:
        return encode_and_store_texts(
            model_name=request.model_name,
            texts=request.texts,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur inattendue : {str(e)}",
        )


@router.post("/search/", status_code=status.HTTP_200_OK)
def search_texts(request: SearchRequest):
    try:
        result = search_similar_texts(
            model_name=request.model_name,
            query_text=request.query,
            top_k=request.top_k,
        )

        if result["results_count"] == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Aucun document similaire trouvé pour ce modèle",
            )

        return result

    except HTTPException:
        raise

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur inattendue : {str(e)}",
        )