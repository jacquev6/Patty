<script setup lang="ts">
import { onMounted, useTemplateRef } from 'vue'
import autosize from 'autosize'

import assert from './assert'

const model = defineModel<string>({ required: true })

const textareaRef = useTemplateRef('textarea')

onMounted(() => {
  assert(textareaRef.value !== null)
  autosize(textareaRef.value)
})
</script>

<template>
  <textarea ref="textarea" v-model="model"></textarea>
</template>

<style scoped>
textarea {
  width: 100%;
  resize: none;
}
</style>
