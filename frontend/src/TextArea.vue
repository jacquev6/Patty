<script setup lang="ts">
import { nextTick, useTemplateRef, watch } from 'vue'
import assert from './assert'

const model = defineModel<string>({ required: true })

const textareaRef = useTemplateRef('textarea')

watch(
  model,
  async () => {
    await nextTick()
    assert(textareaRef.value !== null)
    textareaRef.value.style.height = 'auto' // Reduce size when user deletes lines
    textareaRef.value.style.height = `calc(${textareaRef.value.scrollHeight + 4 + 'px'} + 1.5em)` // Give room to avoid flickering when user adds lines
  },
  { immediate: true },
)
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
