<template>
  <v-container v-if="!loading">
    <v-card>
      <v-card-title class="mb-4">
        Estimer la note d'un film
        <v-divider />
      </v-card-title>
      <v-card-item>
        <v-alert v-if="error !== null" type="error">
          {{ error }}
        </v-alert>
        <v-form ref="formRef" v-model="isFormValid">
          <!-- Champ Texte -->
          <v-row>
            <v-col cols="12" md="4">
              <v-text-field
                v-model="filmTitle"
                label="Titre du film"
                outlined
                required
                :rules="[minLengthRule]"
              />
            </v-col>
            <v-col cols="12" md="4">
              <v-select
                v-model="selectedGenres"
                :items="availableGenres"
                label="Genres"
                multiple
                outlined
                chips
                closable-chips
                required
                :rules="[minLengthRule]"
              />
            </v-col>

            <v-col cols="12" md="4">
              <v-autocomplete
                v-model="selectedTags"
                :items="availableTags"
                label="Tags"
                multiple
                outlined
                chips
                closable-chips
                required
                :rules="[minLengthRule]"
              />
            </v-col>
          </v-row>
        </v-form>
      </v-card-item>
      <v-card-actions>
        <v-spacer />
        <v-btn
          :disabled="
            filmTitle == '' ||
            selectedTags.length == 0 ||
            selectedGenres.length == 0
          "
          color="primary"
          variant="outlined"
          class="mr-4 mb-3"
          @click="submitForm"
        >
          Calculer
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-container>
  <v-container>
    <v-card>
      <v-card-title class="mb-4">
        Mes dernières estimations
        <v-divider />
      </v-card-title>
      <v-card-text>
        <v-row>
          <v-col
            v-for="(film, index) in testedFilms"
            :key="index"
            class="pa-3"
            cols="12"
            md="6"
            lg="4"
          >
            <v-card class="pa-3" variant="outlined">
              <v-card-title class="text-h6">
                {{ film.title }} : <i class="text-red">{{ film.note }}/5</i>
              </v-card-title>
              <v-card-subtitle class="text-body-2">
                <strong>Tags : </strong>
                <span v-for="(tag, i) in film.tags" :key="i">
                  {{ tag }}<span v-if="i < film.tags.length - 1">, </span>
                </span>
              </v-card-subtitle>

              <v-card-subtitle class="text-body-2">
                <strong>Genres : </strong>
                <span v-for="(genre, i) in film.genres" :key="i">
                  {{ genre }}<span v-if="i < film.genres.length - 1">, </span>
                </span>
              </v-card-subtitle>
            </v-card>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import api from "@/services/axios";

interface Film {
  title: string;
  tags: string[];
  genres: string[];
  note: number;
}
const filmTitle = ref<string>("");
const selectedTags = ref<string[]>([]);
const selectedGenres = ref<string[]>([]);
const isFormValid = ref<boolean>(false);
// Référencement du formulaire
const formRef = ref<any>(null);
const availableTags = ref<string[]>([]);
const availableGenres = ref<string[]>([]);
const testedFilms = ref<Film[]>([]);
// Validation
const minLengthRule = (value: any) =>
  (!!value && value.length > 0) || "Ce champ est requis.";
const url = import.meta.env.VITE_APP_URL;

const loading = ref<boolean>(false);
const error = ref<string | null>(null);
// Fonction de soumission
const submitForm = async () => {
  if (formRef.value.validate()) {
    loading.value = true;
    error.value = null;
    api
      .post("notation", {
        tags: selectedTags.value,
        genres: selectedGenres.value,
      })
      .then((response) => {
        console.log(response);
        testedFilms.value.unshift({
          title: filmTitle.value,
          tags: selectedTags.value,
          genres: selectedGenres.value,
          note: response.data["rating"],
        });
        console.log(testedFilms);
        loading.value = false;
      })
      .catch((error) => {
        error.value = "Formulaire soumis en erreur";
      });
  } else {
    error.value = "Formulaire soumis en erreur";
  }
};

onMounted(() => {
  api
    .get("/tags")
    .then((response) => {
      availableTags.value = response.data;
      loading.value = false;
    })
    .catch((error) => {
      error.value = "";
    });
  api
    .get("/genres")
    .then((response) => {
      availableGenres.value = response.data;
      loading.value = false;
    })
    .catch((error) => {
      error.value = "";
    });
});
</script>
