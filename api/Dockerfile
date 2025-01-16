# Utiliser une image Python comme base
FROM python:3.9-slim
# Utilise une image légère de Python 3.9 basée sur Debian (slim), optimisée pour réduire la taille tout en conservant les fonctionnalités nécessaires.

# Définir le répertoire de travail
WORKDIR /app
# Définit `/app` comme répertoire de travail dans le conteneur.
# Toutes les commandes exécutées et fichiers copiés dans le conteneur seront relatives à ce répertoire.

# Copier les dépendances
COPY ../api/requirements.txt .
# Copie le fichier `requirements.txt` depuis le répertoire `../api` de la machine hôte vers le conteneur, dans `/app`.

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt
# Installe les bibliothèques Python spécifiées dans `requirements.txt`.
# L'option `--no-cache-dir` empêche pip de stocker les fichiers d'installation en cache, réduisant ainsi la taille de l'image finale.

# Copier le code source de l'API
COPY ../api/api_reco.py /app
# Copie le fichier principal de l'API (`api_reco.py`) depuis le répertoire `../api` de la machine hôte vers le répertoire `/app` dans le conteneur.

# Copier les fichiers du modèle et les données nécessaires
COPY ../datasets/model/best_model.pkl /app/best_model.pkl
# Copie le fichier du modèle Machine Learning (`best_model.pkl`) depuis `../datasets/model` vers `/app` dans le conteneur.

COPY ../datasets/clean_data/movies_with_ratings.csv /app/movies_with_ratings.csv
# Copie un fichier CSV nettoyé (`movies_with_ratings.csv`) contenant les données des films vers le répertoire `/app` dans le conteneur.

COPY ../datasets/clean_data/tfidf.pkl /app/tfidf.pkl
# Copie un fichier supplémentaire (`tfidf.pkl`) utilisé par l'application vers le répertoire `/app` dans le conteneur.

# Exposer le port 7010
EXPOSE 7010
# Indique que le conteneur écoute sur le port 7010 pour les connexions externes.
# Cette instruction est informative et ne mappe pas automatiquement le port (cela est fait via `docker run` ou `docker-compose.yml`).

# Définir la commande par défaut pour exécuter l'application
CMD ["uvicorn", "api_reco:app", "--host", "0.0.0.0", "--port", "7010"]
# Définit la commande par défaut lorsque le conteneur démarre :
# - `uvicorn` : serveur ASGI rapide pour exécuter les applications FastAPI.
# - `api_reco:app` : spécifie le module Python (`api_reco`) et l'application FastAPI (`app`) à exécuter.
# - `--host 0.0.0.0` : permet d'accepter des connexions externes (hors du conteneur).
# - `--port 7010` : indique que l'application FastAPI écoutera sur le port 7010.
