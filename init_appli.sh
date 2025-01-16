#!/bin/bash

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
# source l'env python
. .venv/bin/activate

# export le PYTHONPATH
export PYTHONPATH=$PYTHONPATH:`pwd`


# Supprimer le fichier dvc.lock si confirmé
if confirm "Voulez-vous supprimer le fichier dvc.lock pour forcer une reconstruction complète ?"; then
    rm -rf dvc.lock
    echo "✔️ Fichier dvc.lock supprimé."
else
    echo "⏩ Suppression de dvc.lock ignorée."
fi

# Forcer la reconstruction des pipelines DVC
if confirm "Souhaitez-vous exécuter 'dvc repro --force' pour forcer la reconstruction des pipelines ?"; then
    dvc repro --force
    echo "✔️ Reconstruction des pipelines DVC terminée."
else
    echo "⏩ Reconstruction des pipelines DVC ignorée."
fi

# Reconstruire les images Docker sans cache
if confirm "Voulez-vous reconstruire les images Docker en ignorant le cache ?"; then
    docker compose -f docker-compose-appli.yml build --no-cache
    echo "✔️ Images Docker reconstruites sans cache."
else
    echo "⏩ Reconstruction des images Docker ignorée."
fi

# Démarrer les conteneurs Docker
if confirm "Souhaitez-vous démarrer les conteneurs Docker en mode détaché ?"; then
    docker compose -f docker-compose-appli.yml up -d
    echo "✔️ Conteneurs Docker démarrés."
else
    echo "⏩ Démarrage des conteneurs Docker ignoré."
fi

# Fin du script
echo "🚀 Processus terminé. l'aaplication ecoute sur http://127.0.0.1:7000"


