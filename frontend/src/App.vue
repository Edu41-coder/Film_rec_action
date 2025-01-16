<template>
  <v-app>
    <v-app-bar>
      <v-app-bar-title>{{ appName }}</v-app-bar-title>
    </v-app-bar>
    <v-main>
      <router-view />
    </v-main>
  </v-app>
</template>

<script lang="ts" setup>
const appName = import.meta.env.VITE_APP_NAME;
</script>
