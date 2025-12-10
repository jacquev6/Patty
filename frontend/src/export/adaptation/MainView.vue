<!-- Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net> -->

<script setup lang="ts">
import type { AdaptedExercise, ImagesUrls } from '@/frontend/ApiClient'
import AdaptedExerciseRenderer from '@/adapted-exercise/AdaptedExerciseRenderer.vue'

// WARNING: changing this type requires changing the export code in the backend
type Data = {
  studentAnswersStorageKey: string
  adaptedExercise: AdaptedExercise
  imagesUrls: ImagesUrls
}

const data = JSON.parse('##TO_BE_SUBSTITUTED_ADAPTATION_EXPORT_DATA##') as Data
</script>

<template>
  <AdaptedExerciseRenderer :navigateUsingArrowKeys="true" v-bind="data" style="height: 100vh" />
</template>
