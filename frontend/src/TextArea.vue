<script setup lang="ts">
import { computed, nextTick, onMounted, useTemplateRef, watch } from 'vue'
import autosize from 'autosize'

import assert from './assert'

const model = defineModel<string>({ required: true })

const textareaRef = useTemplateRef('textarea')

onMounted(() => {
  assert(textareaRef.value !== null)
  autosize(textareaRef.value)
})

watch(model, async () => {
  assert(textareaRef.value !== null)
  await nextTick()
  autosize.update(textareaRef.value)
})

defineExpose({
  wrapped: computed(() => {
    assert(textareaRef.value !== null)
    return textareaRef.value
  }),
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
