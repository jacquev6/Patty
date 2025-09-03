<script setup lang="ts">
import type { AdaptedExercise } from '@/frontend/ApiClient'

export type Exercise =
  | {
      exerciseId: string
      pageNumber: number
      exerciseNumber: string
      kind: 'adapted'
      studentAnswersStorageKey: string
      adaptedExercise: AdaptedExercise
    }
  | {
      exerciseId: string
      pageNumber: number
      exerciseNumber: string
      kind: 'external'
      originalFileName: string
      data: string
    }

export type Data = {
  title: string
  exercises: Exercise[]
}

const data = JSON.parse('##TO_BE_SUBSTITUTED_TEXTBOOK_EXPORT_DATA##') as Data
</script>

<template>
  <RouterView v-slot="{ Component }">
    <component :is="Component" :data />
  </RouterView>
</template>
