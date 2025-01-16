FROM python:3.9-slim

# Installer MLflow
RUN pip install mlflow==2.9.1

# Exposer le port MLflow
EXPOSE 5000

# Point d'entrée : démarrer le serveur MLflow
ENTRYPOINT ["mlflow"]

# Commande par défaut : serveur MLflow
CMD ["server", "--host", "0.0.0.0", "--backend-store-uri", "sqlite:///mlflow.db", "--default-artifact-root", "/mlflow"]
