<!-- Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net> -->

<script lang="ts" setup>
import type { AdaptedExercise, ImagesUrls } from '@/frontend/ApiClient'

// WARNING: changing this type requires changing the export code in the backend
export type Data = {
  exerciseId: string
  studentAnswersStorageKey: string
  adaptedExercise: AdaptedExercise
  imagesUrls: ImagesUrls
}[]

const data = JSON.parse('##TO_BE_SUBSTITUTED_BATCH_EXPORT_DATA##') as Data
</script>

<template>
  <RouterView v-slot="{ Component }">
    <component :is="Component" :data />
  </RouterView>
</template>
