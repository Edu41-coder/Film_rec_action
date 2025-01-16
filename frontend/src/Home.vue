<template>
  <v-container>
    <h1>Bienvenue sur RecoFilm</h1>
    <v-btn color="primary" @click="goToMovies">Voir les Films Recommandés</v-btn>
  </v-container>
</template>

<script lang="ts" setup>
import { useRouter } from 'vue-router';

const router = useRouter();

const goToMovies = () => {
  router.push('/movies');
};
</script>

<style scoped>
h1 {
  color: #1976d2;
}
</style>
