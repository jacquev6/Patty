<script setup lang="ts">
import { useElementSize } from '@vueuse/core'
import { nextTick, onMounted, onUpdated, useTemplateRef, watch } from 'vue'

const container = useTemplateRef('container')
const { width } = useElementSize(container)
watch(width, () => nextTick(recolor))
onMounted(recolor)
onUpdated(recolor)

// Client found a situation where the colors were not updated. I have no idea why :-/
// (https://github.com/jacquev6/Gabby/issues/76)
// So, better safe than sorry, let's update the colors periodically.
setInterval(recolor, 1000)

/* Colors provided by client */
const colors = ['#00F', '#F00', '#0C0']

function recolor() {
  if (container.value !== null) {
    const tricolorables = Array.from(
      container.value.getElementsByClassName('tricolorable') as HTMLCollectionOf<HTMLElement>,
    )

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
        element.style.color = color
      })
    })
  }
}
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
