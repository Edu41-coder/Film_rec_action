#!/bin/bash

# Arrêter le script en cas d'erreur
set -e

# Fonction pour demander une confirmation à l'utilisateur
confirm() {
    while true; do
        read -rp "$1 (y/n): " response
        case "$response" in
            [Yy]*) return 0 ;;  # Continuer si "y"
            [Nn]*) return 1 ;;  # Arrêter si "n"
            *) echo "Veuillez répondre par 'y' ou 'n'." ;;
        esac
    done
}

echo "----------------------------------------"
echo "🚀 Initialisation du projet"
echo "----------------------------------------"



# Demander si l'utilisateur souhaite supprimer les répertoires existants
if confirm "Voulez-vous supprimer les répertoires existants (./logs, ./bdd, ./datasets, ./mlruns, ./plugins .venv) ?"; then
    echo "🗑️ Arret des dockers..."
    docker compose down
    docker compose -f docker-compose-appli.yml down
    echo "🗑️ Suppression des anciens répertoires..."
    sudo rm -rf ./logs ./bdd ./datasets ./mlruns ./plugins .venv/
    echo "✅ Répertoires supprimés."
else
    echo "⏩ Suppression des répertoires ignorée."
fi

# Création des répertoires nécessaires
if confirm "Souhaitez-vous créer les répertoires nécessaires (logs, bdd, datasets, etc.) ?"; then
    echo "📂 Création des répertoires..."
    mkdir -p ./logs ./bdd ./datasets/raw_files/ ./mlruns ./plugins
    chmod 777 ./logs ./bdd ./datasets ./mlruns ./plugins
    echo "✅ Répertoires créés et droits appliqués."
else
    echo "⏩ Création des répertoires ignorée."
fi

echo "----------------------------------------"
echo "🐍 Installation et activation de l'environnement Python"
echo "----------------------------------------"

# Création de l'environnement virtuel
if confirm "Voulez-vous vérifier ou créer un environnement virtuel Python ?"; then
    if [ ! -d ".venv" ]; then
        python3 -m venv .venv
        echo "✅ Environnement Python créé."
    else
        echo "⚠️ L'environnement Python existe déjà."
    fi
else
    echo "⏩ Création de l'environnement virtuel ignorée."
fi

# Activer l'environnement virtuel
if confirm "Souhaitez-vous activer l'environnement Python ?"; then
    . .venv/bin/activate
    echo "✅ Environnement Python activé."
else
    echo "⏩ Activation de l'environnement virtuel ignorée."
fi

# Installer les dépendances
if confirm "Voulez-vous installer les dépendances à partir de requirements.txt ?"; then
    if [ -f "requirements.txt" ]; then
        echo "📦 Installation des dépendances..."
        pip install --upgrade pip
        pip install -r requirements.txt
        echo "✅ Dépendances installées."
    else
        echo "❌ Le fichier requirements.txt est introuvable. Assurez-vous qu'il existe."
    fi
else
    echo "⏩ Installation des dépendances ignorée."
fi

# Lancement de Docker Compose
echo "----------------------------------------"
echo "🐳 Lancement de Docker Compose"
echo "----------------------------------------"

# Initialisation d'Airflow avec Docker Compose
if confirm "Voulez-vous initialiser Airflow avec Docker Compose ?"; then
    docker compose up -d airflow-init
    echo "✅ Airflow initialisé."
else
    echo "⏩ Initialisation d'Airflow ignorée."
fi

# Lancer tous les services Docker Compose
if confirm "Souhaitez-vous démarrer les services Docker pour airflow ?"; then
    docker compose up -d
    echo "✅ Services Docker Compose démarrés avec succès."
else
    echo "⏩ Démarrage des services ignoré."
fi

if confirm "Souhaitez-vous récupérer les données brutes (raws) ?"; then
    curl https://files.grouplens.org/datasets/movielens/ml-20m.zip --output datasets/ml-20m.zip
    unzip datasets/ml-20m.zip -d datasets/raw_files
    mv datasets/raw_files/ml-20m/* datasets/raw_files/
    rmdir datasets/raw_files/ml-20m/
    rm -f datasets/ml-20m.zip
    echo "✅ Données récupérées avec succès."
else
    echo "⏩ Récupération des données brutes ignorée."
fi

# Instructions finales
echo "----------------------------------------"
echo "📂 Instructions finales"
echo "----------------------------------------"
echo
echo "Pour activer l'environnement Python, utilisez :"
echo "  . .venv/bin/activate"
echo
echo "Ajoutez également le chemin au PYTHONPATH avec :"
echo "  export PYTHONPATH=\$PYTHONPATH:`pwd`"
echo
echo "L'interface Airflow sera accessible à l'adresse suivante : http://127.0.0.1:8080 dans environ 1 minute."
echo
echo "L'interface MLflow sera accessible à l'adresse suivante : http://127.0.0.1:5000 dans environ 1 minute"
echo "----------------------------------------"

