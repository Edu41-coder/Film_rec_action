from dags.analyse_data import execute_all

# Dossier de sortie pour les fichiers nettoyés
REP_CLEAN = "datasets/clean_data"

REP_ANALYSE = "datasets/analyses"

if __name__ == "__main__":
    # lance execute_all du  dag analyse_data
    execute_all(CLEAN=REP_CLEAN, ANALYSE=REP_ANALYSE)
