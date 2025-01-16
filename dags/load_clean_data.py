import pandas as pd
import re
import os

from airflow import DAG

from airflow.operators.python import PythonOperator

from datetime import datetime

def clean_text(cell):
    """
    Nettoie une cellule de texte en supprimant les caractères spéciaux,
    uniformisant en minuscules, et supprimant les espaces superflus.

    :param cell: Le texte à nettoyer.
    :return: Texte nettoyé.
    """
    # Supprimer les caractères non alphabétiques, numériques ou espaces
    cleaned = re.sub(r"[^\w\s]", "", str(cell))
    # Supprimer les espaces en début et en fin, puis mettre en minuscules
    cleaned = cleaned.strip().lower()
    return cleaned


class GeneralDataPipeline:
    """
    Pipeline général pour le chargement, nettoyage, et sauvegarde des données.

    Étapes :
    1. Charger un fichier CSV.
    2. Nettoyer les données (valeurs manquantes, doublons, caractères spéciaux).
    3. Sauvegarder les données nettoyées.
    """

    def __init__(self, file_path):
        """
        Initialisation du pipeline avec le chemin vers un fichier CSV.

        :param file_path: Chemin vers le fichier CSV.
        """
        self.file_path = file_path
        self.data = None  # Contiendra les données chargées

    def load_data(self):
        """
        Charger les données depuis un fichier CSV.
        """
        try:
            self.data = pd.read_csv(self.file_path)
            print(f"Données chargées depuis {self.file_path} avec succès.")
        except Exception as e:
            print(f"Erreur lors du chargement des données : {e}")

    def clean_data(self):
        """
        Nettoyer les données :
        - Supprimer les valeurs manquantes.
        - Nettoyer les colonnes spécifiques (tags, genres).
        - Supprimer les doublons.
        """
        print("\nNettoyage des données...")

        # Nettoyer les tags si la colonne 'tag' est présente
        if "tag" in self.data.columns:
            self.data["tag"] = self.data["tag"].apply(clean_text)

        # Identifier et gérer les valeurs manquantes
        na_count = self.data.isna().sum()  # Compter les NaN par colonne
        if na_count.sum() > 0:
            print(f"Valeurs manquantes détectées :\n{na_count[na_count > 0]}")
            self.data.dropna(inplace=True)  # Supprimer les lignes contenant des NaN
            print("Valeurs manquantes supprimées.")
        else:
            print("Aucune valeur manquante détectée.")

        # Nettoyer chaque cellule pour supprimer les caractères spéciaux
        self.data.applymap(clean_text)

        # Identifier et gérer les doublons
        duplicates_count = self.data.duplicated().sum()  # Compter les doublons
        if duplicates_count > 0:
            self.data.drop_duplicates(inplace=True)  # Supprimer les doublons
            print(f"{duplicates_count} doublons supprimés.")
        else:
            print("Aucun doublon détecté.")

        print("Nettoyage terminé.")

    def save_data(self):
        """
        Sauvegarder les données nettoyées dans un dossier `Datasets/Clean`.
        """

        # Construire le chemin pour le fichier nettoyé
        base_name = os.path.basename(self.file_path)  # Nom du fichier d'origine
        output_file = os.path.join(REP_CLEAN, f"cleaned_{base_name}"
        ) 

        try:
            # Sauvegarder le fichier nettoyé
            self.data.to_csv(output_file, index=False)
            print(f"Données nettoyées sauvegardées dans : {output_file}")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des données : {e}")

    def run_pipeline(self):
        """
        Exécuter toutes les étapes du pipeline :
        - Charger les données.
        - Nettoyer les données.
        - Sauvegarder les données.
        """
        self.load_data()
        self.clean_data()
        self.save_data()


def execute_all(RAW,CLEAN):
    """
    Exemple d'exécution : traiter plusieurs fichiers CSV dans un pipeline automatisé.
    """
    global REP_CLEAN,REP_RAW
    REP_RAW = RAW
    REP_CLEAN = CLEAN

    os.makedirs(REP_CLEAN, exist_ok=True)  # Créer le dossier s'il n'existe pas


    # Liste des fichiers à traiter
    csv_files = [
        os.path.join(REP_RAW, "movies.csv"),
        os.path.join(REP_RAW, "ratings.csv"),
        os.path.join(REP_RAW, "tags.csv"),
    ]

    # Appliquer le pipeline à chaque fichier
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
    dag_id="0_data_cleaning_pipeline",
    default_args=default_args,
    schedule_interval=None,  # DAG déclenché manuellement
    catchup=False,
) as dag:

    # Tâche pour exécuter le pipeline
    run_pipeline_task = PythonOperator(
        task_id="execute_all",
        python_callable=execute_all,
        op_kwargs={
            "RAW": "/opt/airflow/datasets/raw_files",  # Dossier source
            "CLEAN": "/opt/airflow/datasets/clean_data",  # Dossier de destination
        },
    )

    run_pipeline_task