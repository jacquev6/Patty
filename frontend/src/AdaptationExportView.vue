<script setup lang="ts">
import AdaptedExerciseRenderer from './AdaptedExercise/AdaptedExerciseRenderer.vue'

const data = JSON.parse('{{ data }}')
</script>

<template>
  <AdaptedExerciseRenderer :adaptedExercise="data" style="height: 100vh" />
</template>
