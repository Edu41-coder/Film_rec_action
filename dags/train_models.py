from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import mean_squared_error
import pandas as pd
import pickle
import os
from sklearn.linear_model import LinearRegression, ElasticNet
from xgboost import XGBRegressor
import mlflow
import mlflow.sklearn
from sklearn.neighbors import KNeighborsRegressor

from airflow import DAG

from airflow.operators.python import PythonOperator

from datetime import datetime

# Créer le dossier s'il n'existe pas


def init_data(train_file, validation_file, target_column):
    """
    Charger et préparer les données pour l'entraînement et la validation.

    :param train_file: Chemin vers le fichier d'entraînement.
    :param validation_file: Chemin vers le fichier de validation.
    :param target_column: Colonne cible (valeur à prédire).
    :return: X_train, y_train, X_validation, y_validation
    """
    train_df = pd.read_csv(train_file)  # Charger les données d'entraînement
    validation_df = pd.read_csv(validation_file)  # Charger les données de validation

    # Supprimer les valeurs manquantes
    train_df = train_df.dropna()
    validation_df = validation_df.dropna()

    # Supprimer la colonne inutile 'title_x'
    train_df = train_df.drop(columns=["title_x"])
    validation_df = validation_df.drop(columns=["title_x"])

    # Diviser les données en caractéristiques (X) et cible (y)
    X_train = train_df.drop(columns=[target_column])
    y_train = train_df[target_column]

    X_validation = validation_df.drop(columns=[target_column])
    y_validation = validation_df[target_column]

    return X_train, y_train, X_validation, y_validation


def init_grid(rf, model_type):
    """
    Initialiser une recherche de grille (GridSearchCV) pour optimiser les hyperparamètres.

    :param rf: Estimateur (modèle de régression).
    :param model_type: Type de modèle.
    :return: Un objet GridSearchCV configuré.
    """
    if model_type == "XGBoost":
        param_grid = {
            "n_estimators": [100, 200, 300],
            "max_depth": [3, 5, 7],
            "learning_rate": [0.01, 0.1, 0.2],
            "subsample": [0.6, 0.8, 1.0],
            "colsample_bytree": [0.6, 0.8, 1.0],
        }
    elif model_type == "ElasticNet":
        param_grid = {
            "alpha": [0.01, 0.1, 1, 10, 100],  # Paramètre de régularisation
            "l1_ratio": [0.2, 0.5, 0.8, 1.0],  # Ratio L1/L2
        }
    elif model_type == "KNeighborsRegressor":
        param_grid = {
            "n_neighbors": [3, 5, 10, 15],
            "weights": ["uniform", "distance"],
            "p": [1, 2],
        }

    # Configurer GridSearchCV
    return GridSearchCV(
        estimator=rf,
        param_grid=param_grid,
        scoring="neg_mean_squared_error",  # Minimise l'erreur quadratique moyenne
        cv=5,  # Validation croisée à 5 plis
        n_jobs=-1,  # Utiliser tous les cœurs disponibles
        verbose=2,  # Afficher des informations détaillées
    )


def evaluate_model(model, y_validation, X_validation, model_type):
    """
    Évaluer le modèle sur l'ensemble de validation.

    :param model: Modèle entraîné.
    :param y_validation: Cible réelle de l'ensemble de validation.
    :param X_validation: Caractéristiques de l'ensemble de validation.
    :param model_type: Type de modèle.
    :return: Erreur quadratique moyenne (MSE).
    """
    y_pred = model.predict(X_validation)  # Prédire les valeurs cibles
    mse = mean_squared_error(y_validation, y_pred)  # Calculer le MSE
    print(f"{model_type} : Mean Squared Error (MSE) : {mse}")
    return mse


