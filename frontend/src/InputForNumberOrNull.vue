<script setup lang="ts">
import { computed } from 'vue'

const model = defineModel<number | null>({ required: true })

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
  <input type="number" v-model="value" />
</template>
