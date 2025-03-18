<script setup lang="ts">
import { provide, useTemplateRef } from 'vue'

import type { AdaptedExercise } from '@/apiClient'
import LineComponent from './components/LineComponent.vue'

defineProps<{
  adaptedExercise: AdaptedExercise
}>()

provide('adaptedExerciseTeleportBackdropTo', useTemplateRef('container'))
</script>

<template>
  <div ref="container">
    <p v-for="{ contents } in adaptedExercise.instructions.lines">
      <LineComponent :contents />
    </p>
    <div v-for="page in adaptedExercise.wording.pages">
      <p v-for="{ contents } in page.lines">
        <LineComponent :contents />
      </p>
    </div>
  </div>
</template>

<style scoped>
div {
}
</style>
