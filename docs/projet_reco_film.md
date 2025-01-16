# Table des matières

- [Table des matières](#table-des-matières)
- [1. Introduction](#1-introduction)
- [2. Limitations](#2-limitations)
  - [2.1. Description des fichiers de données](#21-description-des-fichiers-de-données)
- [3. Pipelines](#3-pipelines)
  - [3.1. Récuperation des datas](#31-récuperation-des-datas)
    - [3.1.1. Méthodes Principales de `Pipelines/0_load_clean_data.py` ](#311-méthodes-principales-de-pipelines0_load_clean_datapy-)
  - [3.2. Exploration des données](#32-exploration-des-données)
    - [3.2.1. Méthodes principales du script `Pipelines/1_analyse_data.py`](#321-méthodes-principales-du-script-pipelines1_analyse_datapy)
    - [3.2.2. Résultats après le chargement et l'analyse des données](#322-résultats-après-le-chargement-et-lanalyse-des-données)
      - [3.2.2.1. `movies.csv`](#3221-moviescsv)
      - [3.2.2.2. `ratings.csv`](#3222-ratingscsv)
      - [3.2.2.3. `tags.csv`](#3223-tagscsv)
    - [3.2.3. Conclusions sur les chargements et analyses des données](#323-conclusions-sur-les-chargements-et-analyses-des-données)
  - [3.3. Modèle](#33-modèle)
    - [3.3.1. Définition](#331-définition)
      - [3.3.1.1. Objectif](#3311-objectif)
      - [3.3.1.2. Valeure cible](#3312-valeure-cible)
      - [3.3.1.3. Valeurs en entrées](#3313-valeurs-en-entrées)
      - [3.3.1.4.  Indicateur d'évaluation](#3314--indicateur-dévaluation)
    - [3.3.2. Préparation des données pour le modéle](#332-préparation-des-données-pour-le-modéle)
      - [3.3.2.1 Méthodes principales du script `Pipelines/2_optimize_data.py`](#3321-méthodes-principales-du-script-pipelines2_optimize_datapy)
    - [3.3.3. Split des données](#333-split-des-données)
    - [3.3.4. Elaboration du modèle](#334-elaboration-du-modèle)
      - [3.3.4.1 Méthodes principales du script `Pipelines/2_optimize_data.py`](#3341-méthodes-principales-du-script-pipelines2_optimize_datapy)
    - [3.3.5 DVC](#335-dvc)
    - [3.3.6. Résultats](#336-résultats)
    - [3.3.7. Conclusion](#337-conclusion)
- [4. Application](#4-application)
  - [4.1. Backend](#41-backend)
    - [4.1.1. Endpoint `/tags`](#411-endpoint-tags)
    - [4.1.2. Endpoint `/genres`](#412-endpoint-genres)
    - [4.1.3. Endpoint `/notation`](#413-endpoint-notation)
  - [4.1. Frontend](#41-frontend)
    - [4.1.1. Fonctionnalités](#411-fonctionnalités)
    - [4.1.1.1. Récupération des Données](#4111-récupération-des-données)
    - [4.1.1.2. Sélection à partir des Listes](#4112-sélection-à-partir-des-listes)
    - [4.1.1.3. Calcul de la note estimée](#4113-calcul-de-la-note-estimée)

# 1. Introduction
Ce rapport est basé sur le MovieLens 20M Dataset (https://grouplens.org/datasets/movielens/20m/), un ensemble de données publiques fourni par le site GroupLens. Ce dataset contient :
- 20 millions d'évaluations réalisées par des utilisateurs sur des films.
- Des informations sur environ 27 000 films, incluant leurs genres et années de sortie.
- Des données sur les tags assignés par les utilisateurs.

# 2. Limitations

## 2.1. Description des fichiers de données
- `ratings.csv` contient les interactions utilisateur-film (notes attribuées). C’est le fichier principal pour :
  - Entraîner un modèle basé sur les préférences des utilisateurs.
  - Identifier les films les plus populaires ou les utilisateurs les plus actifs.

- `movies.csv` contient des métadonnées sur les films, comme les titres et les genres. il est utile pour :
  - Enrichir les modèles avec des informations basées sur le contenu :
  - Associer des films similaires en fonction de leurs genres.
  - Fournir des descriptions dans les recommandations (par exemple, afficher le titre et le genre d'un film recommandé).

- `tags.csv` capture les descriptions qualitatives et subjectives des films ajoutées par les utilisateurs.Il permet de personnaliser davantage les recommandations en tenant compte des préférences implicites.

- `links.csv` contient des identifiants IMDb et TMDb. Il est utile pour enrichir les données avec des bases externes, mais cette étape peut être hors du cadre d’une formation centrée sur MLOps.

- `genome-scores.csv et genome-tags.csv`. Ils sont 
  - Très riches (scores de pertinence entre films et tags), mais volumineux (~25M lignes).
  - Leur manipulation nécessite des ressources supplémentaires et ajoute une complexité trop importante pour notre apprentissages  MLOps.

Nous allons nous limiter aux fichiers  `ratings.csv, movies.csv, et tags.csv` car dans le cadre de notre  formation MLOps, l'objectif est de  construire, déployer et maintenir des pipelines de machine learning reproductibles et scalables sans ajouter une complexité inutile.



# 3. Pipelines
Dans cette section, nous allons détailler les pipelines nécessaires pour générer un modèle.

## 3.1. Récuperation des datas

La récupération des données est effectuée par le script `Pipelines/0_load_clean_data.py`.
 Ce script charge les données brutes, les nettoie, puis sauvegarde les données nettoyées dans le dossier `Datasets/Clean`.

### 3.1.1. Méthodes Principales de `Pipelines/0_load_clean_data.py` <a id="3.1.1."></a>
- `load_data()`
  - Cette méthode charge les données depuis le fichier CSV spécifié.
  - Elle vérifie si le fichier est accessible et lit les données dans un DataFrame.
  - En cas de succès, les données sont prêtes pour les étapes suivantes.
  - Rôle :
    - Transformer les données brutes en un format analysable.

- `clean_data()`
    - Identifie les problèmes courants dans les données :
    - Valeurs manquantes : Les lignes avec des valeurs manquantes sont supprimées.
    - Doublons : Les entrées dupliquées sont détectées et supprimées.
    - Fournit un rapport clair sur les anomalies détectées avant et après nettoyage.
    - Rôle :
      - Préparer un dataset propre pour les analyses.
- `save_data()`
    - Rôle
        Sauvegarder les données nettoyées dans un dossier `Datasets/Clean`.
- `run_pipeline()`
  - Méthode d’orchestration qui exécute toutes les étapes principales dans l’ordre :
    - load_data
    - clean_data.
    - save_data
  - Rôle :
    - Lire, nettoyer et sauvegarder les données propres

## 3.2. Exploration des données
Cette exploration, basée sur les données issues du pipeline 0_load_clean_data.py, vise à :
- Effectuer une analyse exploratoire des données.
- Identifier les tendances dominantes (genres populaires, distribution temporelle).
- Mettre en évidence les caractéristiques clés pour construire un système de recommandation.

L'analyse des données est effectuée par le script `Pipelines/1_analyse_data.py`.


### 3.2.1. Méthodes principales du script `Pipelines/1_analyse_data.py`

- `describe_data()`
  - Description :
    - Fournit une vue d’ensemble des données :
      - Nombre total de lignes et de colonnes.
      - Statistiques descriptives pour les colonnes numériques (moyenne, médiane, écart-type, etc.).
      - Comptage des valeurs uniques dans chaque colonne.
    - Offre un aperçu utile pour comprendre la structure des données et identifier rapidement des tendances ou anomalies.
  - Rôle :
    - Résumer les données pour faciliter leur compréhension et détecter des problématiques éventuelles.
- `visualize_data()`
  - Description :
    - Génère des visualisations pertinentes en fonction des colonnes disponibles :
      - Distribution des notes : Produit un graphique en barres si une colonne rating est présente.
      - Distribution des genres : Analyse les genres et crée des graphiques en barres.
    - Les graphiques générés sont enregistrés sous forme de fichiers PNG dans `Analyse`
  - Rôle :
    - Faciliter la compréhension des données grâce à des représentations visuelles.
- `analyze_year_distribution()`
  - Description :
    - Extrait les années de sortie des titres (si une colonne title est disponible).
    - Analyse la répartition des films par année.
    - Crée un graphique linéaire pour visualiser les tendances temporelles.
  - Rôle :
    - Identifier des périodes clés de production ou de popularité des films.

### 3.2.2. Résultats après le chargement et l'analyse des données

#### 3.2.2.1. `movies.csv`
- Nettoyage :
  - Aucune valeur manquante ou doublon détecté.
- Description des données :
  - Nombre de films : 27,278.
  - Colonnes disponibles : movieId, title, genres.
- Graphiques générés :
  - Distribution des genres
    ![Distribution des genres](../Analyse/movies_genres_distribution.png)
    - Observations :
      - Les genres Drama, Comedy dominent largement le dataset.
      - Les genres moins fréquents comme Film-noir et Western apparaissent sporadiquement.
    - Conclusions :
      - Les genres populaires sont bien représentés et influencent probablement les préférences des utilisateurs.
      - Les genres rares peuvent cibler des niches spécifiques mais nécessiter des recommandations personnalisées.
  - Répartition temporelle des films (movies_year_distribution.png):
    ![Répartition temporelle des films](../Analyse/film_year_distribution.png)
    - Observations :
      - La production cinématographique connaît un pic dans les années 2000.
      - Les films produits avant les années 1950 sont rares.
      - La production semble se stabiliser après 2010.
    - Conclusions :
      - Les films anciens, moins représentés, pourraient nécessiter une approche différente dans les systèmes de recommandation.

#### 3.2.2.2. `ratings.csv`
  - Nettoyage :
    - Aucune valeur manquante ou doublon détecté.
  - Description des données :
    - Nombre total d’évaluations : 20,000,263.
    - Colonnes disponibles : userId, movieId, rating, timestamp.
    - Moyenne des notes : ~3.52.
    - Les évaluations sont biaisées vers des notes moyennes à élevées.
  - Graphique généré :
    - Distribution des notes (ratings_ratings_distribution.png):
    ![Répartition temporelle des films](../Analyse/ratings_distribution.png)
    - Observations :
      - Les notes 3.0, 4.0 et 5.0 sont les plus fréquentes.
      - Les notes faibles (≤ 2.0)  sont assez rares.
    - Conclusions :
      - Les utilisateurs tendent à attribuer des évaluations positives, ce qui reflète un biais d’évaluation.
      - Ce biais pourrait nécessiter des ajustements dans les algorithmes de recommandation pour éviter de sur-représenter certains contenus.


#### 3.2.2.3. `tags.csv`
  - Nettoyage :
    - 16 valeurs manquantes détectées dans tag, supprimées.
    - Aucun doublon détecté.
  - Description des données :
    - Nombre de liaisons tags : 465,548.
    - Colonnes disponibles : userId, movieId, tag, timestamp.
  - Conclusions :
    - Les tags offrent des informations contextuelles uniques et permettent d’enrichir la personnalisation dans les recommandations.
    - L’analyse plus détaillée des tags pourrait révéler des préférences implicites des utilisateurs.



### 3.2.3. Conclusions sur les chargements et analyses des données

Les fichiers sont majoritairement bien structurés, nécessitant peu de nettoyage.

Les genres dominants (Drama, Comedy) sont les plus populaires. Les genres rares peuvent représenter des opportunités pour cibler des niches.

La production de films a fortement augmenté dans les années 2000. Les films anciens sont sous-représentés et nécessitent des approches spécifiques.

Les notes sont biaisées vers des évaluations positives, nécessitant des ajustements pour éviter les recommandations biaisées.


## 3.3. Modèle

### 3.3.1. Définition

#### 3.3.1.1. Objectif 

Prédire le score moyen d’un film (variable cible) en s'appuyant sur les genres et les tags (variables d’entrée) comme principales caractéristiques. Nous recherchons donc un modèle de régression

#### 3.3.1.2. Valeure cible 

La valeur cible est définie comme le score moyen attribué à un film.
Elle est calculée à partir des évaluations disponibles dans le fichier ratings.csv.
Elle représente l'appréciation générale des utilisateurs pour un film donné.

#### 3.3.1.3. Valeurs en entrées

Principales Caractéristiques en Entrée:
- Le genre (sous forme de vecteur)
- Les tags sous forme de vecteurs pondérés. Chaque mot devient une dimension du vecteur, et sa valeur représente son importance relative.

#### 3.3.1.4.  Indicateur d'évaluation

Nous souhaitons minimiser la différence entre la note réelle et la note estimée. Pour cela, nous utilisons la **MSE (Mean Squared Error)** comme indicateur d'évaluation.


### 3.3.2. Préparation des données pour le modéle

Suite à la définition du modèle, nous devons effectuer les calculs suivants :

- Calcul du score moyen de chaque film : À partir des notes attribuées par les utilisateurs, déterminer la moyenne des évaluations pour chaque film afin de refléter son appréciation globale.
- Transformation des genres en vecteurs binaires : Représenter les genres sous forme de vecteurs binaires pour une exploitation optimale dans les modèles.
- Utilisation de TF-IDF pour les tags : Évaluer l'importance relative de chaque mot-clé (tag) associé aux films et les transformer en vecteurs pondérés, exploitables pour l’analyse et la modélisation.

Les calculs mentionnés ci-dessus sont effectués sur les données issues du script `Pipelines/2_optimize_data.py`.
Les données en entrée proviennent des données nettoyées.

Ce script génère un nouveau fichier CSV `Datasets/Clean/optimized_movies.csv` qui remplace les données nettoyées de movies par un ensemble enrichi comprenant :
- L’importance relative de chaque mot-clé,
- Le score moyen de chaque film,
- Les genres transformés en vecteurs binaires.

#### 3.3.2.1 Méthodes principales du script `Pipelines/2_optimize_data.py`

- `calculate_average_rating()`
  - Description :
    - Calcule le score moyen attribué à chaque film à partir des évaluations des utilisateurs.
    - Transforme les genres en colonnes binaires.
- `process_tags_with_tfidf()`
  - Description :
    - Applique l'algorithme TF-IDF aux tags pour créer une représentation pondérée des mots-clés associés aux films.
- `save_data()`
  - Description :
    - Sauvegarde les données nettoyées ou transformées dans un fichier CSV.

- Exécution principale (dans __main__)
  - Étapes principales :
    - Charger les fichiers CSV nettoyés pour les films, évaluations et tags.
    - Calculer les scores moyens et binariser les genres.
    - Appliquer TF-IDF pour traiter les tags.
    - Sauvegarder les données enrichies dans le fichier `Datasets/Clean/optimized_movies.csv`.

### 3.3.3. Split des données

le Split est fait dans  `Pipelines/3_split_data.py`. Il génére deux fichiers :
- `Datasets/Model/train_movies.csv` (fichier pour l'entraînement)
- `Datasets/Model/validation_movies.csv` (fichier pour la validation)

### 3.3.4. Elaboration du modèle

Nous allons tester 4 algorithmes de régression :
- LinearRegression 
- XGBoost avec gridCv pour trouver les meilleurs parametres
  ```
  param_grid = {
              "n_estimators": [100, 200, 300],
              "max_depth": [3, 5, 7],
              "learning_rate": [0.01, 0.1, 0.2],
              "subsample": [0.6, 0.8, 1.0],
              "colsample_bytree": [0.6, 0.8, 1.0],
          }
  ```
- ElasticNet
    ```
     param_grid = {
            "alpha": [0.01, 0.1, 1, 10, 100],  
            "l1_ratio": [0.2, 0.5, 0.8, 1.0],  
        }
    ```
- KNeighborsRegressor
  ```
   param_grid = {
            "n_neighbors": [3, 5, 10, 15], 
            "weights": ["uniform", "distance"], 
            "p": [1, 2],
        }
  ```

la dertmination du méilleur modéle est faite dans le script Pipelines/4_train_models.py. 
il est composé  de plusieurs fonctions

il va générer le modele optimisé `Models/best_model.pkl`

#### 3.3.4.1 Méthodes principales du script `Pipelines/2_optimize_data.py`

Voici un résumé détaillé des fonctions dans votre script :

- `init_data()`
   - Description:  
     - Charge les fichiers de données d'entraînement et de validation, supprime les lignes contenant des valeurs manquantes, et prépare les matrices de caractéristiques (\(X\)) et la cible (\(y\)).
   - Sorties :  
     - \(X\) et \(y\) pour les ensembles d'entraînement et de validation.

- `init_grid()`
  - Description** :  
    - Configure un objet `GridSearchCV` pour effectuer une recherche d’hyperparamètres adaptée au modèle spécifié.
  - Sortie :  
    - Un objet `GridSearchCV` configuré avec une grille d’hyperparamètres appropriée.

- `evaluate_model()` 
  - Description :  
    - Évalue le modèle en calculant le **Mean Squared Error (MSE)** sur l'ensemble de validation.
  - Sortie :  
    - Le MSE obtenu sur l'ensemble de validation.

-  `train_with_grid()`
   - Description :  
     - Entraîne un modèle en optimisant ses hyperparamètres avec une recherche de grille (GridSearchCV) si applicable, puis l’évalue sur l’ensemble de validation.
     - Envoie les résultats à **MLflow**.
   - Sorties :  
     - Le MSE et le modèle entraîné.

- `get_best_model()`
  - Description
    - Compare plusieurs modèles (LinearRegression, XGBoost, ElasticNet, KNeighborsRegressor) pour déterminer celui avec le plus faible MSE sur l’ensemble de validation.
  - Sortie :  
    - Le meilleur modèle (modèle ayant le plus faible MSE).


### 3.3.5 DVC
Afin de pouvoir facilement rejouer notre pipeline, nous avons mis en place un DVC, dont voici le fichier YAML:
```
stages:
  load_clean_data:
    cmd: python pipelines/load_clean_data.py
    deps:
      - pipelines/load_clean_data.py
      - datasets/raw_files/movies.csv
      - datasets/raw_files/ratings.csv
      - datasets/raw_files/tags.csv
    outs:
      - datasets/clean_data/cleaned_movies.csv
      - datasets/clean_data/cleaned_ratings.csv
      - datasets/clean_data/cleaned_tags.csv

  analyze_data:
    cmd: python pipelines/analyse_data.py
    deps:
      - pipelines/analyse_data.py
      - datasets/clean_data/cleaned_movies.csv
      - datasets/clean_data/cleaned_ratings.csv
      - datasets/clean_data/cleaned_tags.csv
    outs:
      - datasets/analyses/analyse_cleaned_movies.txt
      - datasets/analyses/analyse_cleaned_ratings.txt
      - datasets/analyses/film_year_distribution.png
      - datasets/analyses/movies_genres_distribution.png
      - datasets/analyses/ratings_distribution.png

  optimize_data:
    cmd: python pipelines/optimize_data.py
    deps:
      - pipelines/optimize_data.py
      - datasets/clean_data/cleaned_movies.csv
      - datasets/clean_data/cleaned_ratings.csv
      - datasets/clean_data/cleaned_tags.csv
    outs:
      - datasets/clean_data/optimized_movies.csv
      - datasets/clean_data/tfidf.pkl

  split_data:
    cmd: python pipelines/split_data.py
    deps:
      - pipelines/split_data.py
      - datasets/clean_data/optimized_movies.csv
    outs:
      - datasets/clean_data/train_movies.csv

  train_models:
    cmd: python pipelines/train_models.py
    deps:
      - datasets/clean_data/train_movies.csv
      - datasets/clean_data/tfidf.pkl
    outs:
      - datasets/model/best_model.pkl

```

### 3.3.6. Résultats

Comme nous pouvons le constater sur la page MLflow, le meilleur modèle sélectionné est XGBoost avec une mse à **0.22**. 

![best modele](../Analyse/comparaison_algo.png)

Les meilleurs paramètres sont :
![best modele](../Analyse/grid.png)


### 3.3.7. Conclusion

La MSE de 0.22 signifie qu'en moyenne, l'erreur absolue des prédictions est d'environ 0.47 sur une échelle de 0 à 5, ce qui est assez satisfaisant. Nous allons donc utiliser ce modèle pour créer notre application.


# 4. Application
Dans ce chapitre, nous allons montrer les fonctionnalités de notre backend et de notre frontend.
**Pour info, les codes sont en cours de développement.**

## 4.1. Backend

Le backend est développé en FastAPI.

il possede trois APis:

### 4.1.1. Endpoint `/tags`
Récupération de tous les **Tags** (sans doublons) : 
- url `/tags`
- methode : GET
- JSON en sortie de ce type (ordre alphabetique)
    ```
    {
      "tags": ["bollywood", "conspiracy theory", "dark hero", "drôle"]
    }
    ```  

### 4.1.2. Endpoint `/genres` 
Récupération de tous les **Genres** (sans doublons) :
- url `/genres`
- methode : GET
- JSON en sortie de ce type (ordre alphabetique)
    ```
    {
      "genres": ["Action", "Comedy", "Crime",....]
    }
    ```  

### 4.1.3. Endpoint `/notation` 
Demande de notation pour un ensemble de Tags et de Genres
  - url `/notation`
  - methode : POST
  - JSON en entrée de ce type 
    ```
     {
      "genres": ["genre1", "genre2",...],
      "tags": ["tag1", "tag3",...]
    }
    ```
 - JSON en sortie de ce type 
      ```
      {"rating": 3.54}
      ```    
 
    

## 4.1. Frontend
L'application Vue.js récupère et affiche deux listes (genres et tags) depuis le backend, et permet à l'utilisateur de sélectionner des éléments de chaque liste. 
Ces sélections sont ensuite envoyées au backend au format JSON via l'endpoint /notations.

### 4.1.1. Fonctionnalités

### 4.1.1.1. Récupération des Données

Le projet fait deux requêtes GET au backend pour récupérer les listes :
- `/genres` : Cette API retourne une liste de genres sans doublons.
- `/tags` : Cette API retourne une liste de tags sans doublons.
Les données reçues seront affichées sous forme de deux listes distinctes.

### 4.1.1.2. Sélection à partir des Listes 
Chaque liste (genres et tags) sera affichée en tant que simple liste.
L'utilisateur pourra cliquer sur les éléments de chaque liste pour les sélectionner.
Une fois des genres ou des tag sélectionnés, il seront mis en surbrillance pour indiquer sa sélection.
Envoi des Données au Backend :

Une fois que l'utilisateur a fait sa sélection, il appuie sur un bouton "Envoyer".

### 4.1.1.3. Calcul de la note estimée
L'application envoie la sélection au backend via une requête POST vers `/notations`.
Les données seront envoyées au format JSON sous la forme :
{
  "genres": ["genre1", "genre2"],
  "tags": ["tag1", "tag3"]
}

Le score sera ensuite affiché 























