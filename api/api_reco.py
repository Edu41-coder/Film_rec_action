from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import JSONResponse
import pandas as pd
from pathlib import Path
from typing import List
from pydantic import BaseModel
import os
from contextlib import asynccontextmanager
import secrets
import json
import joblib
from fastapi.middleware.cors import CORSMiddleware

# ==============================
# Configuration et Variables
# ==============================

# Variables globales pour stocker les DataFrames et modèles
tags_list = None  # Liste des tags disponibles
genres_list = None  # Liste des genres disponibles
tfidf_vectorizer = None  # Modèle TF-IDF chargé
df_movies = None  # DataFrame contenant les films et données dérivées
model = None  # Modèle Machine Learning chargé

# Chemins des fichiers requis
MODELE_FILNAME = Path("best_model.pkl")  # Chemin du modèle ML
MOVIES_FILNAME = Path("movies_with_ratings.csv")  # Fichier des films
TAGS_FILNAME = Path("tfidf.pkl")  # Fichier TF-IDF vectorizer

# Simuler une base de données pour les tokens générés
tokens_db = {}

# Dictionnaire des utilisateurs autorisés (login: mot de passe)
USER_CREDENTIALS = {"admin": "admin", "user1": "123456"}


# ==============================
# Modèles Pydantic
# ==============================


class NotationRequest(BaseModel):
    """
    Requête de notation :
    - `genres`: Liste des genres sélectionnés par l'utilisateur.
    - `tags`: Liste des tags associés au film.
    """

    genres: List[str]
    tags: List[str]


class TokenRequest(BaseModel):
    """
    Requête pour générer un token :
    - `username`: Identifiant de l'utilisateur.
    - `password`: Mot de passe de l'utilisateur.
    """

    username: str
    password: str


# ==============================
# Fonctions Utilitaires
# ==============================


def prepare_input_data(genres: List[str], tags: List[str]) -> pd.DataFrame:
    """
    Prépare les données pour la prédiction en combinant les genres et les tags.

    :param genres: Liste des genres du film.
    :param tags: Liste des tags associés au film.
    :return: DataFrame prêt pour être utilisé par le modèle.
    """
    # Transformation des genres en colonnes binaires
    genre_columns = df_movies.columns
    genre_data = {genre: 1 if genre in genres else 0 for genre in genre_columns}

    # Transformation des tags avec TF-IDF
    tag_string = " ".join(tags)  # Concaténer les tags en une seule chaîne
    tag_vector = tfidf_vectorizer.transform([tag_string]).toarray()[0]
    tag_data = dict(zip(tfidf_vectorizer.get_feature_names_out(), tag_vector))

    # Combiner genres et tags en une seule entrée
    input_data = {**genre_data, **tag_data}

    # Retourner un DataFrame prêt à l'emploi
    return pd.DataFrame([input_data])


def load_data():
    """
    Charger les données et modèles requis pour l'application :
    - `tfidf_vectorizer`: Vectorizer TF-IDF des tags.
    - `df_movies`: Données enrichies des films.
    - `model`: Modèle de prédiction sauvegardé.
    """
    global tags_list, genres_list, tfidf_vectorizer, model, df_movies
    try:
        # Charger le vectorizer TF-IDF
        tfidf_vectorizer = joblib.load(TAGS_FILNAME)

        # Charger et trier les tags disponibles
        tags_list = sorted(tfidf_vectorizer.get_feature_names_out())

        # Charger les données des films
        df_movies = pd.read_csv(MOVIES_FILNAME, sep=",")

        # Identifier les colonnes pour les genres
        genres_list = sorted(
            df_movies.columns.difference(
                ["movieId", "average_rating", "title"]
            ).tolist()
        )

        # Charger le modèle ML
        model = joblib.load(MODELE_FILNAME)
    except Exception as e:
        raise RuntimeError(f"Erreur lors du chargement des fichiers : {str(e)}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestionnaire du cycle de vie de l'application.
    - Chargement des fichiers CSV et modèles au démarrage.
    """
    try:
        load_data()  # Charger les données nécessaires
        print("Application is starting up...")
        yield
    except Exception as e:
        raise RuntimeError(f"Erreur pendant le démarrage : {e}")


# ==============================
# Initialisation de l'application
# ==============================

app = FastAPI(lifespan=lifespan)

# Evite les pb de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Accepter toutes les origines
    allow_credentials=True,  # Autoriser l'envoi de cookies ou d'identifiants
    allow_methods=["*"],  # Autoriser toutes les méthodes HTTP (GET, POST, etc.)
    allow_headers=["*"],  # Autoriser tous les en-têtes
)


# ==============================
# Endpoints
# ==============================


@app.get("/")
async def root():
    """
    Endpoint racine :
    Retourne un message pour confirmer que l'API est en ligne.
    """
    return {"message": "Bienvenue dans l'API de recommandation de films"}


@app.post("/token")
async def generate_basic_token(request: TokenRequest):
    """
    Générer un token pour un utilisateur valide.

    :param request: Contient le `username` et le `password`.
    :return: Token généré si les informations sont valides.
    """
    if (
        request.username not in USER_CREDENTIALS
        or USER_CREDENTIALS[request.username] != request.password
    ):
        raise HTTPException(
            status_code=401, detail="Nom d'utilisateur ou mot de passe incorrect"
        )

    # Générer un token unique
    token = secrets.token_hex(32)
    tokens_db[token] = {"username": request.username}
    return {"access_token": token}


@app.get("/validate-token")
async def validate_token(token: str):
    """
    Valider un token envoyé par l'utilisateur.

    :param token: Token à valider.
    :return: Confirmation si le token est valide ou non.
    """
    token_data = tokens_db.get(token)
    if not token_data:
        raise HTTPException(status_code=401, detail="Token invalide")
    return {"message": "Token valide", "username": token_data["username"]}


@app.get("/tags")
async def get_unique_tags(authorization: str = Header(...)):
    """
    Retourner les tags uniques disponibles dans le système.

    :param authorization: Header contenant le token.
    :return: Liste des tags disponibles.
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Le format du token est invalide")

    token = authorization.split(" ")[1]
    if token not in tokens_db:
        raise HTTPException(status_code=401, detail="Token invalide ou non autorisé")

    try:
        return tags_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne : {str(e)}")


@app.get("/genres")
async def get_unique_genres(authorization: str = Header(...)):
    """
    Retourner les genres uniques disponibles dans le système.

    :param authorization: Header contenant le token.
    :return: Liste des genres disponibles.
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Le format du token est invalide")

    token = authorization.split(" ")[1]
    if token not in tokens_db:
        raise HTTPException(status_code=401, detail="Token invalide ou non autorisé")

    try:
        return genres_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne : {str(e)}")


@app.post("/notation")
async def get_notation(request: NotationRequest, authorization: str = Header(...)):
    """
    Prédire une notation (average_rating) basée sur les genres et tags fournis.

    :param request: Contient les genres et tags à évaluer.
    :param authorization: Header contenant le token.
    :return: Prédiction calculée par le modèle.
    """
    print("Préparer les données pour le modèle")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Le format du token est invalide")

    token = authorization.split(" ")[1]
    if token not in tokens_db:
        raise HTTPException(status_code=401, detail="Token invalide ou non autorisé")

    try:
        # Préparer les données pour le modèle
        input_data = prepare_input_data(genres=request.genres, tags=request.tags)

        # Aligner les colonnes avec celles attendues par le modèle
        input_data = input_data.reindex(columns=model.feature_names_in_, fill_value=0)

        # Prédire la notation
        predicted_rating = round(model.predict(input_data)[0],2)

        return {"rating": str(predicted_rating)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
