from dags.load_clean_data import execute_all

# Dossier des données brutes
REP_RAW = "datasets/raw_files"

# Dossier de sortie pour les fichiers nettoyés
REP_CLEAN = "datasets/clean_data"

if __name__ == "__main__":
    # lance execute_all du  dag load_clean_data
    execute_all(CLEAN=REP_CLEAN, RAW=REP_RAW)
