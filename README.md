<<<<<<< HEAD
# Initialisation de l'environnement
```
. ./init_env.sh
```
Répondez "y" à toutes les questions et assurez-vous de suivre les instructions indiquées à la fin :
- Exporter le PYTHONPATH.
- Sourcer l'environnement Python.

# Compilation et lancement de l'application

Si vous passez par Airflow, exécutez le DAG `recofilm_master` et attendez qu'il se termine (**dans ce cas il ne faudra pas utilisé dvc dans le script `init_appli.sh`**).

Si vous ne passez pas par Airflow, vous pouvez utiliser DVC et lancer directement le script `init_appli.sh`.


```
. ./init_appli.sh
```

L'application sera accessible à l'adresse suivante : http://127.0.0.1:7000
=======
# Film_rec_action
>>>>>>> 8fbde1cd17b144a9ced77131f3ddc3dacf5dc72b
