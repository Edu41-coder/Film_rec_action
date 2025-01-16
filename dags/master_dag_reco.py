from airflow import DAG

from airflow.operators.python import PythonOperator

from datetime import datetime

from load_clean_data import execute_all as load_clean_data
from analyse_data import execute_all as analyse_data
from optimize_data import execute_all as optimize_data
from split_data import execute_all as split_data
from train_models import execute_all as train_models

# Définir le DAG Airflow
default_args = {
    "owner": "recofilm",
    "depends_on_past": False,
    "start_date": datetime(2023, 12, 1),
    "retries": 2,
}
with DAG(
    dag_id="recofilm_master",
    default_args=default_args,
    schedule_interval=None,  # DAG déclenché manuellement
    catchup=False,
) as dag:

    load_clean_data_task = PythonOperator(
        task_id="load_clean_data_master",
        python_callable=load_clean_data,
        op_kwargs={
            "RAW": "/opt/airflow/datasets/raw_files",  # Dossier source
            "CLEAN": "/opt/airflow/datasets/clean_data",  # Dossier de destination
        },
    )

    analyse_data_task = PythonOperator(
        task_id="analyse_data_task_master",
        python_callable=analyse_data,
        op_kwargs={
            "ANALYSE": "/opt/airflow/datasets/analyses",  # Dossier source
            "CLEAN": "/opt/airflow/datasets/clean_data",  # Dossier de destination
        },
    )

    optimize_data_task = PythonOperator(
        task_id="optimize_data_master",
        python_callable=optimize_data,
        op_kwargs={
            "CLEAN": "/opt/airflow/datasets/clean_data",  # Dossier de destination
        },
    )

    split_data_task = PythonOperator(
        task_id="split_data_master",
        python_callable=split_data,
        op_kwargs={
            "CLEAN": "/opt/airflow/datasets/clean_data",  # Dossier de destination
        },
    )

    train_models_task = PythonOperator(
        task_id="train_models_master",
        python_callable=train_models,
        op_kwargs={
            "CLEAN": "/opt/airflow/datasets/clean_data",  # Dossier de destination
            "MODEL": "/opt/airflow/datasets/model",
            "mlflow_serveur": "mlflow",
        },
    )

    load_clean_data_task >> [analyse_data_task, optimize_data_task] >> split_data_task >> train_models_task