def train_with_grid(
    train_file: str,
    validation_file: str,
    target_column: str,
    model_type: str,
    mlflow_serveur : str,
):
    """
    Entraîner un modèle avec recherche d'hyperparamètres (GridSearchCV).

    :param train_file: Chemin vers le fichier d'entraînement.
    :param validation_file: Chemin vers le fichier de validation.
    :param target_column: Nom de la colonne cible.
    :param model_type: Type de modèle (ex. : XGBoost, ElasticNet).
    :param mlflow_serveur: nom du serveur mlflow
    :return: MSE et le modèle entraîné.
    """
    # Charger les données
    X_train, y_train, X_validation, y_validation = init_data(
        train_file, validation_file, target_column
    )
    mlflow.set_tracking_uri(f"http://{mlflow_serveur}:5000")

    # Démarrer une session MLflow pour suivre l'entraînement
    with mlflow.start_run(run_name=model_type, nested=True):
        if model_type == "LinearRegression":
            # Entraîner un modèle de régression linéaire
            search = LinearRegression()
            best_model = search.fit(X_train, y_train)
        else:
            # Configurer le modèle et la recherche de grille
            if model_type == "XGBoost":
                rf = XGBRegressor()
            elif model_type == "KNeighborsRegressor":
                rf = KNeighborsRegressor()
            elif model_type == "ElasticNet":
                rf = ElasticNet()
            search = init_grid(rf, model_type)
            search.fit(X_train, y_train)  # Entraîner la recherche de grille
            best_model = search.best_estimator_  # Récupérer le meilleur modèle
            mlflow.log_params(
                search.best_params_
            )  # Enregistrer les meilleurs hyperparamètres

        mse = evaluate_model(
            best_model, y_validation, X_validation, model_type
        )  # Évaluer le modèle
        mlflow.log_metric("mse", mse)  # Enregistrer le MSE dans MLflow
    mlflow.end_run()
    return mse, best_model


def get_best_model(train_file, validation_file, target_column, mlflow_serveur):
    """
    Identifier et retourner le meilleur modèle en fonction du MSE.

    :param train_file: Chemin vers le fichier d'entraînement.
    :param validation_file: Chemin vers le fichier de validation.
    :param target_column: Nom de la colonne cible.
    :return: Meilleur modèle entraîné.
    """
    # tested_model = ["LinearRegression", "XGBoost", "ElasticNet", "KNeighborsRegressor"]
    tested_model = ["LinearRegression"]

    best_mse, best_model = None, None

    # Tester plusieurs modèles
    for model_type in tested_model:
        mse, model = train_with_grid(
            train_file, validation_file, target_column, model_type, mlflow_serveur
        )
        if best_mse is None or mse < best_mse:
            best_model = model
            best_mse = mse
            print(f"Best so far: {model_type}")

    return best_model


def execute_all(CLEAN, MODEL, mlflow_serveur):

    global REP_CLEAN, REP_MODEL
    REP_CLEAN = CLEAN
    REP_MODEL = MODEL

    os.makedirs(REP_MODEL, exist_ok=True)
    try:
        train_file = os.path.join(REP_CLEAN, "train_movies.csv")
        validation_file = os.path.join(REP_CLEAN, "validation_movies.csv")
        # Obtenir le meilleur modèle
        best_model = get_best_model(
            train_file, validation_file, target_column="average_rating",mlflow_serveur=mlflow_serveur
        )
        with open(os.path.join(REP_MODEL, "best_model.pkl"), "wb") as filehandler:
            pickle.dump(best_model, filehandler)
        print("Best model sauvegardé dans Models/best_model.pkl")
    except Exception as e:
        print("Problème lors de l'analyse")
        print(e)


# Définir le DAG Airflow
default_args = {
    "owner": "recofilm",
    "depends_on_past": False,
    "start_date": datetime(2023, 12, 1),
    "retries": 1,
}

with DAG(
    dag_id="4_model_train_pipeline",
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
            "MODEL": "/opt/airflow/datasets/model",
            "mlflow_serveur": "mlflow"
        },
    )

    run_pipeline_task
