<script setup lang="ts">
import type { Data } from './RootView.vue'
import { useI18n } from 'vue-i18n'

defineProps<{
  data: Data
}>()

const { t } = useI18n()
</script>

<template>
  <p v-for="exercise in data">
    <RouterLink :to="{ name: 'exercise', params: { id: exercise.exerciseId } }">
      {{ t('exercise') }} {{ exercise.exerciseId }}
    </RouterLink>
  </p>
</template>

<i18n>
fr:
  exercise: "Exercice"
</i18n>
