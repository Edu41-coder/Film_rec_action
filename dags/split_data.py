from sklearn.model_selection import train_test_split
import pandas as pd
import os

from airflow import DAG

from airflow.operators.python import PythonOperator

from datetime import datetime


def load_data(file_path: str) -> pd.DataFrame:
    """
    Charger les données depuis un fichier CSV.

    :param file_path: Chemin vers le fichier CSV.
    :return: Un DataFrame contenant les données chargées.
    """
    try:
        data = pd.read_csv(file_path)
        return data
    except Exception as e:
        print(f"Erreur lors du chargement des données : {e}")


def split_and_save_movies(df_movies, train_size=0.8, output_dir="Datasets/Model"):
    """
    Séparer le DataFrame df_movies en ensembles d'entraînement et de validation,
    et sauvegarder ces ensembles dans des fichiers CSV.

    :param df_movies: DataFrame contenant les données des films.
    :param train_size: Proportion des données pour l'entraînement (entre 0 et 1).
    :param output_dir: Répertoire où sauvegarder les fichiers.
    """
    # Séparer les données en train et validation
    train_df, validation_df = train_test_split(
        df_movies, train_size=train_size, random_state=42
    )

    # Sauvegarder les fichiers CSV
    train_file = os.path.join(REP_CLEAN, "train_movies.csv")
    validation_file = os.path.join(REP_CLEAN, "validation_movies.csv")

    train_df.to_csv(train_file, index=False)
    validation_df.to_csv(validation_file, index=False)

    print(
        f"Ensemble d'entraînement sauvegardé dans : {train_file} (Taille : {len(train_df)})"
    )
    print(
        f"Ensemble de validation sauvegardé dans : {validation_file} (Taille : {len(validation_df)})"
    )


# Exemple d'exécution pour le MovieLens Dataset
def execute_all(CLEAN):

    global REP_CLEAN
    REP_CLEAN = CLEAN

    df_movies = load_data(os.path.join(REP_CLEAN, "optimized_movies.csv"))
    split_and_save_movies(df_movies=df_movies)


# Définir le DAG Airflow
default_args = {
    "owner": "recofilm",
    "depends_on_past": False,
    "start_date": datetime(2023, 12, 1),
    "retries": 1,
}

with DAG(
    dag_id="3_data_split_pipeline",
    default_args=default_args,
    schedule_interval=None,  # DAG déclenché manuellement
    catchup=False,
) as dag:

    # Tâche pour exécuter le pipeline
    run_pipeline_task = PythonOperator(
        task_id="execute_all",
        python_callable=execute_all,
        op_kwargs={
            "CLEAN": "/opt/airflow/datasets/clean_data",  # Dossier de destination
        },
    )

    run_pipeline_task
