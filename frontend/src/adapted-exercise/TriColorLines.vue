<!-- Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net> -->

<script lang="ts">
/* Colors provided by client */
export const colors: [string, string, string] = ['rgb(0, 0, 255)', 'rgb(255, 0, 0)', 'rgb(0, 204, 0)']
</script>

<script setup lang="ts">
import { useElementSize } from '@vueuse/core'
import { nextTick, onMounted, onUpdated, provide, ref, useTemplateRef, watch } from 'vue'

const props = defineProps<{
  tricolored: boolean
}>()

const container = useTemplateRef('container')
const { width } = useElementSize(container)
watch(width, () => nextTick(recolor))
onMounted(recolor)
onUpdated(recolor)

// Client found a situation where the colors were not updated. I have no idea why :-/
// (https://github.com/jacquev6/Gabby/issues/76)
// So, better safe than sorry, let's update the colors periodically.
setInterval(recolor, 1000)

const tricolorablesRevisionIndex = ref(0)
provide('tricolorablesRevisionIndex', tricolorablesRevisionIndex)

function recolor() {
  if (container.value !== null) {
    let somethingChanged = false

    const tricolorables = Array.from(
      container.value.getElementsByClassName('tricolorable') as HTMLCollectionOf<HTMLElement>,
    )

    if (props.tricolored) {
      type Line = { top: number; bottom: number; tricolorables: HTMLElement[] }
      const lines: Line[] = []

      tricolorables.forEach((element) => {
        const { top, bottom } = element.getBoundingClientRect()
        const line = lines.find(
          (line) => (line.top <= top && line.bottom >= bottom) || (line.top >= top && line.bottom <= bottom),
        )
        if (line) {
          line.top = Math.min(line.top, top)
          line.bottom = Math.max(line.bottom, bottom)
          line.tricolorables.push(element)
        } else {
          lines.push({ top, bottom, tricolorables: [element] })
        }
      })

      lines.sort((a, b) => a.top - b.top)

      lines.forEach((line, i) => {
        const color = colors[i % colors.length]
        line.tricolorables.forEach((element) => {
          if (element.style.color !== color) {
            somethingChanged = true
            element.style.color = color
          }
        })
      })
    } else {
      tricolorables.forEach((element) => {
        if (element.style.color !== '') {
          somethingChanged = true
          element.style.color = ''
        }
      })
    }

    if (somethingChanged) {
      tricolorablesRevisionIndex.value += 1
    }
  }
}

defineExpose({ recolor })
</script>

<template>
  <div ref="container"><slot></slot></div>
</template>

<style scoped>
:deep(.tricolorable .tricolorable) {
  background-color: red;
}

:deep(.tricolorable .tricolorable::after) {
  content: 'BUG (nested tricolorable)';
  color: white;
}
</style>
