<!-- Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net> -->

<script setup lang="ts">
import { watch, useTemplateRef } from 'vue'

const model = defineModel<boolean | null>({ required: true })

const checkbox = useTemplateRef('checkbox')

watch(
  [model, checkbox],
  ([value, checkbox]) => {
    if (checkbox) {
      checkbox.indeterminate = value === null
      checkbox.checked = value === true
    }
  },
  { immediate: true },
)
</script>

<template>
  <input ref="checkbox" type="checkbox" v-model="model" />
</template>
