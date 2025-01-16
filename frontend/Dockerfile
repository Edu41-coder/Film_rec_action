# Utilise l'image officielle Node.js en version LTS (long-term support) basée sur Alpine Linux.
FROM node:lts-alpine
# Alpine est une distribution légère de Linux, idéale pour des conteneurs minimalistes.

# Installe un serveur HTTP léger pour servir du contenu statique.
RUN npm install -g http-server
# La commande `npm install -g http-server` installe globalement le serveur HTTP `http-server` pour servir les fichiers générés.

# Définit `/app` comme répertoire de travail dans le conteneur.
WORKDIR /app
# Toutes les commandes suivantes s'exécuteront à partir de ce répertoire.

# Copie `package.json` et `package-lock.json` (si disponible) dans le répertoire de travail.
COPY package*.json ./
# Cette étape est utilisée pour tirer parti du cache Docker. Si les fichiers `package.json` n'ont pas changé, Docker réutilisera les couches précédentes.

# Installe les dépendances du projet.
RUN yarn install
# Installe toutes les dépendances définies dans `package.json` à l'aide de Yarn, un gestionnaire de packages rapide et efficace.

# Copie tout le contenu du projet dans le conteneur, y compris le code source, le fichier `yarn.lock`, etc.
COPY . .
# Cette étape copie tous les fichiers et dossiers du projet (sauf ceux définis dans `.dockerignore`) vers le conteneur.

# Construit l'application Vue.js pour la production.
RUN yarn build
# La commande `yarn build` exécute le script de build défini dans le fichier `package.json`. Elle génère les fichiers optimisés pour la production dans le dossier `dist`.

# Expose le port 7000 pour les connexions externes.
EXPOSE 7000
# Cette instruction informe Docker que le conteneur écoute sur le port 7000, mais elle ne mappe pas le port automatiquement (cela se fait avec `docker run -p` ou dans un fichier `docker-compose.yml`).

# Démarre le serveur HTTP pour servir les fichiers statiques générés.
CMD [ "http-server", "dist", "-p", "7000" ]
# La commande par défaut exécute `http-server`, qui sert les fichiers dans le répertoire `dist` (fichiers générés par `yarn build`) sur le port 7000.
