import pandas as pd
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from joblib import dump


from airflow import DAG

from airflow.operators.python import PythonOperator

from datetime import datetime


def load_data(file_path: str) -> pd.DataFrame:
    """
    Charger les données depuis un fichier CSV.

    :param file_path: Chemin du fichier CSV.
    :return: Un DataFrame contenant les données chargées.
    """
    try:
        data = pd.read_csv(file_path)  # Charger les données CSV dans un DataFrame
        return data
    except Exception as e:
        print(f"Erreur lors du chargement des données : {e}")  # Afficher une erreur si le fichier ne peut pas être chargé


def calculate_average_rating(movies_df: pd.DataFrame, ratings_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcule le score moyen de chaque film à partir des évaluations et transforme
    les genres en colonnes binaires.

    :param movies_df: DataFrame contenant les informations sur les films.
    :param ratings_df: DataFrame contenant les notes des utilisateurs.
    :return: DataFrame enrichi avec les scores moyens et les genres transformés.
    """
    # Calcul de la moyenne des évaluations pour chaque film
    average_ratings = ratings_df.groupby('movieId')['rating'].mean().reset_index()
    average_ratings.rename(columns={'rating': 'average_rating'}, inplace=True)

    # Fusionner les évaluations moyennes avec les informations des films
    movies_with_ratings = movies_df.merge(average_ratings, on='movieId', how='left')

    # Supprimer les films sans évaluation
    movies_with_ratings = movies_with_ratings.dropna(subset=['average_rating'])

    # Transformer les genres en colonnes binaires
    genre_columns = movies_with_ratings['genres'].str.get_dummies('|')
    movies_with_ratings = pd.concat([movies_with_ratings, genre_columns], axis=1)

  

    # Supprimer la colonne 'genres' après transformation
    movies_with_ratings = movies_with_ratings.drop(columns=['genres'])

    movies_with_ratings.to_csv(os.path.join(REP_CLEAN,'movies_with_ratings.csv'), index=False)

    return movies_with_ratings


def process_tags_with_tfidf(movies_df: pd.DataFrame, tags_df: pd.DataFrame) -> pd.DataFrame:
    """
    Représente les tags sous forme de vecteurs pondérés à l'aide de TF-IDF.

    :param movies_df: DataFrame des films enrichi avec les scores moyens.
    :param tags_df: DataFrame contenant les tags des films.
    :return: DataFrame enrichi avec les caractéristiques TF-IDF des tags.
    """
    print("\nTraitement des tags avec TF-IDF...")

    # Vérifier si la colonne 'tag' est présente
    if 'tag' not in tags_df.columns:
        raise ValueError("Le DataFrame des tags doit contenir une colonne 'tag'.")

    # Supprimer les tags vides et les combiner par film
    tags_df = tags_df.dropna(subset=['tag'])  # Supprimer les valeurs manquantes
    tags_grouped = tags_df.groupby('movieId')['tag'].apply(lambda x: ' '.join(x)).reset_index()

    # Appliquer TF-IDF pour transformer les tags en vecteurs pondérés
    tfidf_vectorizer = TfidfVectorizer(max_features=2000, stop_words='english')  # Max 2000 mots-clés
    tfidf_matrix = tfidf_vectorizer.fit_transform(tags_grouped['tag'])

    # Sauvegarder le modèle TF-IDF pour réutilisation
    dump(tfidf_vectorizer, os.path.join(REP_CLEAN,"tfidf.pkl"))

    # Transformer la matrice TF-IDF en DataFrame
    tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=tfidf_vectorizer.get_feature_names_out())
    tfidf_df['movieId'] = tags_grouped['movieId'].values  # Ajouter les ID des films

    # Fusionner les données TF-IDF avec les informations des films
    movies_with_ratings = movies_df.merge(tfidf_df, on='movieId', how='left')

    return movies_with_ratings


def save_data(file_path: str, df: pd.DataFrame) -> bool:
    """
    Sauvegarde les données nettoyées dans un fichier CSV.

    :param file_path: Chemin du fichier de sortie.
    :param df: DataFrame à sauvegarder.
    :return: Indique si la sauvegarde a réussi.
    """


    try:
        df.to_csv(file_path, index=False)  # Sauvegarde des données sans index
        print(f"Données sauvegardées avec succès dans {file_path}")
        return True
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des données : {e}")
        return False


# Exemple d'exécution pour le MovieLens Dataset
def execute_all(CLEAN):

    global REP_CLEAN
    REP_CLEAN = CLEAN

    # Charger les données depuis les fichiers CSV
    df_movies = load_data(os.path.join(REP_CLEAN,"cleaned_movies.csv"))
    df_ratings = load_data(os.path.join(REP_CLEAN,"cleaned_ratings.csv"))
    df_tags = load_data(os.path.join(REP_CLEAN,"cleaned_tags.csv"))


    # Calculer les scores moyens et transformer les genres
    df_movies = calculate_average_rating(df_movies, df_ratings)

    # Ajouter les vecteurs TF-IDF pour les tags
    df_movies = process_tags_with_tfidf(movies_df=df_movies, tags_df=df_tags)

    # Sauvegarder les données optimisées dans un fichier
    save_data(os.path.join(REP_CLEAN,'optimized_movies.csv'), df_movies)


# Définir le DAG Airflow
default_args = {
    "owner": "recofilm",
    "depends_on_past": False,
    "start_date": datetime(2023, 12, 1),
    "retries": 1,
}

with DAG(
    dag_id="2_data_optimize_pipeline",
    default_args=default_args,
    schedule_interval=None,  # DAG déclenché manuellement
    catchup=False,
) as dag:

    # Tâche pour exécuter le pipeline
    run_pipeline_task = PythonOperator(
        task_id="execute_all",
        python_callable=execute_all ,
         op_kwargs={
            "CLEAN": "/opt/airflow/datasets/clean_data",  # Dossier de destination
        },
    )

    run_pipeline_task