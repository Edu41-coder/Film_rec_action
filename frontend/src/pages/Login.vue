<template>
  <v-container>
    <h1 class="text-h4 mb-4">
      Connexion
    </h1>
    <v-alert
      v-if="errorMessage"
      type="error"
      class="mt-4"
    >
      {{ errorMessage }}
    </v-alert>
    <v-form
      ref="formRef"
      v-model="isFormValid"
    >
      <v-text-field
        v-model="username"
        label="Username"
        type="text"
        outlined
        required
      />

      <v-text-field
        v-model="password"
        label="Mot de passe"
        type="password"
        outlined
        required
      />

      <v-btn
        class="mt-4"
        color="primary"
        :disabled="!isFormValid"
        @click="handleLogin"
      >
        Se connecter
      </v-btn>
    </v-form>
  </v-container>
</template>

<script setup lang="ts">
// Imports
import {ref} from 'vue';
import {useRouter} from 'vue-router';
import axios from "axios";
// Champs de formulaire
const username = ref<string>('');
const password = ref<string>('');
const isFormValid = ref<boolean>(false);
const errorMessage = ref<string | null>(null);
const router = useRouter();

// Règles de validation
// Référence du formulaire
const formRef = ref<any>(null);
// Fonction de connexion
const handleLogin = async () => {
  if (!formRef.value.validate()) return;

  try {
    const response = await axios.post(`${import.meta.env.VITE_API_URL}/token`, {
      username: username.value,
      password: password.value,
    });
    if (response.status == 200)
      localStorage.setItem('token', response.data.access_token);
       router.push('/');
  } catch (error) {
    console.error('Erreur de connexion:', error);
    errorMessage.value = 'Échec de la connexion. Vérifiez vos informations.';
  }
};
</script>
