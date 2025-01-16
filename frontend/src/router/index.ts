/**
 * router/index.ts
 *
 * Automatic routes for `./src/pages/*.vue`
 */

// Composables
import { createRouter, createWebHistory } from "vue-router/auto";
import { routes } from "vue-router/auto-routes";
import axios from "axios"; // Import de l'instance Axios

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

// Vérification du token avant chaque navigation
router.beforeEach(async (to, from, next) => {
  const token = localStorage.getItem("token");
  // Si aucun token et la page n'est pas la page de connexion, redirigez vers Login
  if (!token && to.name !== "/Login") {
    next("/Login");
    return;
  }

  // Si un token existe, le valider avec l'API
  if (token && to.name !== "/Login") {
    try {
      const response = await axios.get(
        `${import.meta.env.VITE_API_URL}/validate-token`,
        {
          params: { token }, // Passer le token en paramètre
        }
      );

      // Si le token est valide, continuer
      if (response.data.message === "Token valide") {
        next();
      } else {
        // Sinon, rediriger vers Login
        console.warn("Token invalide :", response.data.message);
        next("/Login");
      }
    } catch (error) {
      // En cas d'erreur, rediriger vers Login
      console.error("Erreur lors de la validation du token :", error);
      next("/Login");
    }
  } else {
    next(); // Aucun token requis pour la navigation vers d'autres pages
  }
});

// Suppression de l'élément local utilisé pour le rechargement dynamique
router.isReady().then(() => {
  localStorage.removeItem("reloading");
});

export default router;
