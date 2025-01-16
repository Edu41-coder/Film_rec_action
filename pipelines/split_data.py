from dags.split_data import execute_all

# Dossier de sortie pour les fichiers nettoyés
REP_CLEAN = "datasets/clean_data"

if __name__ == "__main__":
    # lance execute_all du  dag optimize_data
    execute_all(CLEAN=REP_CLEAN)
