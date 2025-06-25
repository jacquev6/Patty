<script setup lang="ts">
import { computed } from 'vue'

import type { PassiveComponent } from '@/apiClient'
import FormattedComponent from './FormattedComponent.vue'

const props = defineProps<{
  kind: 'selectableInput'
  contents: PassiveComponent[]
  colors: string[]
  tricolorable: boolean
}>()

const colorIndex = defineModel<number>({ required: true })

function increment() {
  colorIndex.value = (colorIndex.value + 1) % (props.colors.length + 1)
}

const highlighted = computed(() => (colorIndex.value === 0 ? null : props.colors[colorIndex.value - 1]))

const style = computed(() => {
  if (props.contents.length === 1 && props.contents[0].kind === 'text' && props.contents[0].text.length === 1) {
    const c = props.contents[0].text[0]
    if ('.!?,;:'.includes(c)) {
      return {
        padding: '16px 3.2px',
      }
    } else {
      return {
        padding: '2px 2px',
      }
    }
  } else {
    return {}
  }
})
</script>

<template>
  <FormattedComponent
    kind="formatted"
    class="main"
    :style
    :contents
    :highlighted
    :tricolorable
    data-cy="selectableInput"
    @click="increment()"
  />
</template>

<style scoped>
.main {
  cursor: pointer;
  user-select: none; /* Prevent accidental selection. Warning: not tested using Cypress (too difficult). */
}

.main:hover {
  outline: 1px dashed green;
}
</style>
