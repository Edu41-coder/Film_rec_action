import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL, // URL de l'API définie dans les variables d'environnement
  headers: {
    "Content-Type": "application/json",
  },
});

// Fonction de validation du token
const validateToken = async (token: string): Promise<boolean> => {
  try {
    const response = await axios.get(
      `${import.meta.env.VITE_API_URL}/validate-token`,
      {
        params: { token }, // Passer le token en paramètre
      }
    );
    return response.data.message === "Token valide";
  } catch (error) {
    console.error("Erreur lors de la validation du token :", error);
    return false;
  }
};

// Ajouter le token JWT à chaque requête après validation
api.interceptors.request.use(
  async (config) => {
    const token = localStorage.getItem("token");

    if (token) {
      console.log('mlsdmqldsmqlsdmkl')
      // Valider le token avant d'ajouter l'autorisation
      const isValid = await validateToken(token);
      if (isValid) {
        config.headers.Authorization = `Bearer ${token}`;
      } else {
        console.warn("Token invalide, redirection vers la page de connexion.");
        localStorage.removeItem("token"); // Supprimez le token invalide
        window.location.href = "/Login"; // Redirigez l'utilisateur vers la page de connexion
        return Promise.reject(new Error("Token invalide"));
      }
    }
    return config;
  },
  (error) => {
    // Gérer les erreurs avant qu'elles ne soient envoyées
    return Promise.reject(error);
  }
);

export default api;
