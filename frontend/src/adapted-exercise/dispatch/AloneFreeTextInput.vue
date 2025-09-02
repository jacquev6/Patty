<script setup lang="ts">
import { useTemplateRef } from 'vue'

import type { TextInputRenderable } from '@/adapted-exercise/AdaptedExerciseRenderer.vue'
import TextInputRenderer from '@/adapted-exercise/components/TextInputRenderer.vue'
import assert from '$/assert'

defineProps<{
  component: TextInputRenderable
  tricolorable: boolean
}>()

const inner = useTemplateRef('inner')

function focus() {
  assert(inner.value !== null)
  inner.value.focus()
}
</script>

<template>
  <p @click="focus">
    <TextInputRenderer
      ref="inner"
      :path="component.path"
      :initialText="component.initialText"
      :increaseHorizontalSpace="component.increaseHorizontalSpace"
      :tricolorable="tricolorable"
      :aloneOnLine="true"
    />
  </p>
</template>

<style scoped>
p {
  border: 2px outset black;
  padding: 4px;
  margin-bottom: 1em;
}

p:has(:focus) {
  background-color: #fffdd4;
}
</style>
