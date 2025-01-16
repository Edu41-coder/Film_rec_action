import pandas as pd
import matplotlib.pyplot as plt
import os

from airflow import DAG

from airflow.operators.python import PythonOperator

from datetime import datetime


class GeneralDataPipeline:
    """
    Pipeline général pour analyser les données :
    - Chargement des données.
    - Analyse descriptive et sauvegarde.
    - Visualisation des données.
    - Analyse temporelle (année de sortie).
    """

    def __init__(self, file_path):
        """
        Initialise le pipeline avec le chemin d'un fichier CSV.

        :param file_path: Chemin vers le fichier CSV.
        """
        self.file_path = file_path  # Chemin du fichier
        self.data = None  # Contiendra les données chargées

    def load_data(self):
        """
        Charger les données depuis un fichier CSV.
        """
        try:
            self.data = pd.read_csv(self.file_path)  # Charger les données
            print(f"Données chargées depuis {self.file_path} avec succès.")
        except Exception as e:
            print(f"Erreur lors du chargement des données : {e}")

    def describe_data(self):
        """
        Décrire les données : dimensions, colonnes, statistiques descriptives.
        Sauvegarder ces informations dans un fichier texte dans `Analyse`.
        """
        # Construire le chemin du fichier d'analyse
        output_file = os.path.join(
            REP_ANALYSE,
            f"analyse_{os.path.basename(self.file_path).replace('.csv', '.txt')}",
        )

        with open(output_file, "w") as f:
            f.write("===== Description des Données =====\n\n")
            f.write(f"Nombre total de lignes : {self.data.shape[0]}\n")
            f.write(f"Nombre total de colonnes : {self.data.shape[1]}\n\n")

            f.write("Colonnes disponibles :\n")
            for col in self.data.columns:
                f.write(
                    f" - {col} (Type : {self.data[col].dtype}, Valeurs uniques : {self.data[col].nunique()})\n"
                )
            f.write("\n===== Statistiques Descriptives =====\n")
            f.write(self.data.describe(include=[float, int]).transpose().to_string())
            f.write("\n\n===== Aperçu des Données =====\n")
            f.write(self.data.head().to_string())
            f.write("\n")

        print(f"Analyse enregistrée dans : {output_file}")

    def visualize_data(self):
        """
        Générer des visualisations pour les colonnes clés (`rating` et `genres`).
        Sauvegarder les graphiques dans `Analyse`.
        """
        if "rating" in self.data.columns:
            print("\nVisualisation des notes...")
            plt.figure(figsize=(10, 6))
            self.data["rating"].value_counts().sort_index().plot(kind="bar")
            plt.title("Distribution des Notes")
            plt.xlabel("Note")
            plt.ylabel("Nombre d'Évaluations")
            plt.tight_layout()
            plt.savefig(os.path.join(REP_ANALYSE, "ratings_distribution.png"))
            plt.close()

        if "genres" in self.data.columns:
            print("\nVisualisation des genres...")
            genres = self.data["genres"].str.split("|").explode()  # Séparer les genres
            plt.figure(figsize=(10, 6))
            genres.value_counts().plot(kind="bar")
            plt.title("Distribution des Genres")
            plt.xlabel("Genre")
            plt.ylabel("Nombre de Films")
            plt.tight_layout()
            plt.savefig(os.path.join(REP_ANALYSE, "movies_genres_distribution.png"))
            plt.close()

    def analyze_year_distribution(self):
        """
        Analyser la répartition des films par année de sortie.
        Sauvegarder un graphique montrant la distribution temporelle.
        """
        if "title" in self.data.columns:
            print("\nAnalyse de la répartition temporelle...")
            self.data["year"] = self.data["title"].str.extract(
                r"\((\d{4})\)", expand=False
            )  # Extraire l'année
            self.data["year"] = pd.to_numeric(
                self.data["year"], errors="coerce"
            )  # Convertir en numérique

            year_distribution = (
                self.data["year"].value_counts().sort_index()
            )  # Distribution par année

            plt.figure(figsize=(10, 6))
            year_distribution.plot(kind="line")
            plt.title("Répartition Temporelle des Films")
            plt.xlabel("Année")
            plt.ylabel("Nombre de Films")
            plt.tight_layout()
            plt.savefig(os.path.join(REP_ANALYSE, "film_year_distribution.png"))
            plt.close()
        else:
            print("Colonne 'title' introuvable pour l'analyse temporelle.")

    def run_pipeline(self):
        """
        Exécuter toutes les étapes principales du pipeline.
        """
        self.load_data()
        self.describe_data()
        self.visualize_data()
        if "title" in self.data.columns:
            self.analyze_year_distribution()


def execute_all(CLEAN, ANALYSE):
    """
    Exemple d'exécution : appliquer le pipeline sur plusieurs fichiers CSV.
    """
    global REP_CLEAN, REP_ANALYSE
    REP_CLEAN = CLEAN
    REP_ANALYSE = ANALYSE

    os.makedirs(REP_ANALYSE, exist_ok=True)  # Créer le dossier s'il n'existe pas

    csv_files = [
        os.path.join(REP_CLEAN, "cleaned_movies.csv"),
        os.path.join(REP_CLEAN, "cleaned_ratings.csv"),
        os.path.join(REP_CLEAN, "cleaned_ratings.csv"),
    ]
    for file_path in csv_files:
        print(f"\nTraitement du fichier : {file_path}")
        pipeline = GeneralDataPipeline(file_path)
        pipeline.run_pipeline()

    print(f"\nAnalyse terminée pour les fichiers {', '.join(csv_files)}.")


# Définir le DAG Airflow
default_args = {
    "owner": "recofilm",
    "depends_on_past": False,
    "start_date": datetime(2023, 12, 1),
    "retries": 1,
}

with DAG(
    dag_id="1_data_analyse_pipeline",
    default_args=default_args,
    schedule_interval=None,  # DAG déclenché manuellement
    catchup=False,
) as dag:

    # Tâche pour exécuter le pipeline
    run_pipeline_task = PythonOperator(
        task_id="execute_all",
        python_callable=execute_all,
        op_kwargs={
            "ANALYSE": "/opt/airflow/datasets/analyses",  # Dossier source
            "CLEAN": "/opt/airflow/datasets/clean_data",  # Dossier de destination
        },
    )

    run_pipeline_task
