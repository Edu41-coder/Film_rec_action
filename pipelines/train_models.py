from dags.train_models import execute_all

# Dossier des données brutes
REP_MODEL = "datasets/model"

# Dossier de sortie pour les fichiers nettoyés
REP_CLEAN = "datasets/clean_data"

if __name__ == "__main__":
    # lance execute_all du  dag load_clean_data
    execute_all(CLEAN=REP_CLEAN, MODEL=REP_MODEL, mlflow_serveur="127.0.0.1")
