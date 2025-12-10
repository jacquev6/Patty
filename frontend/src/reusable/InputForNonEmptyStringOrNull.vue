<!-- Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net> -->

<script setup lang="ts">
import { computed } from 'vue'

const model = defineModel<string | null>({ required: true })

const value = computed({
  get: () => (model.value === null ? '' : model.value),
  set: (value) => {
    if (value === '') {
      model.value = null
    } else {
      model.value = value
    }
  },
})
</script>

<template>
  <input v-model="value" />
</template>
