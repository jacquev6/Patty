<script setup lang="ts">
import { computed, provide, ref, useTemplateRef } from 'vue'

import type { AdaptedExercise } from '@/apiClient'
import LineComponent from './components/LineComponent.vue'
import PageNavigationControls from './PageNavigationControls.vue'

const props = defineProps<{
  adaptedExercise: AdaptedExercise
}>()

provide('adaptedExerciseTeleportBackdropTo', useTemplateRef('container'))

const pagesCount = computed(() => props.adaptedExercise.wording.pages.length)
const page = ref(0)
</script>

<template>
  <div ref="container">
    <PageNavigationControls :pagesCount v-model="page">
      <p v-for="{ contents } in adaptedExercise.instructions.lines">
        <LineComponent :contents />
      </p>
      <p v-for="{ contents } in adaptedExercise.wording.pages[page].lines">
        <LineComponent :contents />
      </p>
    </PageNavigationControls>
  </div>
</template>

<style scoped>
div {
  height: 100%;
}
</style>
